//
// Created by lucas on 11/08/2021.
//

#ifndef GRN_H
#define GRN_H

#include <grn_fpga/grn_fpga.h>
#include <grn_defs.h>
#include <iostream>
#include <string>
#include <vector>
#include <utility>
#include <fstream>
#include <sstream>
#include <map>
#include <algorithm>
#include <iomanip>

class Grn {
private:
    std::string m_xclbin;
    std::string m_kernel_name;
    std::string m_input_file;
    std::string m_output_file;
    GrnFpga * m_grn_fpga;
    grn_conf_t ** m_input_data;
    grn_data_out_t ** m_output_data;
    unsigned long * m_input_size;
    unsigned long * m_output_size;
    void readInputFile();

public:
    Grn(std::string xclbin, std::string kernel_name,std::string input_file, std::string output_file);
    ~Grn();
    void run();
    void savePerfReport();
    void saveGrnReport();
};

bool myCmp(std::string a, std::string b);

#endif //GRN_H
