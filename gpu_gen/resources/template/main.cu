#include <grn_gpu.h>
#include <iostream>
#include <string>
#include <utility>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <iomanip>
#include <timer.h>

using namespace std;

size_t read_input_file(std::string input_file,bool **initial_states);
void write_output_file(std::string output_file,uint32_t * transients, uint32_t * periods, bool * attractors, size_t num_states);
void write_report_file(double exec_time);

TIMER_INIT(1);

int main(int argc, char *argv[]) {

    if(argc < 3){
        printf("Usage: ./%s <GRN initial states file> <Output file name>\n",argv[0]);
        return EXIT_FAILURE;
    }

    std::string input_file = argv[1];
    std::string output_file = argv[2];
    cudaError_t err = cudaSuccess;

    bool *h_initial_states = NULL;
    size_t num_states = read_input_file(input_file,&h_initial_states);

    size_t size = NUM_NOS * num_states * sizeof(bool);
    size_t size_transients = num_states*sizeof(uint32_t);
    size_t size_periods = num_states*sizeof(uint32_t);

    uint32_t *h_transients = (uint32_t*)malloc(size_transients);
    uint32_t *h_periods = (uint32_t*)malloc(size_periods);
    bool *h_attractors = (bool *)malloc(size);

    bool     *d_initial_states = NULL;
    uint32_t *d_transients = NULL;
    uint32_t *d_periods = NULL;
    bool     *d_attractors = NULL;

    printf("Find attractors net %d nodes in %lu initials states.\n", NUM_NOS,num_states);

    if (h_transients == NULL)
    {
        fprintf(stderr, "Failed to allocate h_transients!\n");
        exit(EXIT_FAILURE);
    }

    if (h_periods == NULL)
    {
        fprintf(stderr, "Failed to allocate h_periods!\n");
        exit(EXIT_FAILURE);
    }

    if (h_attractors == NULL)
    {
        fprintf(stderr, "Failed to allocate h_attractors!\n");
        exit(EXIT_FAILURE);
    }

    err = cudaMalloc((void **)&d_initial_states, size);
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to allocate d_attractors (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    err = cudaMalloc((void **)&d_transients, num_states*sizeof(uint32_t));
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to allocate d_transients (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    err = cudaMalloc((void **)&d_periods, num_states*sizeof(uint32_t));

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to allocate d_periods (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }
    err = cudaMalloc((void **)&d_attractors, size);
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to allocate d_attractors (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    TIMER_START(0);

    err = cudaMemcpy(d_initial_states,h_initial_states,size, cudaMemcpyHostToDevice);
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to copy vector h_initial_states from host to device (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    uint32_t threadsPerBlock = 256;
    uint32_t blocksPerGrid =(num_states + threadsPerBlock - 1) / threadsPerBlock;

    printf("CUDA kernel launch with %d blocks of %d threads\n", blocksPerGrid, threadsPerBlock);

    findAttractor<<<blocksPerGrid, threadsPerBlock>>>(d_initial_states, d_attractors,d_transients,d_periods,num_states);

    err = cudaGetLastError();
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to launch findAttractor kernel (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

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

    TIMER_STOP_ID(0);

    err = cudaFree(d_initial_states);
    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to free device vector d_initial_states (error code %s)!\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

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

    write_output_file(output_file,h_transients,h_periods,h_attractors,num_states);
    write_report_file(TIMER_REPORT_MS(0));

    free(h_initial_states);
    free(h_transients);
    free(h_periods);
    free(h_attractors);

    err = cudaDeviceReset();

    if (err != cudaSuccess)
    {
        fprintf(stderr, "Failed to deinitialize the device! error=%s\n", cudaGetErrorString(err));
        exit(EXIT_FAILURE);
    }

    printf("Done\n");
    return 0;
}

size_t read_input_file(std::string input_file,bool **initial_states){
    std::string line;
    std::ifstream myfile(input_file);
    size_t num_states = 0;

    if (myfile.is_open()) {
        while (getline(myfile, line)) {
            
            strtok((char *)line.c_str(), ",");
            strtok(NULL, ",");
            strtok(NULL, ",");
            char *str_num_states = strtok(NULL, ",");
            auto sz = std::stoul(str_num_states, nullptr, 10);
            num_states+=sz;            
        }
        myfile.clear();
        myfile.seekg(0);

        *initial_states = (bool *)malloc(sizeof(bool)*num_states*NUM_NOS);
        int num_nos_bytes = (int)ceil(NUM_NOS/8.0);
        int j = 0;
        while (getline(myfile, line)) {
            strtok((char *)line.c_str(), ",");
            char *init_state = strtok(NULL, ",");
            std::string init_state_str(init_state);
            int cb = 0;
            for(int i = 0,p = (num_nos_bytes*2)-2; i < num_nos_bytes;i++,p-=2){
                unsigned long v = std::stoul(init_state_str.substr(p,2), nullptr, 16);
                for(int b = 0;b < 8;b++){
                    (*initial_states)[j*NUM_NOS + cb] = (v & (1 << b));
                    cb++;
                    if(cb >= NUM_NOS){
                        i = num_nos_bytes;
                        break;
                    }
                }
            }
            j++;
        }
        myfile.close();
        return num_states;
    }
    else{
        std::cout << "Error: input file not found." << std::endl;
        exit(255);
    }

}
void write_output_file(std::string output_file, uint32_t * transients, uint32_t * periods, bool * attractors, size_t num_states){

    std::ofstream myfile(output_file);
    unsigned char b = 0;
    int cb = 0;
    for(unsigned long i = 0; i < num_states;i++){
            myfile <<  0 << "," << 0 <<  "," << periods[i] << "," <<  transients[i] <<  ",";
            for(int j=NUM_NOS-1; j >= 0 ;--j){
               b |= attractors[i*NUM_NOS + j];
               b <<= 1;
               cb++;
               if(cb == 8 || j == 0){
                     myfile << std::hex << std::setw(2) << std::setfill('0') << (int)b << std::dec;
                     b = 0;
                     cb = 0;
               }
            }
            myfile << std::endl;
    }
    myfile.close();
}

void write_report_file(double exec_time){
 std::ofstream myfile("performance_report.csv");
 myfile << "Execution time(ms)" << std::endl;
 myfile << exec_time << std::endl;
 myfile.close();
}
