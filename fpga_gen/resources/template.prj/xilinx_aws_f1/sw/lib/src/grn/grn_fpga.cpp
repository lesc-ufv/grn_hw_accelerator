#include <grn/grn_fpga.h>

TIMER_INIT(5);

GrnFpga::GrnFpga(int num_inputs, int num_outputs):m_input_buffer(num_inputs),
                                                    m_output_buffer(num_outputs),
                                                    m_num_inputs(num_inputs),
                                                    m_num_outputs(num_outputs)
                                                    {
    
    m_input_size_bytes = (size_t *) malloc(sizeof(size_t) * num_inputs);
    m_output_size_bytes = (size_t *) malloc(sizeof(size_t) * num_outputs);
    
    m_inputs_ptr = (void **) malloc(sizeof(void *) * num_inputs);
    m_outputs_ptr = (void **) malloc(sizeof(void *) * num_outputs);
    
    memset(m_input_size_bytes,0, sizeof(size_t) * num_inputs);
    memset(m_output_size_bytes, 0, sizeof(size_t) * num_outputs);
}

int GrnFpga::cgra_fpga_init(std::string &binary_file, std::string kernel_name){

  TIMER_START(INIT_TIMER_ID);   
  cl_int err;
  // get_xil_devices() is a utility API which will find the xilinx
  // platforms and will return list of devices connected to Xilinx platform
  auto devices = xcl::get_xil_devices();
  // read_binary_file() is a utility API which will load the binary_file
  // and will return the pointer to file buffer.
  auto fileBuf = xcl::read_binary_file(binary_file);
  cl::Program::Binaries bins{{fileBuf.data(), fileBuf.size()}};
  bool valid_device = false;
  for (unsigned int i = 0; i < devices.size(); i++) {
    auto device = devices[i];
    // Creating Context and Command Queue for selected Device
    OCL_CHECK(err, m_context = cl::Context(device, NULL, NULL, NULL, &err));
    OCL_CHECK(err, m_q = cl::CommandQueue(m_context, device, CL_QUEUE_PROFILING_ENABLE | CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE, &err));

    std::cout << "Trying to program device[" << i
              << "]: " << device.getInfo<CL_DEVICE_NAME>() << std::endl;
    m_prog = cl::Program(m_context, {device}, bins, NULL, &err);
    if (err != CL_SUCCESS) {
      std::cout << "Failed to program device[" << i << "] with xclbin file!\n";
    } else {
      std::cout << "Device[" << i << "]: program successful!\n";
      valid_device = true;
      break; // we break because we found a valid device
    }
  }
  
  if (!valid_device) {
    std::cout << "Failed to program any device found, exit!\n";
    exit(EXIT_FAILURE);
  }

  OCL_CHECK(err, m_kernel = cl::Kernel(m_prog,kernel_name.c_str(), &err));

  TIMER_STOP_ID(INIT_TIMER_ID);

  return 0;    
    
}

void * GrnFpga::cgra_allocate_mem_align(size_t size){
    
    void *ptr;
    if( posix_memalign((void**)&ptr,4096,size) == 0){
        return ptr;
    }
    return nullptr;
}

void GrnFpga::createInputQueue(int input_id, size_t size){
    if(input_id >= 0 && input_id < m_num_inputs){
        m_inputs_ptr[input_id] = cgra_allocate_mem_align(size);
        m_input_size_bytes[input_id] = size;
        OCL_CHECK(err,
                  m_input_buffer[input_id] = cl::Buffer(m_context,
                                                        CL_MEM_USE_HOST_PTR | CL_MEM_READ_ONLY,
                                                        size, m_inputs_ptr[input_id],
                                                        &err));
    }
}
  
void * GrnFpga::getInputQueue(int input_id){
    if(input_id >= 0 && input_id < m_num_inputs){
        return m_inputs_ptr[input_id];
    }
    return nullptr;
}
  
void GrnFpga::createOutputQueue(int output_id, size_t size){
    if(output_id >= 0 && output_id < m_num_outputs){
        m_outputs_ptr[output_id] = cgra_allocate_mem_align(size);
        m_output_size_bytes[output_id] = size;
        
        OCL_CHECK(err,
                  m_output_buffer[output_id] = cl::Buffer(m_context,
                                                          CL_MEM_USE_HOST_PTR | CL_MEM_WRITE_ONLY,
                                                          size,
                                                          m_outputs_ptr[output_id],
                                                          &err));
    }    
}
  
void * GrnFpga::getOutputQueue(int output_id){
    if(output_id >= 0 && output_id < m_num_outputs){
        return m_outputs_ptr[output_id];
    }
    return nullptr; 
}

void GrnFpga::cgra_set_args(){
    
    int id = m_num_inputs + m_num_outputs;
    for(int i = 0; i < m_num_inputs;++i){
         if(m_input_size_bytes[i] == 0){
            createInputQueue(i,64);
         }        
         OCL_CHECK(err, err = m_kernel.setArg(i, sizeof(cl_int),(void *)& m_input_size_bytes[i]));  
         OCL_CHECK(err, err = m_kernel.setArg(id, m_input_buffer[i]));
         id += 2;
    }
    id = m_num_inputs + m_num_outputs + 1;
    for(int i = 0; i < m_num_outputs;++i){
        if(m_output_size_bytes[i] == 0){
            createOutputQueue(i,64);
        }        
        OCL_CHECK(err, err = m_kernel.setArg(m_num_inputs + i, sizeof(cl_int),(void *)& m_output_size_bytes[i]));
        OCL_CHECK(err, err = m_kernel.setArg(id, m_output_buffer[i]));
        id += 2;
    }
}

int GrnFpga::cgra_execute(){
  
    TIMER_START(TOTAL_EXE_TIMER_ID);
    {
        cgra_set_args();
        TIMER_START(DATA_CPY_HtoD);
        {
            // Copy input data to device global memory
            OCL_CHECK(err, err = m_q.enqueueMigrateMemObjects(m_input_buffer,0/* 0 means from host*/));
            OCL_CHECK(err, err = m_q.finish());
        }
        TIMER_STOP_ID(DATA_CPY_HtoD);
        TIMER_START(EXE_TIMER_ID);
        {
            // Launch the Kernel
            OCL_CHECK(err, err = m_q.enqueueTask(m_kernel));
            OCL_CHECK(err, err = m_q.finish());
        }
        TIMER_STOP_ID(EXE_TIMER_ID);
        TIMER_START(DATA_CPY_DtoH);
        {
            // Copy Result from Device Global Memory to Host Local Memory
            OCL_CHECK(err, err = m_q.enqueueMigrateMemObjects(m_output_buffer, CL_MIGRATE_MEM_OBJECT_HOST));
            OCL_CHECK(err, err = m_q.finish());
        }
        TIMER_STOP_ID(DATA_CPY_DtoH);
    
    }
    TIMER_STOP_ID(TOTAL_EXE_TIMER_ID);
        
    return 0;
}

int GrnFpga::cleanup(){  
    
    for(int i = 0; i < m_num_inputs;++i){
        free(m_inputs_ptr[i]);
    }    
    
    for(int i = 0; i < m_num_outputs;++i){
        free(m_outputs_ptr[i]);
    }
    free(m_inputs_ptr);
    free(m_outputs_ptr);
    free(m_input_size_bytes);
    free(m_output_size_bytes);
    m_input_buffer.clear();
    m_output_buffer.clear();
    return 0;
}

int GrnFpga::print_report(){
    printf("------------------------------------------------------\n");
    printf("  Performance Summary                                 \n");
    printf("------------------------------------------------------\n");
    printf("  Device Initialization      : %12.4f ms\n", TIMER_REPORT_MS(INIT_TIMER_ID));
    printf("  Data copy host to device   : %12.4f ms\n", TIMER_REPORT_MS(DATA_CPY_HtoD));
    printf("  Data copy device to host   : %12.4f ms\n", TIMER_REPORT_MS(DATA_CPY_DtoH));
    printf("  Execution:                 : %12.4f ms\n", TIMER_REPORT_MS(EXE_TIMER_ID));
    printf("  Total:                     : %12.4f ms\n", TIMER_REPORT_MS(TOTAL_EXE_TIMER_ID));
    printf("------------------------------------------------------\n");
    return 0;
}


