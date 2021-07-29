#include <iostream>
#include <math.h>
#include <omp.h>
#include <chrono>

#define NUM_NODES 5
#define NUM_STATES 21

using namespace std;
using namespace std::chrono;

void pass(bool *aux);
bool equals(bool *vet1, bool *vet2, int size);
void initialState(unsigned long int valor, bool *vet1, bool *vet2, int size);
string boolArraytoString(bool *vet, int size);
unsigned long long int boolArraytoInt(bool *vet, int size);
void runGNR(int inicio, int fim, unsigned int * period_vet, unsigned int * transient_vet);

int main() {
    unsigned int *period_vet = nullptr;
    unsigned int *transient_vet = nullptr;
    period_vet = (unsigned int *)malloc(sizeof(unsigned int)*NUM_STATES);
    transient_vet = (unsigned int *)malloc(sizeof(unsigned int)*NUM_STATES);
    if(period_vet == nullptr || transient_vet == nullptr){
        cout << "Error: malloc failed!" << endl;
        exit(255);
    }
    high_resolution_clock::time_point s;
    duration<double> diff{};
    s = high_resolution_clock::now();
    runGNR(0,NUM_STATES,period_vet,transient_vet);
    diff = high_resolution_clock::now() - s;
    cout << "Number of state: " << NUM_STATES << endl;
    cout << "Execution Time: " << diff.count() * 1000 << "ms" << endl;
    cout << "State per second: " << (NUM_STATES/diff.count()) << endl;
    free(period_vet);
    free(transient_vet);   
    return 0;
}

void runGNR(int inicio, int fim, unsigned int * period_vet, unsigned int * transient_vet) {
    bool s0[NUM_NODES];
    bool s1[NUM_NODES];
    unsigned int period = 0;
    unsigned int transient = 0;
    #pragma omp parallel for schedule(static) private(s0,s1,period,transient)
    for (unsigned long long int i = inicio; i < fim; i++) {
        initialState(i, s0, s1, NUM_NODES);
        do {
            pass(s0);
            pass(s1);
            pass(s1);
            transient++;
        } while (!equals(s0, s1, NUM_NODES));
        do {
            pass(s1);
            period++;
        } while (!equals(s0, s1, NUM_NODES));
        period--;
        period_vet[i] = period;
        transient_vet[i] = transient;
        printf("%lld: P: %u T: %u\n",i,period,transient);
        period = 0;
        transient = 0;
    }
}

void initialState(unsigned long int valor, bool *vet1, bool *vet2, int size) {
    for (int i = 0; i < size; i++) {
        vet1[i] = (valor & 1) != 0;
        vet2[i] = vet1[i];
        valor >>= 1;
    }
}

bool equals(bool *vet1, bool *vet2, int size) {
    for (int i = 0; i < size; i++) {
        if (vet1[i] != vet2[i]) {
            return false;
        }
    }
    return true;
}

string boolArraytoString(bool *vet, int size) {
    string out;
    for (int i = size - 1; i >= 0; i--) {
        if (vet[i]) {
            out = out + "1";
        } else {
            out = out + "0";
        }
    }
    return out;
}

unsigned long long int boolArraytoInt(bool *vet, int size) {
    int out = 0;
    for (int i = size - 1; i >= 0; i--) {
        if (vet[i]) {
            out |= 1;
        }
        if (i > 0) out <<= 1;
    }
    return out;
}

void pass(bool *aux){
    bool vet[NUM_NODES];
    for (int i=0; i<NUM_NODES; i++){
        vet[i]=aux[i];
    }

    aux[1]  =   ( vet[1] ||vet[3] )  && ( !vet[0] )  && ( !vet[4] )  ;
    aux[3]  =  vet[2] &&!vet[1] ;
    aux[4]  =  vet[1] &&!vet[2] ;
    aux[2]  =  vet[1] &&vet[0] && ( !vet[3] )  && ( !vet[2] )  ;
    aux[0]  =  vet[1] && ( !vet[0] )  && ( !vet[4]  )  ;
    
}
