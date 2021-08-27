#include <stdio.h>
// For the CUDA runtime routines (prefixed with "cuda_")
#include <cuda_runtime.h>

#define NUM_STATES (1<<20)
#define NUM_COPYS  (1 << 10)
#define NUM_NOS 70

typedef unsigned int uint32_t;

using namespace std; 

__device__
bool state_comp(bool *s0, bool *s1){
   for(int i = 0; i < NUM_NOS; i++){
       if(s0[i] != s1[i]) return false;
   }
   return true;
}

__device__
void pass(bool *aux){
  
  bool vet[NUM_NOS];
  for(int i = 0; i < NUM_NOS; i++){
       vet[i] = aux[i];
  }
  aux[0] = vet[41];
  aux[1] = vet[21];
  aux[2] = vet[41] && ! vet[33] ;
  aux[3] = vet[36] && ! ( vet[37] || vet[7] ) ;
  aux[4] = ( ( vet[51] || vet[34] ) && vet[37] ) && ! vet[3] ;
  aux[5] = ! ( vet[21] && vet[1] ) ;
  aux[6] = ( vet[49] || vet[32] ) && ! ( vet[34] || vet[37] ) ;
  aux[7] = ( vet[8] || vet[9] ) && ! vet[22] ;
  aux[8] = vet[18] && ! ( vet[11] || vet[33] ) ;
  aux[9] = vet[14] && ! ( vet[22] || vet[33] ) ;
  aux[10] = vet[47] && ! vet[48] ;
  aux[11] = vet[32] ;
  aux[12] = vet[43] && vet[53] ;
  aux[13] = ( vet[5] || vet[49] || vet[27] ) && ! vet[21] ;
  aux[14] = vet[31] ;
  aux[15] = vet[35] ;
  aux[16] = vet[29] ;
  aux[17] = vet[65] ;
  aux[18] = vet[53] || vet[17] ;
  aux[19] = vet[16] ;
  aux[20] = vet[60] ;
  aux[21] = ! ( vet[15] || vet[3] ) ;
  aux[22] = ( vet[32] || vet[49] ) && ! vet[44] ;
  aux[23] = ! vet[24] ;
  aux[24] = ( vet[3] || ( vet[43] && vet[53] ) ) ;
  aux[25] = vet[20] && ! vet[50] ;
  aux[26] = vet[2] || vet[30] ;
  aux[27] = ( ( vet[5] || vet[16] ) && vet[26] ) && ! vet[21] ;
  aux[28] = ( vet[34] && vet[3] ) && ! ( vet[21] || vet[0] ) ;
  aux[29] = vet[39] || vet[41] ;
  aux[30] = vet[10] || vet[52] || vet[53] ;
  aux[31] = ( vet[4] || vet[51] || vet[10] ) && ! vet[6] ;
  aux[32] = ! vet[23] ;
  aux[33] = ( vet[34] || vet[45] ) && ! ( vet[21] || vet[7] ) ;
  aux[34] = ( vet[38] || vet[26] || vet[0] ) && ! vet[28] ;
  aux[35] = vet[12] ;
  aux[36] = ( vet[15] || vet[40] ) && ! vet[38] ;
  aux[37] = vet[10] && ! vet[3] ;
  aux[38] = vet[34] && ! ( vet[32] || vet[27] ) ;
  aux[39] = vet[10] || vet[40] ;
  aux[40] = vet[15] || vet[20] ;
  aux[41] = vet[53] && ! vet[42] ;
  aux[42] = vet[32] || vet[49] ;
  aux[43] = vet[48] ;
  aux[44] = vet[31] ;
  aux[45] = vet[52] && ! vet[27] ;
  aux[46] = vet[45] || vet[32] ;
  aux[47] = vet[34] || vet[18] ;
  aux[48] = vet[16] || vet[53] ;
  aux[49] = vet[25] ;
  aux[50] = vet[49] ;
  aux[51] = vet[8] && ! vet[6] ;
  aux[52] = vet[58] && ! vet[46] ;
  aux[53] = vet[55] ;
  aux[54] = ( vet[63] || vet[66] ) && ! vet[60] ;
  aux[55] = vet[59] ;
  aux[56] = vet[61] && ! ( vet[64] || vet[58] ) ;
  aux[57] = ( vet[62] || vet[64] ) && ! ( vet[63] || vet[58] || vet[61] ) ;
  aux[58] = vet[54] ;
  aux[59] = ( vet[64] || vet[67] ) && ! vet[63] ;
  aux[60] = vet[59] || vet[66] || vet[32] ;
  aux[61] = vet[66] || vet[56] ;
  aux[62] = vet[66] || vet[59] ;
  aux[63] = vet[54] || vet[56] ;
  aux[64] = vet[57] || vet[65] ;
  aux[65] = vet[64] && ! vet[58] ;
  aux[66] = ( vet[67] || vet[55] ) && ! vet[63] ;
  aux[67] = vet[32] ;
  aux[68] = ( vet[19] && vet[13] ) && ! ( vet[33] || vet[7] ) ;
  aux[69] = vet[7] ;

}

__global__
void findAttractor(bool *attractors, uint32_t * transients, uint32_t *periods, uint32_t numThreads){
   const int numNos = NUM_NOS;
   const int numState = NUM_STATES;
   const int numCopys = NUM_COPYS;
   unsigned int periodo, transient;
   bool S0[numNos];
   bool S1[numNos];
   uint32_t thread = blockDim.x * blockIdx.x + threadIdx.x;
   uint32_t step =  numState / numCopys; 
   uint32_t rest =  numState % numCopys;
   uint32_t begin = 0;
   uint32_t end = step - 1;
   bool flag = true;
   if(thread < numThreads){
       if(rest > 0){
           end = end + 1;
           rest = rest - 1;
       }else{
           flag = false;
       }
       
       for(uint32_t i = 0; i < numCopys;i++){
         if(i == thread) break;
         if(rest > 0){
           end = end + 1;
           begin = begin + 1;
           rest = rest - 1;
         }
         else if(rest == 0 && flag){
           begin = begin + 1;
           flag = 0;
         }
         begin += step;
         end += step;
       }
       //printf("Thread %d: begin:%d end: %d numStates: %d\n",thread,begin,end,end-begin+1);
       for(uint32_t  i = begin; i <= end; i++){
          int aux = i;
          for(int k = 0; k < numNos; k++){
              S0[k] = aux & 1 != 0;
              S1[k] = aux & 1 != 0;
	      aux >>= 1;
          }
          periodo = 0;
          transient = 0;
          do{
             pass(S0);
             pass(S1);
             pass(S1);
             transient++;
          }while (state_comp(S0,S1));
          do{
             pass(S0);
             periodo++;
          }while(state_comp(S0,S1));
          periodo--;
	  
          transients[i] = transient;
          periods[i]= periodo;
          for(int s = 0; s < numNos; s++){
            attractors[i*numNos + s] = S0[s];
	  }
       }
   }
}


int getIndice(int num_col, int i, int j)
{
    return (i*num_col)+ j;
}
/**
 * Host main routine
 */
int main(void)
{
    // Error code to check return values for CUDA calls
    cudaError_t err = cudaSuccess;

    // Print the vector length to be used, and compute its size
    size_t numNos = NUM_NOS;
    size_t numState = NUM_STATES;
    size_t size = numNos * numState * sizeof(bool);
    size_t size_transients = numState*sizeof(uint32_t);
    size_t size_periods = numState*sizeof(uint32_t);
    size_t totalBytes = size+size_transients+size_periods;
    size_t kb = totalBytes/(1024);
    size_t mb = kb/(1024);
    size_t gb = mb/(1024);
    printf("Find attractors net %lu nodes in %lu initials states.\n", numNos,numState);
    printf("Memory usage: %lu Gb or %lu Mb or %lu Kb.\n",gb,mb,kb);
    uint32_t *h_transients = (uint32_t*)malloc(size_transients);
    // Verify that allocations succeeded
    if (h_transients == NULL)
    {
        fprintf(stderr, "Failed to allocate h_transients!\n");
        exit(EXIT_FAILURE);
    }    
    uint32_t *h_periods = (uint32_t*)malloc(size_periods);
    // Verify that allocations succeeded
    if (h_periods == NULL)
    {
        fprintf(stderr, "Failed to allocate h_periods!\n");
        exit(EXIT_FAILURE);
    }
    // Allocate the host output vector C
    bool *h_attractors = (bool *)malloc(size);

    // Verify that allocations succeeded
    if (h_attractors == NULL)
    {
        fprintf(stderr, "Failed to allocate h_attractors!\n");
        exit(EXIT_FAILURE);
    }
    // Allocate the device vectors
    uint32_t *d_transients = NULL;
    err = cudaMalloc((void **)&d_transients, NUM_STATES*sizeof(uint32_t));

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to allocate d_transients (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    uint32_t *d_periods = NULL;
    err = cudaMalloc((void **)&d_periods, NUM_STATES*sizeof(uint32_t));

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to allocate d_periods (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    
    bool *d_attractors = NULL;
    err = cudaMalloc((void **)&d_attractors, size);

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to allocate d_attractors (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    // Launch the Vector Add CUDA Kernel
    uint32_t threadsPerBlock = 256;
    uint32_t blocksPerGrid =(NUM_COPYS + threadsPerBlock - 1) / threadsPerBlock;
    printf("CUDA kernel launch with %d blocks of %d threads\n", blocksPerGrid, threadsPerBlock);
    
    findAttractor<<<blocksPerGrid, threadsPerBlock>>>(d_attractors,d_transients,d_periods,NUM_COPYS);
    
    err = cudaGetLastError();
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to launch findAttractor kernel (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    // Copy the device result vector in device memory to the host result vector
    // in host memory.
    printf("Copy output data from the CUDA device to the host memory\n");
    err = cudaMemcpy(h_transients, d_transients,size_transients, cudaMemcpyDeviceToHost);
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to copy vector d_transients from device to host (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    
        err = cudaMemcpy(h_periods, d_periods, size_periods, cudaMemcpyDeviceToHost);
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to copy vector d_periods from device to host (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    err = cudaMemcpy(h_attractors, d_attractors, size, cudaMemcpyDeviceToHost);
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to copy vector d_attractors from device to host (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    /*
    printf("Attractor found:\n");
    for(int i = 0; i < numState; i++){
       for(int j = 0; j < numNos; j++){
          printf("%d",h_attractors[getIndice(numNos,i,j)]);
      }
      printf("\n");
    }
    printf("\n");
    */
    err = cudaFree(d_transients);

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to free device vector d_transients (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    err = cudaFree(d_periods);

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to free device vector d_periods (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    err = cudaFree(d_attractors);

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to free device vector d_attractors (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    // Free host memory
    free(h_transients);
    free(h_periods);
    free(h_attractors);

    // Reset the device and exit
    // cudaDeviceReset causes the driver to clean up all state. While
    // not mandatory in normal operation, it is good practice.  It is also
    // needed to ensure correct operation when the application is being
    // profiled. Calling cudaDeviceReset causes all profile data to be
    // flushed before the application exits
    err = cudaDeviceReset();

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to deinitialize the device! error=%s\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    printf("Done\n");
    return 0;
}





