#include <stdio.h>
#include <cuda_runtime.h>

typedef unsigned int uint32_t;

#define NUM_NOS (#NUM_NOS)

__device__
bool state_comp(bool *s0, bool *s1){
   bool r = true;
   for(int i = 0; i < NUM_NOS; i++){
       if(s0[i] != s1[i]) r = false;
   }
   return r;
}

__device__
void pass(bool *state){

  bool aux[NUM_NOS];
  for(int i = 0; i < NUM_NOS; i++){
       aux[i] = state[i];
  }
  #PASS
}

__global__
void findAttractor(bool *initial_states, bool *attractors, uint32_t * transients, uint32_t *periods, size_t num_threads){

   uint32_t period = 0;
   uint32_t transient = 0;

   bool S0[NUM_NOS];
   bool S1[NUM_NOS];

   uint32_t thread_id = blockDim.x * blockIdx.x + threadIdx.x;

   if(thread_id < num_threads){
        for(int k = 0; k < NUM_NOS; k++){
            S0[k] = initial_states[thread_id * NUM_NOS + k];
            S1[k] = S0[k];
        }
        do{
            pass(S0);
            pass(S1);
            pass(S1);
            transient++;
        }while (!state_comp(S0,S1));
        do{
            pass(S0);
            period++;
        }while(!state_comp(S0,S1));
        period--;
        transients[thread_id] = transient;
        periods[thread_id]= period;
        for(int s = 0; s < NUM_NOS; s++){
            attractors[thread_id*NUM_NOS + s] = S0[s];
        }
   }
}
