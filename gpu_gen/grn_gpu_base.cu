#include <stdio.h>
// For the CUDA runtime routines (prefixed with "cuda_")
#include <cuda_runtime.h>

#define NUM_STATES (1<<20)
#define NUM_COPYS  (1 << 10)
#define NUM_NOS 70

typedef unsigned int uint32_t;

using namespace std; 

__device__
bool state_comp(bool *s0, bool *s1, int size){
   for(int i = 0; i < size; i++){
       if(s0[i] != s1[i])return false;
   }
   return true;
}

__device__
void pass(bool *State){
  
  bool currentState [NUM_NOS];
  for(int i = 0; i < NUM_NOS; i++){
       currentState[i] = State[i];
  }
  State[0] = currentState[41];
  State[1] = currentState[21];
  State[2] = currentState[41] && ! currentState[33] ;
  State[3] = currentState[36] && ! ( currentState[37] || currentState[7] ) ;
  State[4] = ( ( currentState[51] || currentState[34] ) && currentState[37] ) && ! currentState[3] ;
  State[5] = ! ( currentState[21] && currentState[1] ) ;
  State[6] = ( currentState[49] || currentState[32] ) && ! ( currentState[34] || currentState[37] ) ;
  State[7] = ( currentState[8] || currentState[9] ) && ! currentState[22] ;
  State[8] = currentState[18] && ! ( currentState[11] || currentState[33] ) ;
  State[9] = currentState[14] && ! ( currentState[22] || currentState[33] ) ;
  State[10] = currentState[47] && ! currentState[48] ;
  State[11] = currentState[32] ;
  State[12] = currentState[43] && currentState[53] ;
  State[13] = ( currentState[5] || currentState[49] || currentState[27] ) && ! currentState[21] ;
  State[14] = currentState[31] ;
  State[15] = currentState[35] ;
  State[16] = currentState[29] ;
  State[17] = currentState[65] ;
  State[18] = currentState[53] || currentState[17] ;
  State[19] = currentState[16] ;
  State[20] = currentState[60] ;
  State[21] = ! ( currentState[15] || currentState[3] ) ;
  State[22] = ( currentState[32] || currentState[49] ) && ! currentState[44] ;
  State[23] = ! currentState[24] ;
  State[24] = ( currentState[3] || ( currentState[43] && currentState[53] ) ) ;
  State[25] = currentState[20] && ! currentState[50] ;
  State[26] = currentState[2] || currentState[30] ;
  State[27] = ( ( currentState[5] || currentState[16] ) && currentState[26] ) && ! currentState[21] ;
  State[28] = ( currentState[34] && currentState[3] ) && ! ( currentState[21] || currentState[0] ) ;
  State[29] = currentState[39] || currentState[41] ;
  State[30] = currentState[10] || currentState[52] || currentState[53] ;
  State[31] = ( currentState[4] || currentState[51] || currentState[10] ) && ! currentState[6] ;
  State[32] = ! currentState[23] ;
  State[33] = ( currentState[34] || currentState[45] ) && ! ( currentState[21] || currentState[7] ) ;
  State[34] = ( currentState[38] || currentState[26] || currentState[0] ) && ! currentState[28] ;
  State[35] = currentState[12] ;
  State[36] = ( currentState[15] || currentState[40] ) && ! currentState[38] ;
  State[37] = currentState[10] && ! currentState[3] ;
  State[38] = currentState[34] && ! ( currentState[32] || currentState[27] ) ;
  State[39] = currentState[10] || currentState[40] ;
  State[40] = currentState[15] || currentState[20] ;
  State[41] = currentState[53] && ! currentState[42] ;
  State[42] = currentState[32] || currentState[49] ;
  State[43] = currentState[48] ;
  State[44] = currentState[31] ;
  State[45] = currentState[52] && ! currentState[27] ;
  State[46] = currentState[45] || currentState[32] ;
  State[47] = currentState[34] || currentState[18] ;
  State[48] = currentState[16] || currentState[53] ;
  State[49] = currentState[25] ;
  State[50] = currentState[49] ;
  State[51] = currentState[8] && ! currentState[6] ;
  State[52] = currentState[58] && ! currentState[46] ;
  State[53] = currentState[55] ;
  State[54] = ( currentState[63] || currentState[66] ) && ! currentState[60] ;
  State[55] = currentState[59] ;
  State[56] = currentState[61] && ! ( currentState[64] || currentState[58] ) ;
  State[57] = ( currentState[62] || currentState[64] ) && ! ( currentState[63] || currentState[58] || currentState[61] ) ;
  State[58] = currentState[54] ;
  State[59] = ( currentState[64] || currentState[67] ) && ! currentState[63] ;
  State[60] = currentState[59] || currentState[66] || currentState[32] ;
  State[61] = currentState[66] || currentState[56] ;
  State[62] = currentState[66] || currentState[59] ;
  State[63] = currentState[54] || currentState[56] ;
  State[64] = currentState[57] || currentState[65] ;
  State[65] = currentState[64] && ! currentState[58] ;
  State[66] = ( currentState[67] || currentState[55] ) && ! currentState[63] ;
  State[67] = currentState[32] ;
  State[68] = ( currentState[19] && currentState[13] ) && ! ( currentState[33] || currentState[7] ) ;
  State[69] = currentState[7] ;

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
          }while (state_comp(S0,S1,numNos));
          do{
             pass(S0);
             periodo++;
          }while(state_comp(S0,S1,numNos));
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





