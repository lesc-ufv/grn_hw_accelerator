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
        
    grn_acc.execute();
        
    grn_acc.print_report();
    
    grn_acc.cleanup();
    
    return 0;
}

