#include <iostream>
#include <math.h>
#include <omp.h>
#include <chrono>
#include <vector>
#include <algorithm>
#include <fstream>

#define NUM_NOS 21

using namespace std;
using namespace std::chrono;

vector<string> splitString(string s, string delimiter);
void readInputFile(uint32_t ***period, uint32_t ***transient, uint64_t **init_state, uint64_t **end_state, bool ***s0, bool ***s1, uint64_t ***atractor, uint32_t *lines, string filename);
void pass(bool *aux);
bool equals(bool *vet1, bool *vet2);
string vet_to_hex(bool *vet1);
void initialState(uint64_t valor, bool *vet1, bool *vet2);
string boolArraytoString(bool *vet);
uint64_t boolArraytoInt(bool *vet);
void runGNR(uint64_t *init_state, uint64_t *end_state, uint32_t **period_vet, uint32_t **transient_vet, bool **s0, bool **s1, uint64_t **atractor_vet, uint32_t lines);
void writeOutputFile(uint32_t **period, uint32_t **transient, uint64_t *init_state, uint64_t *end_state, uint64_t **atractor, uint32_t lines, string filename);

class InputParser {
private:
    vector<string> tokens;

public:
    InputParser(int &argc, char **argv) {
        for(int i=1; i<argc; ++i) {
            this->tokens.push_back(string(argv[i]));
        }
    }

    bool cmdOptionExists(const string &option) const{
        return find(this->tokens.begin(), this->tokens.end(), option)
                != this->tokens.end();
    }

    const string& getCmdOption(const string &option) const{
        vector<string>::const_iterator itr;
        itr =  find(this->tokens.begin(), this->tokens.end(), option);
        if (itr != this->tokens.end() && ++itr != this->tokens.end() && (*itr).front() != '-'){
            return *itr;
        }
        static const string empty_string("");
        return empty_string;
    }
};

int main(int argc, char **argv) {
    InputParser input(argc, argv);

    string filein = input.getCmdOption("-i");
    string fileout = input.getCmdOption("-o");

    if(!filein.size() || !fileout.size()) {
        cout << "Usage: ./<executable> -i <input filename> -o <utput filename csv>" << endl;
        exit(255);
    } 
        
    uint32_t **period_vet = nullptr;
    uint32_t **transient_vet = nullptr;
    uint64_t *init_state = nullptr;
    uint64_t *end_state = nullptr;
    uint32_t lines;

    bool **s0 = nullptr;
    bool **s1 = nullptr;

    uint64_t **atractor_vet;
    
    readInputFile(&period_vet, &transient_vet, &init_state, &end_state, &s0, &s1, &atractor_vet, &lines, filein);
    
    if(period_vet == nullptr || transient_vet == nullptr || init_state == nullptr || end_state == nullptr) {
        cout << "Error: malloc failed!" << endl;
        exit(255);
    }
    
    high_resolution_clock::time_point s;
    duration<double> diff{};
    s = high_resolution_clock::now();
    
    runGNR(init_state, end_state, period_vet, transient_vet, s0, s1, atractor_vet, lines);
    
    diff = high_resolution_clock::now() - s;
    
    // cout << "Number of state: " << NUM_STATES << endl;
    cout << "Execution Time: " << diff.count() * 1000 << "ms" << endl;
    // cout << "State per second: " << (NUM_STATES/diff.count()) << endl;

    writeOutputFile(period_vet, transient_vet, init_state, end_state, atractor_vet, lines, fileout);
    
    // free(period_vet);
    // free(transient_vet);
     
    return 0;
}

void writeOutputFile(uint32_t **period, uint32_t **transient, uint64_t *init_state, uint64_t *end_state, uint64_t **atractor, uint32_t lines, string filename) {
    ofstream file(filename);
    for(uint32_t l=0; l<lines; ++l) {
        for(uint64_t s=init_state[l], i = 0; s <= end_state[l]; ++s, ++i) {
            file << to_string(l) << ", " << to_string(period[l][i]) << ", " << to_string(transient[l][i]) << ", " << std::hex << (atractor[l][i]) << endl;
        }
    }
    file.close();
}

vector<string> splitString(string s, string delimiter) {
    size_t pos = 0;
    vector<string> ans;
    while((pos = s.find(delimiter)) != string::npos) {
        ans.push_back(s.substr(0, pos));
        s.erase(0, pos + delimiter.length());
    }
    ans.push_back(s);
    return ans;
}

void readInputFile(uint32_t ***period, uint32_t ***transient, uint64_t **init_state, uint64_t **end_state, bool ***s0, bool ***s1, uint64_t ***atractor, uint32_t *lines, string filename) {
    ifstream file(filename);
    uint32_t cnt_lines = 0;
    string line;
    uint32_t size;
    vector<vector<string>> all_items;
    while(getline(file, line)) {
        auto items = splitString(line, ",");
        if(items.size() == 4) {
            cnt_lines++;
            all_items.push_back(items);
        }
    }
    file.close();

    (*lines) = cnt_lines;
    (*period) = (uint32_t **) malloc(cnt_lines * sizeof (uint32_t *));
    (*transient) = (uint32_t **) malloc(cnt_lines * sizeof(uint32_t *));
    (*init_state) = (uint64_t *) malloc(cnt_lines * sizeof(uint64_t));
    (*end_state) = (uint64_t *) malloc(cnt_lines * sizeof(uint64_t));
    (*s0) = (bool **) malloc(cnt_lines * sizeof(bool *));
    (*s1) = (bool **) malloc(cnt_lines * sizeof(bool *));
    (*atractor) = (uint64_t **) malloc(cnt_lines * sizeof (uint64_t *));

    for(int i=0; i<cnt_lines; ++i) {
        size = stoul(all_items[i][3], NULL, 10);
        (*period)[i] = (uint32_t *) malloc(size * sizeof(uint32_t));
        (*transient)[i] = (uint32_t *) malloc(size * sizeof(uint32_t));
        (*init_state)[i] = stoull(all_items[i][1], NULL, 16);
        (*end_state)[i] = stoull(all_items[i][2], NULL, 16);
        (*s1)[i] = (bool *) malloc(NUM_NOS * sizeof(bool));
        (*s0)[i] = (bool *) malloc(NUM_NOS * sizeof(bool)); 
        (*atractor)[i] = (uint64_t *) malloc(size * sizeof(uint64_t));
    }
}

void runGNR(uint64_t *init_state, uint64_t *end_state, uint32_t **period_vet, uint32_t **transient_vet, bool **s0, bool **s1, uint64_t **atractor_vet, uint32_t lines) {
    #pragma omp parallel for schedule(static)
    for(uint32_t l=0; l<lines; ++l) {
        for (uint64_t s = init_state[l], i = 0; s <= end_state[l]; s++, i++) {
            initialState(s, s0[l], s1[l]);
            transient_vet[l][i] = 0;
            period_vet[l][i] = 0;
            do {
                pass(s0[l]);
                pass(s1[l]);
                pass(s1[l]);
                // transient++;
                transient_vet[l][i]++;
            } while (!equals(s0[l], s1[l]));
            do {
                pass(s1[l]);
                // period++;
                period_vet[l][i]++;
            } while (!equals(s0[l], s1[l]));

            period_vet[l][i]--;
            atractor_vet[l][i] = boolArraytoInt(s0[l]);
            // printf("%lld: P: %u T: %u\n", i, period, transient);
            /* if(output.is_open()) {
                string str = "";
                str += to_string()
                str += to_string(i);
                str += ",";
                str += to_string(period);
                str += ",";
                str += to_string(transient);
                str += "\n";
                cout << str << endl;
                output.write(str.c_str(), str.size());
            } */
        }
    }
}

void initialState(uint64_t valor, bool *vet1, bool *vet2) {
    for (int i = 0; i < NUM_NOS; i++) {
        vet1[i] = (valor & 1) != 0;
        vet2[i] = vet1[i];
        valor >>= 1;
    }
}

bool equals(bool *vet1, bool *vet2) {
    for (int i = 0; i < NUM_NOS; i++) {
        if (vet1[i] != vet2[i]) {
            return false;
        }
    }
    return true;
}

string vet_to_hex(bool *vet) {
    string hex = "";
    for(int i=0; i<NUM_NOS; i += 4) {
        int v=0;
        for(int j=i+3; j>=i; --j) {
            if(j < NUM_NOS) {
                v = (v << 1) | (vet[j] ? 1 : 0);
            } 
        }
        if(v >= 10) hex += ('a' + v - 10);
        else hex += to_string(v);
    }
    reverse(hex.begin(), hex.end());

    return hex;
}

string boolArraytoString(bool *vet) {
    string out = "";
    for (int i = NUM_NOS - 1; i >= 0; i--) {
        if (vet[i]) {
            out += "1";
        } else {
            out += "0";
        }
    }
    return out;
}

uint64_t boolArraytoInt(bool *vet) {
    uint64_t out = 0;
    // std::cout <<"boolArraytoInt:"<< std::endl;
    for (int i = NUM_NOS - 1; i >= 0; i--) {
        //   std::cout << vet[i] << " ";
        out = (out << 1ll) | vet[i];
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
void pass(bool *aux){int size, 
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

void pass(bool *aux){int size, 
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

void pass(bool *aux) {

}

#endif