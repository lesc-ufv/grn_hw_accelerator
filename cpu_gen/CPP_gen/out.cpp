#include <iostream>
#include <math.h>
#include <omp.h>
#include <chrono>

#define NUM_NODES 188
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

    aux[137]  =   (  vet[19]  )   ;
     aux[152]  =   (  vet[31]  )  || (  vet[12] && (   (   (  vet[27]  )   )   )   )  || (  vet[144]  )   ;
     aux[183]  =   (  vet[73] && (   (   (  vet[74]  )   )   )   )   ;
     aux[40]  =   (  vet[161] && (   (   (  vet[54]  )   )   )   )   ;
     aux[28]  =   (  vet[146]  )  || (  vet[147]  )   ;
     aux[156]  =   (  vet[44]  )  || (  vet[35]  )   ;
     aux[157]  =   (  vet[152]  )   ;
     aux[147]  =   (  vet[187]  )  || (  vet[116]  )  || (  vet[121]  )   ;
     aux[158]  =   (  vet[155]  )   ;
     aux[162]  =   (  vet[40]  )  || (  vet[98]  )   ;
     aux[23]  =   (  vet[178] && (   (   (  vet[129] &&vet[22]  )   )   )   )   ;
     aux[52]  =   (  vet[178]  )  || (  vet[174]  )   ;
     aux[50]  =   (  vet[49]  )   ;
     aux[43]  =   (  vet[121]  )   ;
     aux[39]  =   (  vet[148]  )   ;
     aux[6]  =   (  vet[138]  )   ;
     aux[155]  =   (  vet[156]  )  || (  vet[19]  )   ;
     aux[31]  =   (  vet[15]  )   ;
     aux[116]  =   (  vet[163]  )   ;
     aux[47]  =   (  vet[48]  )   ;
     aux[10]  =   (  vet[30]  )  || (  vet[178]  )   ;
     aux[36]  =   (  vet[10]  )   ;
     aux[44]  =   (  vet[2]  )   ;
     aux[35]  =   (  vet[36] && (   (   (  vet[168]  )   )   )   )   ;
     aux[169]  =   (   (  vet[59]  )  &&! (  vet[165]  )   )  || (   (  vet[62]  )  &&! (  vet[165]  )   )  || (   (  vet[92]  )  &&! (  vet[165]  )   )   ;
     aux[124]  =   (  vet[151]  )  || (  vet[11]  )  || (  vet[139]  )   ;
     aux[184]  =   (  vet[163]  )   ;
     aux[106]  =   (  vet[53] && (   (   (  vet[105] &&vet[107]  )   )   )   )   ;
     aux[166]  =   (  vet[170]  )   ;
     aux[34]  =   (  vet[5] && (   (   (  vet[39]  )   )   )   )   ;
     aux[135]  =   (  ! (   (  vet[65]  )  || (  vet[37]  )   )   )  ||! (  vet[37] ||vet[65]  )   ;
     aux[55]  =   (  ! (   (  vet[1]  )   )   )  ||! (  vet[1]  )   ;
     aux[128]  =   (  vet[41] && (   (   (  vet[42]  )   )   )   )   ;
     aux[181]  =   (  vet[179]  )  || (  vet[180]  )   ;
     aux[82]  =   (  vet[134] && (   (   (  vet[170] &&vet[149]  )   )   )   )   ;
     aux[87]  =   (  vet[86]  )   ;
     aux[172]  =   (  vet[95]  )  || (  vet[101]  )  || (  vet[76]  )  || (  vet[175]  )  || (  vet[122]  )  || (  vet[117]  )   ;
     aux[113]  =   (  vet[51]  )   ;
     aux[65]  =   (  ! (   (  vet[66]  )   )   )  ||! (  vet[66]  )   ;
     aux[56]  =   (  vet[177]  )   ;
     aux[138]  =   (  vet[125]  )  || (  vet[127]  )   ;
     aux[109]  =   (  vet[108]  )  || (  vet[119]  )   ;
     aux[27]  =   (  vet[17]  )  || (  vet[140]  )   ;
     aux[119]  =   (  vet[95]  )   ;
     aux[85]  =   (  vet[171]  )  || (  vet[169]  )  || (  vet[172]  )  || (  vet[170]  )   ;
     aux[101]  =   (  vet[99] && (   (   (  vet[103] &&vet[25]  )   )   )   )  || (  vet[100] && (   (   (  vet[103] &&vet[25]  )   )   )   )   ;
     aux[76]  =   (  vet[25] && (   (   (  vet[77] &&vet[98] &&vet[75]  )   )   )   )   ;
     aux[5]  =   (  vet[132]  )  || (  vet[186]  )   ;
     aux[19]  =   (  vet[168]  )  || (  vet[18]  )  || (  vet[10]  )   ;
     aux[92]  =   (  vet[53] && (   (   (  vet[93] &&vet[91]  )   )   )   )   ;
     aux[164]  =   (  vet[181]  )   ;
     aux[171]  =   (   (  vet[138] && (   (   (  vet[183]  )   )   )   )  &&! (  vet[51]  )   )  || (   (  vet[118]  )  &&! (  vet[51]  )   )   ;
     aux[37]  =   (   (   (  vet[164] && (   (   (  vet[172] &&vet[134]  )   )   )   )  &&! (  vet[170] && (   (   (  vet[159]  )   )   )   )   )  &&! (  vet[169]  )   )  || (  vet[134] && (   (   (  vet[37] &&vet[172]  )   )   )   )   ;
     aux[81]  =   (   (   (  vet[134] && (   (   (  !vet[37]  )   )   )   )  &&! (  vet[177] && (   (   (  vet[135]  )   )   )   )   )  &&! (  vet[172] && (   (   (  vet[174]  )   )   )   )   )  || (   (   (  vet[135]  )  &&! (  vet[177] && (   (   (  vet[135]  )   )   )   )   )  &&! (  vet[172] && (   (   (  vet[174]  )   )   )   )   )   ;
     aux[121]  =   (  vet[187]  )   ;
     aux[176]  =   (  vet[182]  )   ;
     aux[20]  =   (  vet[19]  )   ;
     aux[140]  =   (  vet[35]  )   ;
     aux[126]  =   (  vet[128]  )   ;
     aux[132]  =   (  vet[24]  )  || (  vet[133] && (   (   (  vet[184]  )   )   )   )   ;
     aux[186]  =   (  vet[114] && (   (   (  vet[150]  )   )   )   )   ;
     aux[104]  =   (  vet[173]  )   ;
     aux[97]  =   (  vet[37] && (   (   (  vet[134]  )   )   )   )  || (  vet[172] && (   (   (  vet[134]  )   )   )   )  || (  vet[164] && (   (   (  vet[134]  )   )   )   )  || (  vet[135] && (   (   (  vet[134]  )   )   )   )   ;
     aux[151]  =   (  vet[153]  )   ;
     aux[3]  =   (  vet[171]  )  || (  vet[120]  )  || (  vet[32]  )   ;
     aux[29]  =   (  vet[51]  )   ;
     aux[168]  =   (  vet[10]  )  || (  vet[36]  )   ;
     aux[46]  =   (  vet[45]  )   ;
     aux[143]  =   (  vet[142]  )   ;
     aux[51]  =   (  vet[29]  )  || (   (  vet[174]  )  &&! (  vet[177]  )   )   ;
     aux[26]  =   (  ! (   (  vet[123]  )   )   )  ||! (  vet[123]  )   ;
     aux[32]  =   (  vet[124]  )   ;
     aux[78]  =   (   (   (   (  vet[134] && (   (   (  vet[170] &&vet[135] &&vet[149] &&vet[159]  )   )   )   )  &&! (  vet[169] && (   (   (  vet[37]  )   )   )   )   )  &&! (  vet[174] && (   (   (  vet[37]  )   )   )   )   )  &&! (  vet[172] && (   (   (  vet[37]  )   )   )   )   )   ;
     aux[160]  =   (   (  vet[177]  )  &&! (  vet[51]  )   )   ;
     aux[182]  =   (  vet[111]  )   ;
     aux[115]  =   (  vet[122]  )   ;
     aux[41]  =   (  vet[72] && (   (   (  vet[178]  )   )   )   )   ;
     aux[103]  =   (  ! (   (  vet[173]  )   )   )  ||! (  vet[173]  )   ;
     aux[66]  =   (  vet[8]  )  || (  vet[136]  )  || (  vet[178]  )   ;
     aux[173]  =   (  vet[102]  )  || (  vet[96]  )   ;
     aux[163]  =   (  vet[187]  )  || (  vet[43]  )   ;
     aux[62]  =   (  vet[60] && (   (   (  vet[64] &&vet[63]  )   )   )   )  || (  vet[61] && (   (   (  vet[64] &&vet[63]  )   )   )   )   ;
     aux[73]  =   (  vet[112]  )  || (  vet[72]  )   ;
     aux[153]  =   (  vet[167]  )  || (  vet[154]  )   ;
     aux[21]  =   (  vet[4]  )  || (  vet[7]  )   ;
     aux[120]  =   (  vet[150] && (   (   (  vet[27]  )   )   )   )  || (  vet[126]  )  || (  vet[130]  )   ;
     aux[90]  =   (  vet[88] && (   (   (  vet[73] &&vet[53] &&vet[170] &&vet[159]  )   )   )   )  || (  vet[89] && (   (   (  vet[73] &&vet[53] &&vet[170] &&vet[159]  )   )   )   )   ;
     aux[179]  =   (  vet[37] && (   (   (  vet[149] &&vet[134]  )   )   )   )   ;
     aux[142]  =   (  vet[21] && (   (   (  vet[57]  )   )   )   )  || (  vet[95]  )  || (  vet[162]  )  || (  vet[40]  )  || (  vet[153]  )  || (  vet[35]  )   ;
     aux[122]  =   (  vet[21]  )  || (  vet[119] && (   (   (  vet[98]  )   )   )   )  || (  vet[23]  )   ;
     aux[175]  =   (  vet[95]  )   ;
     aux[15]  =   (  vet[0]  )   ;
     aux[136]  =   (  vet[182]  )   ;
     aux[174]  =   (  vet[101]  )   ;
     aux[96]  =   (  vet[81] && (   (   (  vet[97] &&vet[25] &&vet[98]  )   )   )   )  || (  vet[94] && (   (   (  vet[97] &&vet[25] &&vet[98]  )   )   )   )   ;
     aux[127]  =   (  vet[128]  )   ;
     aux[11]  =   (  vet[152]  )   ;
     aux[131]  =   (  vet[158]  )   ;
     aux[130]  =   (  vet[176]  )   ;
     aux[133]  =   (  vet[163]  )   ;
     aux[144]  =   (  vet[15]  )   ;
     aux[112]  =   (  vet[169]  )   ;
     aux[123]  =   (  vet[139]  )  || (  vet[158]  )   ;
     aux[1]  =   (  vet[141]  )   ;
     aux[16]  =   (  vet[20]  )  || (  vet[145]  )   ;
     aux[13]  =   (  vet[110]  )   ;
     aux[38]  =   (  vet[22] && (   (   (  vet[178]  )   )   )   )  || (  vet[19]  )   ;
     aux[9]  =   (  vet[16]  )   ;
     aux[42]  =   (  vet[22]  )  || (  vet[72]  )   ;
     aux[80]  =   (  vet[79]  )   ;
     aux[150]  =   (  vet[185]  )  || (  vet[137]  )  || (  vet[27] && (   (   (  vet[140]  )   )   )   )  || (  vet[184]  )   ;
     aux[110]  =   (  vet[147]  )   ;
     aux[114]  =   (  vet[150]  )   ;
     aux[178]  =   (  vet[4] && (   (   (  vet[21]  )   )   )   )   ;
     aux[59]  =   (  vet[58]  )   ;
     aux[167]  =   (  vet[54]  )   ;
     aux[99]  =   (  vet[113]  )  || (   (   (   (  vet[51] && (   (   (  vet[149] &&vet[134]  )   )   )   )  &&! (  vet[37]  )   )  &&! (  vet[177] && (   (   (  vet[160]  )   )   )   )   )  &&! (  vet[112]  )   )   ;
     aux[165]  =   (  vet[174]  )  || (  vet[170]  )   ;
     aux[149]  =   (  vet[149]  )  || (  vet[173]  )   ;
     aux[145]  =   (  vet[28]  )   ;
     aux[125]  =   (  vet[128]  )   ;
     aux[54]  =   (  vet[121]  )  || (  vet[161]  )   ;
     aux[14]  =   (  vet[13]  )   ;
     aux[139]  =   (  vet[150]  )  || (  vet[24]  )  || (  vet[133]  )   ;
     aux[67]  =   (  vet[134] && (   (   (  vet[51] ||vet[170]  )  && (   (   (  vet[149]  )   )   )   )   )   )   ;
     aux[12]  =   (  vet[27]  )   ;
     aux[74]  =   (  vet[72]  )   ;
     aux[60]  =   (   (   (  vet[171] && (   (   (  vet[149] &&vet[134]  )   )   )   )  &&! (  vet[37]  )   )  &&! (  vet[170]  )   )  || (   (   (  vet[6]  )  &&! (  vet[37]  )   )  &&! (  vet[170]  )   )  || (   (   (  vet[3] && (   (   (  vet[171]  )   )   )   )  &&! (  vet[37]  )   )  &&! (  vet[170]  )   )  || (   (   (  vet[160] && (   (   (  vet[177] &&vet[149] &&vet[134]  )   )   )   )  &&! (  vet[37]  )   )  &&! (  vet[170]  )   )  || (   (   (  vet[56]  )  &&! (  vet[37]  )   )  &&! (  vet[170]  )   )   ;
     aux[33]  =   (  vet[171]  )   ;
     aux[117]  =   (   (  vet[119]  )  &&! (  vet[166]  )   )  || (   (  vet[95]  )  &&! (  vet[166]  )   )  || (   (  vet[109]  )  &&! (  vet[166]  )   )  || (   (  vet[87]  )  &&! (  vet[166]  )   )   ;
     aux[170]  =   (  vet[84]  )  || (  vet[92]  )  || (  vet[106]  )  || (  vet[90]  )  || (  vet[69]  )   ;
     aux[95]  =   (  vet[81] && (   (   (  vet[25] &&vet[98]  )  && (   (   (  !vet[97]  )   )   )   )   )   )  || (  vet[94] && (   (   (  vet[25] &&vet[98]  )  && (   (   (  !vet[97]  )   )   )   )   )   )   ;
     aux[161]  =   (  vet[38]  )  || (  vet[98] && (   (   (  vet[95]  )   )   )   )   ;
     aux[141]  =   (  vet[143]  )   ;
     aux[22]  =   (  vet[178]  )   ;
     aux[84]  =   (  vet[83] && (   (   (  vet[53] &&vet[25]  )   )   )   )  || (  vet[82] && (   (   (  vet[53] &&vet[25]  )   )   )   )   ;
     aux[118]  =   (  vet[73] && (   (   (  vet[74]  )   )   )   )   ;
     aux[148]  =   (  vet[157]  )   ;
     aux[134]  =   (  vet[21] && (   (   (  vet[178]  )   )   )   )  || (  vet[178] && (   (   (  vet[21]  )   )   )   )  || (   (  vet[14] && (   (   (  vet[138]  )   )   )   )  &&! (  vet[55]  )   )   ;
     aux[57]  =   (  vet[4]  )   ;
     aux[111]  =   (  vet[80]  )   ;
     aux[0]  =   (  vet[50]  )   ;
     aux[185]  =   (  vet[168]  )   ;
     aux[154]  =   (  vet[28]  )   ;
     aux[69]  =   (  vet[67] && (   (   (  vet[71] &&vet[70]  )   )   )   )  || (  vet[68] && (   (   (  vet[71] &&vet[70]  )   )   )   )   ;
     aux[102]  =   (  vet[99] && (   (   (  vet[25] &&vet[104]  )   )   )   )  || (  vet[100] && (   (   (  vet[25] &&vet[104]  )   )   )   )   ;
     aux[17]  =   (  vet[35] && (   (   (  vet[10]  )   )   )   )   ;
     aux[159]  =   (  vet[181] && (   (   (  vet[170]  )   )   )   )  || (  vet[159] && (   (   (  vet[181] ||vet[170]  )   )   )   )   ;
     aux[146]  =   (  vet[47]  )   ;
     aux[187]  =   (  vet[115] && (   (   (  vet[22]  )   )   )   )   ;
     aux[8]  =   (  vet[9] && (   (   (  vet[16]  )   )   )   )   ;
     aux[24]  =   (  vet[12]  )  || (  vet[156]  )   ;
     aux[88]  =   (  vet[134] && (   (   (  vet[170] &&vet[149]  )   )   )   )   ;
     aux[177]  =   (   (  vet[177]  )  &&! (  vet[51]  )   )  || (   (  vet[169]  )  &&! (  vet[51]  )   )   ;
     aux[2]  =  vet[2]  ;
     aux[58]  =  vet[58]  ;
     aux[129]  =  vet[129]  ;
     aux[72]  =  vet[72]  ;
     aux[89]  =  vet[89]  ;
     aux[75]  =  vet[75]  ;
     aux[64]  =  vet[64]  ;
     aux[83]  =  vet[83]  ;
     aux[105]  =  vet[105]  ;
     aux[98]  =  vet[98]  ;
     aux[100]  =  vet[100]  ;
     aux[68]  =  vet[68]  ;
     aux[180]  =  vet[180]  ;
     aux[77]  =  vet[77]  ;
     aux[63]  =  vet[63]  ;
     aux[94]  =  vet[94]  ;
     aux[45]  =  vet[45]  ;
     aux[53]  =  vet[53]  ;
     aux[49]  =  vet[49]  ;
     aux[71]  =  vet[71]  ;
     aux[93]  =  vet[93]  ;
     aux[91]  =  vet[91]  ;
     aux[107]  =  vet[107]  ;
     aux[25]  =  vet[25]  ;
     aux[48]  =  vet[48]  ;
     aux[18]  =  vet[18]  ;
     aux[4]  =  vet[4]  ;
     aux[61]  =  vet[61]  ;
     aux[7]  =  vet[7]  ;
     aux[79]  =  vet[79]  ;
     aux[108]  =  vet[108]  ;
     aux[30]  =  vet[30]  ;
     aux[86]  =  vet[86]  ;
     aux[70]  =  vet[70] ;
    
}
