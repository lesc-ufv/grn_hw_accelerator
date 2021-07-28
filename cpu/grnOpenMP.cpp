#include <iostream>
#include <math.h>
#include <omp.h>
#include <chrono>

#define NUM_STATES (1<<5)
#define NUM_NOS 21

using namespace std;
using namespace std::chrono;

void pass(bool *aux);
bool equals(bool *vet1, bool *vet2, int size);
void print(bool *vet1);
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
    bool s0[NUM_NOS];
    bool s1[NUM_NOS];
    unsigned int period = 0;
    unsigned int transient = 0;
    #pragma omp parallel for schedule(static) private(s0,s1,period,transient)
    for (unsigned long long int i = inicio; i < fim; i++) {
        initialState(i, s0, s1, NUM_NOS);
        do {
            pass(s0);
            pass(s1);
            pass(s1);
            transient++;
        } while (!equals(s0, s1, NUM_NOS));
        do {
            pass(s1);
            period++;
        } while (!equals(s0, s1, NUM_NOS));
        
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
    // std::cout <<"boolArraytoInt:"<< std::endl;
    for (int i = size - 1; i >= 0; i--) {
        //   std::cout << vet[i] << " ";
        if (vet[i]) {
            out |= 1;
        }
        if (i > 0) out <<= 1;
    }
    //  std::cout << " = " << out << std::endl;
    return out;
}
// Equações Biológicas
// CAC Network ( 70 Vértices )
#if NUM_NOS == 70
void pass (bool *aux){
 
    bool vet[NUM_NOS];
    for (int i=0; i<NUM_NOS; i++){
        vet[i] = aux[i];
    }
    aux[0] = vet[41] ;
    aux[1] = vet[21] ;
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
    aux[35] = vet[12];
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
#elif NUM_NOS == 21
// CAC network Reduzida (21 Vértices)
void pass (bool *aux){
    bool vet[NUM_NOS];
    for (int i=0; i<NUM_NOS; i++){
        vet[i]= aux[i];
    }
    aux[0] = ! vet[16] ;
    aux[1] = ! ( vet[15] && vet[4] ) ;
    aux[2] = vet[5] && ! vet[7] ;
    aux[3] = ( vet[1] || vet[18] || vet[10] ) && ! vet[4] ;
    aux[4] = ! ( vet[19] || vet[0] ) ;
    aux[5] = vet[2] ;
    aux[6] = vet[0] || vet[19] ;
    aux[7] = ! vet[5] ;
    aux[8] = ! vet[17] ;
    aux[9] = vet[19] ;
    aux[10] = vet[9] && ! vet[4] ;
    aux[11] = ( vet[5] || vet[13] ) && ! vet[7] ;
    aux[12] = ( vet[15] && vet[0] ) && ! vet[4] ;
    aux[13] = vet[6] ;
    aux[14] = vet[15] && ! vet[4] ;
    aux[15] = ( vet[16] || vet[9] ) && ! vet[12] ;
    aux[16] = vet[15] && ! ( vet[13] || vet[10] ) ;
    aux[17] = vet[18] ;
    aux[18] = vet[8] ;
    aux[19] = vet[11] ;
    aux[20] = vet[3] && ! vet[14] ;
}
#elif NUM_NOS == 54
 // MAPK ( 54 Vértices)
void pass(bool *aux){
    bool vet[NUM_NOS];
 for (int i=0; i<NUM_NOS; i++){
     vet[i] = aux[i];
 }
    aux[0] = vet[37] ;
    aux[1] = vet[37] && ! vet[43] ;
    aux[2] = vet[24] && ( vet[16] || vet[4] ) ;
    aux[3] = ! vet[6] && ! vet[13] && vet[17] && vet[35] ;
     aux[4] = vet[23] || vet[34] ;
     aux[5] = vet[8] ;
     aux[6] = vet[7] && vet[1] ;
     aux[7] = vet[29] ;
     aux[8] = vet[0] ;
     aux[9] = vet[7] ;
     aux[10] = ( vet[11] || vet[49] ) && ! ( vet[39] || vet[21] ) ;
     aux[11] = vet[0] ;
     aux[12] = vet[13] || vet[23] || vet[34] ;
     aux[13] = vet[28] ;
     aux[14] = vet[15] && ! ( vet[21] || vet[39] ) ;
     aux[15] = vet[0] ;
     aux[16] = vet[13] && vet[46] && ( vet[12] || vet[7] ) ;
     aux[17] = vet[23] && ! vet[1] ;
     aux[18] = vet[14] && ! vet[49] && ! vet[21] ;
     aux[19] = vet[21] || vet[38] ;
     aux[20] = vet[47] || vet[35] ;
     aux[21] = vet[10] || vet[18] || vet[52] ;
     aux[22] = vet[33] ;
     aux[23] = ( vet[51] && vet[25] ) || ( vet[25] && vet[30] ) || ( vet[51] && vet[30] ) || ( vet[50] && vet[30] ) |( vet[50] && vet[25] ) || ( vet[50] && vet[51] ) || (( vet[51] || vet[30] || vet[25] || vet[50] ) && ! vet[9] ) ;
     aux[24] = vet[23] ;
     aux[25] = vet[45] ;
     aux[26] = vet[34] ;
     aux[27] = ( vet[35] || vet[1] ) && ! vet[32] ;
     aux[28] = ( vet[44] || vet[25] ) && ! ( vet[41] || vet[2] ) ;
     aux[29] = vet[13] || vet[34] ;
     aux[30] = vet[20] ;
     aux[31] = ( vet[29] && vet[26] ) || ( vet[29] && vet[1] ) ;
     aux[32] = vet[31] ;
     aux[33] = ! vet[1] && vet[35] ;
     aux[34] = ( vet[51] && vet[25] ) || ( vet[25] && vet[30] ) || ( vet[51] && vet[30] ) || ( vet[50] && vet[30] ) |( vet[50] && vet[25] ) || ( vet[50] && vet[51] ) || (( vet[51] || vet[30] || vet[25] || vet[50] ) && ! vet[9] ) ;
     aux[35] = ( vet[5] && vet[34] ) || (( vet[5] || vet[34] ) && ! vet[27] ) ;
     aux[36] = vet[37] && vet[13] ;
     aux[37] = vet[38] ;
     aux[38] = vet[19] || ( vet[45] && vet[48] ) ;
     aux[39] = vet[40] ;
     aux[40] = vet[10] || vet[14] ;
     aux[41] = vet[34] ;
     aux[42] = vet[36] && vet[31] && ! vet[33] ;
     aux[43] = vet[35] ;
     aux[44] = ( vet[45] || vet[39] ) && ! ( vet[13] || vet[1] ) ;
     aux[45] = vet[48] || vet[40] ;
     aux[46] = vet[13] ;
     aux[47] = vet[52] ;
     aux[48] = vet[21] && ! vet[46] ;
     aux[49] = vet[13] ;
     aux[50] = vet[52] ;
     aux[51] = vet[5] ;
     aux[52] = vet[53] ;
     aux[53] = vet[0] ;
}

#elif NUM_NOS == 188

void pass(bool *aux){
    bool vet[NUM_NOS];
    for (int i=0; i<NUM_NOS; i++){
        vet[i]=aux[i];
    }
    aux[0] = ( vet[48] )  ;
    aux[1] = ( vet[17] ) || ( vet[125] && ( ( ( vet[42] ) ) ) ) || ( vet[100] )  ;
    aux[2] = ( vet[82] && ( ( ( vet[126] ) ) ) )  ;
    aux[3] = ( vet[132] && ( ( ( vet[121] ) ) ) )  ;
    aux[4] = ( vet[148] ) || ( vet[7] )  ;
    aux[5] = ( vet[22] ) || ( vet[23] )  ;
    aux[6] = ( vet[1] )  ;
    aux[7] = ( vet[149] ) || ( vet[18] ) || ( vet[54] )  ;
    aux[8] = ( vet[16] )  ;
    aux[9] = ( vet[3] ) || ( vet[163] )  ;
    aux[10] = ( vet[113] && ( ( ( vet[156] && vet[134] ) ) ) )  ;
    aux[11] = ( vet[113] ) || ( vet[93] )  ;
    aux[12] = ( vet[172] )  ;
    aux[13] = ( vet[54] )  ;
    aux[14] = ( vet[137] )  ;
    aux[15] = ( vet[40] )  ;
    aux[16] = ( vet[5] ) || ( vet[48] )  ;
    aux[17] = ( vet[91] )  ;
    aux[18] = ( vet[80] )  ;
    aux[19] = ( vet[178] )  ;
    aux[20] = ( vet[185] ) || ( vet[113] )  ;
    aux[21] = ( vet[20] )  ;
    aux[22] = ( vet[154] )  ;
    aux[23] = ( vet[21] && ( ( ( vet[66] ) ) ) )  ;
    aux[24] = ( ( vet[114] ) && ! ( vet[117] ) ) || ( ( vet[81] ) && ! ( vet[117] ) ) || ( ( vet[49] ) && ! ( vet[117] ) )  ;
    aux[25] = ( vet[63] ) || ( vet[96] ) || ( vet[123] )  ;
    aux[26] = ( vet[80] )  ;
    aux[27] = ( vet[171] && ( ( ( vet[162] && vet[176] ) ) ) )  ;
    aux[28] = ( vet[130] )  ;
    aux[29] = ( vet[47] && ( ( ( vet[14] ) ) ) )  ;
    aux[30] = ( ! ( ( vet[38] ) || ( vet[52] ) ) ) || ! ( vet[52] || vet[38] )  ;
    aux[31] = ( ! ( ( vet[103] ) ) ) || ! ( vet[103] )  ;
    aux[32] = ( vet[76] && ( ( ( vet[108] ) ) ) )  ;
    aux[33] = ( vet[87] ) || ( vet[166] )  ;
    aux[34] = ( vet[138] && ( ( ( vet[130] && vet[118] ) ) ) )  ;
    aux[35] = ( vet[186] )  ;
    aux[36] = ( vet[131] ) || ( vet[45] ) || ( vet[46] ) || ( vet[90] ) || ( vet[89] ) || ( vet[129] )  ;
    aux[37] = ( vet[69] )  ;
    aux[38] = ( ! ( ( vet[78] ) ) ) || ! ( vet[78] )  ;
    aux[39] = ( vet[153] )  ;
    aux[40] = ( vet[120] ) || ( vet[95] )  ;
    aux[41] = ( vet[184] ) || ( vet[43] )  ;
    aux[42] = ( vet[146] ) || ( vet[57] )  ;
    aux[43] = ( vet[131] )  ;
    aux[44] = ( vet[51] ) || ( vet[24] ) || ( vet[36] ) || ( vet[130] )  ;
    aux[45] = ( vet[116] && ( ( ( vet[77] && vet[177] ) ) ) ) || ( vet[164] && ( ( ( vet[77] && vet[177] ) ) ) )  ;
    aux[46] = ( vet[177] && ( ( ( vet[167] && vet[163] && vet[159] ) ) ) )  ;
    aux[47] = ( vet[59] ) || ( vet[60] )  ;
    aux[48] = ( vet[66] ) || ( vet[179] ) || ( vet[20] )  ;
    aux[49] = ( vet[171] && ( ( ( vet[174] && vet[175] ) ) ) )  ;
    aux[50] = ( vet[33] )  ;
    aux[51] = ( ( vet[40] && ( ( ( vet[2] ) ) ) ) && ! ( vet[69] ) ) || ( ( vet[136] ) && ! ( vet[69] ) )  ;
    aux[52] = ( ( ( vet[50] && ( ( ( vet[36] && vet[138] ) ) ) ) && ! ( vet[130] && ( ( ( vet[147] ) ) ) ) ) && ! ( vet[24] ) ) || ( vet[138] && ( ( ( vet[52] && vet[36] ) ) ) )  ;
    aux[53] = ( ( ( vet[138] && ( ( ( ! vet[52] ) ) ) ) && ! ( vet[153] && ( ( ( vet[30] ) ) ) ) ) && ! ( vet[36] && ( ( ( vet[93] ) ) ) ) ) || ( ( ( vet[30] ) && ! ( vet[153] && ( ( ( vet[30] ) ) ) ) ) && ! ( vet[36] && ( ( ( vet[93] ) ) ) ) )  ;
    aux[54] = ( vet[149] )  ;
    aux[55] = ( vet[74] )  ;
    aux[56] = ( vet[48] )  ;
    aux[57] = ( vet[23] )  ;
    aux[58] = ( vet[32] )  ;
    aux[59] = ( vet[151] ) || ( vet[99] && ( ( ( vet[26] ) ) ) )  ;
    aux[60] = ( vet[112] && ( ( ( vet[110] ) ) ) )  ;
    aux[61] = ( vet[79] )  ;
    aux[62] = ( vet[52] && ( ( ( vet[138] ) ) ) ) || ( vet[36] && ( ( ( vet[138] ) ) ) ) || ( vet[50] && ( ( ( vet[138] ) ) ) ) || ( vet[30] && ( ( ( vet[138] ) ) ) )  ;
    aux[63] = ( vet[83] )  ;
    aux[64] = ( vet[51] ) || ( vet[85] ) || ( vet[71] )  ;
    aux[65] = ( vet[69] )  ;
    aux[66] = ( vet[20] ) || ( vet[21] )  ;
    aux[67] = ( vet[170] )  ;
    aux[68] = ( vet[88] )  ;
    aux[69] = ( vet[65] ) || ( ( vet[93] ) && ! ( vet[153] ) )  ;
    aux[70] = ( ! ( ( vet[102] ) ) ) || ! ( vet[102] )  ;
    aux[71] = ( vet[25] )  ;
    aux[72] = ( ( ( ( vet[138] && ( ( ( vet[130] && vet[30] && vet[118] && vet[147] ) ) ) ) && ! ( vet[24] && ( ( ( vet[52] ) ) ) ) ) && ! ( vet[93] && ( ( ( vet[52] ) ) ) ) ) && ! ( vet[36] && ( ( ( vet[52] ) ) ) ) )  ;
    aux[73] = ( ( vet[153] ) && ! ( vet[69] ) )  ;
    aux[74] = ( vet[140] )  ;
    aux[75] = ( vet[89] )  ;
    aux[76] = ( vet[157] && ( ( ( vet[113] ) ) ) )  ;
    aux[77] = ( ! ( ( vet[79] ) ) ) || ! ( vet[79] )  ;
    aux[78] = ( vet[150] ) || ( vet[92] ) || ( vet[113] )  ;
    aux[79] = ( vet[145] ) || ( vet[94] )  ;
    aux[80] = ( vet[149] ) || ( vet[13] )  ;
    aux[81] = ( vet[127] && ( ( ( vet[160] && vet[168] ) ) ) ) || ( vet[181] && ( ( ( vet[160] && vet[168] ) ) ) )  ;
    aux[82] = ( vet[101] ) || ( vet[157] )  ;
    aux[83] = ( vet[115] ) || ( vet[143] )  ;
    aux[84] = ( vet[180] ) || ( vet[182] )  ;
    aux[85] = ( vet[110] && ( ( ( vet[42] ) ) ) ) || ( vet[58] ) || ( vet[98] )  ;
    aux[86] = ( vet[152] && ( ( ( vet[82] && vet[171] && vet[130] && vet[147] ) ) ) ) || ( vet[158] && ( ( ( vet[82] && vet[171] && vet[130] && vet[147] ) ) ) )  ;
    aux[87] = ( vet[52] && ( ( ( vet[118] && vet[138] ) ) ) )  ;
    aux[88] = ( vet[84] && ( ( ( vet[139] ) ) ) ) || ( vet[131] ) || ( vet[9] ) || ( vet[3] ) || ( vet[83] ) || ( vet[23] )  ;
    aux[89] = ( vet[84] ) || ( vet[43] && ( ( ( vet[163] ) ) ) ) || ( vet[10] )  ;
    aux[90] = ( vet[131] )  ;
    aux[91] = ( vet[141] )  ;
    aux[92] = ( vet[74] )  ;
    aux[93] = ( vet[45] )  ;
    aux[94] = ( vet[53] && ( ( ( vet[62] && vet[177] && vet[163] ) ) ) ) || ( vet[169] && ( ( ( vet[62] && vet[177] && vet[163] ) ) ) )  ;
    aux[95] = ( vet[32] )  ;
    aux[96] = ( vet[1] )  ;
    aux[97] = ( vet[8] )  ;
    aux[98] = ( vet[55] )  ;
    aux[99] = ( vet[80] )  ;
    aux[100] = ( vet[91] )  ;
    aux[101] = ( vet[24] )  ;
    aux[102] = ( vet[123] ) || ( vet[8] )  ;
    aux[103] = ( vet[133] )  ;
    aux[104] = ( vet[56] ) || ( vet[119] )  ;
    aux[105] = ( vet[111] )  ;
    aux[106] = ( vet[134] && ( ( ( vet[113] ) ) ) ) || ( vet[48] )  ;
    aux[107] = ( vet[104] )  ;
    aux[108] = ( vet[134] ) || ( vet[157] )  ;
    aux[109] = ( vet[183] )  ;
    aux[110] = ( vet[142] ) || ( vet[0] ) || ( vet[42] && ( ( ( vet[57] ) ) ) ) || ( vet[26] )  ;
    aux[111] = ( vet[7] )  ;
    aux[112] = ( vet[110] )  ;
    aux[113] = ( vet[180] && ( ( ( vet[84] ) ) ) )  ;
    aux[114] = ( vet[155] )  ;
    aux[115] = ( vet[121] )  ;
    aux[116] = ( vet[37] ) || ( ( ( ( vet[69] && ( ( ( vet[118] && vet[138] ) ) ) ) && ! ( vet[52] ) ) && ! ( vet[153] && ( ( ( vet[73] ) ) ) ) ) && ! ( vet[101] ) )  ;
    aux[117] = ( vet[93] ) || ( vet[130] )  ;
    aux[118] = ( vet[118] ) || ( vet[79] )  ;
    aux[119] = ( vet[4] )  ;
    aux[120] = ( vet[32] )  ;
    aux[121] = ( vet[54] ) || ( vet[132] )  ;
    aux[122] = ( vet[105] )  ;
    aux[123] = ( vet[110] ) || ( vet[151] ) || ( vet[99] )  ;
    aux[124] = ( vet[138] && ( ( ( vet[69] || vet[130] ) && ( ( ( vet[118] ) ) ) ) ) )  ;
    aux[125] = ( vet[42] )  ;
    aux[126] = ( vet[157] )  ;
    aux[127] = ( ( ( vet[51] && ( ( ( vet[118] && vet[138] ) ) ) ) && ! ( vet[52] ) ) && ! ( vet[130] ) ) || ( ( ( vet[15] ) && ! ( vet[52] ) ) && ! ( vet[130] ) ) || ( ( ( vet[64] && ( ( ( vet[51] ) ) ) ) && ! ( vet[52] ) ) && ! ( vet[130] ) ) || ( ( ( vet[73] && ( ( ( vet[153] && vet[118] && vet[138] ) ) ) ) && ! ( vet[52] ) ) && ! ( vet[130] ) ) || ( ( ( vet[39] ) && ! ( vet[52] ) ) && ! ( vet[130] ) )  ;
    aux[128] = ( vet[51] )  ;
    aux[129] = ( ( vet[43] ) && ! ( vet[28] ) ) || ( ( vet[131] ) && ! ( vet[28] ) ) || ( ( vet[41] ) && ! ( vet[28] ) ) || ( ( vet[35] ) && ! ( vet[28] ) )  ;
    aux[130] = ( vet[135] ) || ( vet[49] ) || ( vet[27] ) || ( vet[86] ) || ( vet[144] )  ;
    aux[131] = ( vet[53] && ( ( ( vet[177] && vet[163] ) && ( ( ( ! vet[62] ) ) ) ) ) ) || ( vet[169] && ( ( ( vet[177] && vet[163] ) && ( ( ( ! vet[62] ) ) ) ) ) )  ;
    aux[132] = ( vet[106] ) || ( vet[163] && ( ( ( vet[131] ) ) ) )  ;
    aux[133] = ( vet[68] )  ;
    aux[134] = ( vet[113] )  ;
    aux[135] = ( vet[161] && ( ( ( vet[171] && vet[177] ) ) ) ) || ( vet[34] && ( ( ( vet[171] && vet[177] ) ) ) )  ;
    aux[136] = ( vet[82] && ( ( ( vet[126] ) ) ) )  ;
    aux[137] = ( vet[6] )  ;
    aux[138] = ( vet[84] && ( ( ( vet[113] ) ) ) ) || ( vet[113] && ( ( ( vet[84] ) ) ) ) || ( ( vet[122] && ( ( ( vet[40] ) ) ) ) && ! ( vet[31] ) )  ;
    aux[139] = ( vet[180] )  ;
    aux[140] = ( vet[109] )  ;
    aux[141] = ( vet[12] )  ;
    aux[142] = ( vet[66] )  ;
    aux[143] = ( vet[4] )  ;
    aux[144] = ( vet[124] && ( ( ( vet[173] && vet[187] ) ) ) ) || ( vet[165] && ( ( ( vet[173] && vet[187] ) ) ) )  ;
    aux[145] = ( vet[116] && ( ( ( vet[177] && vet[61] ) ) ) ) || ( vet[164] && ( ( ( vet[177] && vet[61] ) ) ) )  ;
    aux[146] = ( vet[23] && ( ( ( vet[20] ) ) ) )  ;
    aux[147] = ( vet[33] && ( ( ( vet[130] ) ) ) ) || ( vet[147] && ( ( ( vet[33] || vet[130] ) ) ) )  ;
    aux[148] = ( vet[19] )  ;
    aux[149] = ( vet[75] && ( ( ( vet[134] ) ) ) )  ;
    aux[150] = ( vet[107] && ( ( ( vet[104] ) ) ) )  ;
    aux[151] = ( vet[125] ) || ( vet[5] )  ;
    aux[152] = ( vet[138] && ( ( ( vet[130] && vet[118] ) ) ) )  ;
    aux[153] = ( ( vet[153] ) && ! ( vet[69] ) ) || ( ( vet[24] ) && ! ( vet[69] ) )  ;
    aux[154] = vet[154]  ;
    aux[155] = vet[155]  ;
    aux[156] = vet[156]  ;
    aux[157] = vet[157]  ;
    aux[158] = vet[158]  ;
    aux[159] = vet[159]  ;
    aux[160] = vet[160]  ;
    aux[161] = vet[161]  ;
    aux[162] = vet[162]  ;
    aux[163] = vet[163]  ;
    aux[164] = vet[164]  ;
    aux[165] = vet[165]  ;
    aux[166] = vet[166]  ;
    aux[167] = vet[167]  ;
    aux[168] = vet[168]  ;
    aux[169] = vet[169]  ;
    aux[170] = vet[170]  ;
    aux[171] = vet[171]  ;
    aux[172] = vet[172]  ;
    aux[173] = vet[173]  ;
    aux[174] = vet[174]  ;
    aux[175] = vet[175]  ;
    aux[176] = vet[176]  ;
    aux[177] = vet[177]  ;
    aux[178] = vet[178]  ;
    aux[179] = vet[179]  ;
    aux[180] = vet[180]  ;
    aux[181] = vet[181]  ;
    aux[182] = vet[182]  ;

    aux[183] = vet[183]  ;

    aux[184] = vet[184]  ;

    aux[185] = vet[185]  ;

    aux[186] = vet[186]  ;

    aux[187] = vet[187] ;

}
#else
 /*Error*/
#endif
