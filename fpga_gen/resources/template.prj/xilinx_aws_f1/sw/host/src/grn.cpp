//
// Created by lucas on 11/08/2021.
//

#include <grn.h>
#include <cstring>
#include <langinfo.h>

Grn::Grn(std::string xclbin,
         std::string kernel_name,
         std::string input_file,
         std::string output_file): m_xclbin(std::move(xclbin)),
                            m_kernel_name(std::move(kernel_name)),
                            m_input_file(std::move(input_file)),
                            m_output_file(std::move(output_file)){

    m_grn_fpga = new GrnFpga(NUM_CHANNELS,NUM_CHANNELS);
    read_input_file();

    m_input_data = (grn_conf_t **) malloc(sizeof(grn_conf_t*)*NUM_CHANNELS);
    m_output_data = (grn_data_out_t **) malloc(sizeof(grn_data_out_t*)*NUM_CHANNELS);
    m_input_size = (unsigned long *) malloc(sizeof(unsigned long)*NUM_CHANNELS);
    m_output_size = (unsigned long *) malloc(sizeof(unsigned long)*NUM_CHANNELS);
    memset(m_input_size,0,sizeof(unsigned long)*NUM_CHANNELS);
    memset(m_output_size,0,sizeof(unsigned long)*NUM_CHANNELS);
}
Grn::~Grn(){
    m_grn_fpga->cleanup();
    for (int i = 0; i < NUM_CHANNELS; ++i) {
        delete m_input_data[i];
        delete m_output_data[i];
    }
    delete m_input_size;
    delete m_output_size;
    delete m_grn_fpga;
}
void Grn::read_input_file(){
    std::string line;
    std::ifstream myfile(m_input_file);
    if (myfile.is_open()) {
        while (getline(myfile, line)) {
            char *id = strtok((char *)line.c_str(), ",");
            char *init_state = strtok(NULL, ",");
            char *end_state = strtok(NULL, ",");
            char *num_states = strtok(NULL, ",");
            auto idx = std::stoul(id, nullptr, 10) / NUM_COPIES_PER_CHANNEL;
            auto sz = std::stoul(num_states, nullptr, 10);
            m_input_size[idx]++;
            m_output_size[idx]+=sz;
        }
        myfile.clear();
        myfile.seekg(0);
        for (int j = 0; j < NUM_CHANNELS; ++j) {
            m_grn_fpga->createInputQueue(j,sizeof(grn_conf_t)*m_input_size[j]);
            m_input_data[j] = (grn_conf_t*)m_grn_fpga->getInputQueue(j);
            m_grn_fpga->createOutputQueue(j,sizeof(grn_data_out_t)*m_output_size[j]);
            m_output_data[j] = (grn_data_out_t*) m_grn_fpga->getOutputQueue(j);
        }
        int c[NUM_CHANNELS];
        memset(c,0,sizeof(int)*NUM_CHANNELS);
        while (getline(myfile, line)) {
            char *id = strtok((char *)line.c_str(), ",");
            char *init_state = strtok(NULL, ",");
            char *end_state = strtok(NULL, ",");
            char *num_states = strtok(NULL, ",");
            std::string init_state_str(init_state);
            std::string end_state_str(end_state);
            auto ch = std::stoul(id, nullptr, 10) / NUM_COPIES_PER_CHANNEL;
            m_input_data[ch][c[ch]].id = std::stoul(id, nullptr, 10) % NUM_COPIES_PER_CHANNEL;
            for(int i = 0,p = 0; i < STATE_SIZE_BYTES;++i,p+=2){
                m_input_data[ch][c[ch]].init_state[i] = std::stoi(init_state_str.substr(p,p+2), nullptr, 16);
                m_input_data[ch][c[ch]].end_state[i] = std::stoi(end_state_str.substr(p,p+2), nullptr, 16);
            }
            c[ch]++;
        }
        myfile.close();
    }
    else{
        std::cout << "Error: input file not found." << std::endl;
    }
}
void Grn::run(){
    m_grn_fpga->fpga_init(m_xclbin, m_kernel_name);
    read_input_file();
    m_grn_fpga->execute();
}
void Grn::save_perf_report(){
//todo: implement this function
}
void Grn::save_grn_report(){

    unsigned long total = 0;
    for (int k = 0; k < NUM_CHANNELS; ++k) {
        total += m_output_size[k];
    }
    std::stringstream data[total];
    unsigned long c = 0;
    std::ofstream myfile(m_output_file);
    unsigned long c_global[NUM_COPIES];
    memset(c_global,0,sizeof(unsigned long )* NUM_COPIES);
    for (int k = 0; k < NUM_CHANNELS; ++k) {
        for(int i = 0; i < m_output_size[k];i++){
            unsigned long idg = ((k*NUM_COPIES_PER_CHANNEL) + m_output_data[k][i].id);
            data[c] <<  idg << "," << c_global[idg] <<  "," << m_output_data[k][i].period << "," <<  m_output_data[k][i].transient <<  ",";
            for(char j : m_output_data[k][i].state){
                data[c] << j;
            }
            c_global[idg]++;
            c++;
        }
    }
    sort(&data[0],&data[total-1]);
    for(int i = 0; i < total; i++){
        myfile << data[i].str();
    }
    myfile.close();
}

