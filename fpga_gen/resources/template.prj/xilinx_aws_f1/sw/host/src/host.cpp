#include <host.h>


int main(int argc, char *argv[]){

    if (argc != 4) {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File> <Kernel name>" << std::endl;
        return EXIT_FAILURE;
    }
    
    std::string binaryFile = argv[1];
    std::string kernel_name = argv[2];
       
    auto grn_acc = GrnFpga(NUM_CHANNELS,NUM_CHANNELS);
    grn_acc.fpga_init(binaryFile, kernel_name);
    
    //create inputs and put the data
    //create outputs
    
    grn_acc.execute();
    
    //print the outputs
    
    grn_acc.print_report();
    
    grn_acc.cleanup();
    
    return 0;
}

