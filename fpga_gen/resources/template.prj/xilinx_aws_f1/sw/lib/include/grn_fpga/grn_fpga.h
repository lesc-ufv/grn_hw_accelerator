#include <cstring>
#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <vector>
#include <string>
#include <cmath>

#include <grn_fpga/timer.h>
#include <xcl2/xcl2.hpp>

//Timers
#define INIT_TIMER_ID 0
#define DATA_CPY_HtoD 1
#define DATA_CPY_DtoH 2
#define EXE_TIMER_ID 3
#define TOTAL_EXE_TIMER_ID 4
#define SET_ARGS_TIMER_ID 5

using namespace std;
using namespace std::chrono;

typedef unsigned char byte;

class GrnFpga{
    
private:
  cl::Context m_context;
  cl::CommandQueue m_q;
  cl::Program m_prog;
  cl::Kernel m_kernel;
  
  std::vector<cl::Memory> m_input_buffer;
  std::vector<cl::Memory> m_output_buffer;
  
  int m_num_inputs;
  int m_num_outputs;
  
  size_t *m_input_size_bytes;
  size_t *m_output_size_bytes;
    
  cl_int m_err;
  
  void ** m_inputs_ptr;
  void ** m_outputs_ptr;

  void setArgs();
  
  void * allocateMemAlign(size_t size);
      
public:
        
  GrnFpga(int num_inputs, int num_outputs);  
  
  int fpgaInit(std::string &binary_file, std::string kernel_name);
  
  void * createInputQueue(int input_id, size_t size);
  
  void * getInputQueue(int input_id);
  
  void * createOutputQueue(int output_id, size_t size);
  
  void * getOutputQueue(int output_id);
  
  int execute();
     
  int cleanup();
      
  int printReport();

  double getInitTime();
  
  double getDataCopyHtoDTime();
  
  double getDataCopyDtoHTime();
  
  double getExecTime();
  
  double getTotalTime();
  
  double getSetArgsTime();

  unsigned long getTotalInputSize();

  unsigned long getTotalOutputSize();

};
