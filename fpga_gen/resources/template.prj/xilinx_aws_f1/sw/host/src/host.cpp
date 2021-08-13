#include <host.h>


int main(int argc, char *argv[]){
            
    if (argc != 5) {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File> <kernel name> <GRN Configuration file> <Output file name>" << std::endl;
        return EXIT_FAILURE;
    }
    
    std::string binaryFile = argv[1];
    std::string kernel_name = argv[2];
    std::string grn_cfg = argv[3];
    std::string grn_outputfile = argv[4];

    auto grn = Grn(binaryFile,kernel_name,grn_cfg,grn_outputfile);
    grn.run();
    grn.save_grn_report();

    return 0;
}

