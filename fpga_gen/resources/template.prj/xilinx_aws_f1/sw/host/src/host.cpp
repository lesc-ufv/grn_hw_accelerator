#include <host.h>

typedef struct grn_conf_t{
    short id;
    char init_state[1];
    char end_state[1];
}grn_conf_t;

typedef struct grn_data_out_t{
    short id;
    int period;
    int transient;
    char end_state[1];
}grn_data_out_t;

int main(int argc, char *argv[]){

    if (argc != 4) {
        std::cout << "Usage: " << argv[0] << " <XCLBIN File> <Kernel name>" << std::endl;
        return EXIT_FAILURE;
    }
    
    std::string binaryFile = argv[1];
    std::string kernel_name = argv[2];
       
    auto grn_acc = GrnFpga(NUM_CHANNELS,NUM_CHANNELS);
    
    grn_acc.fpga_init(binaryFile, kernel_name);
    
    grn_acc.createInputQueue(0,8*sizeof(grn_conf_t));
    
    grn_acc.createOutputQueue(0,8*sizeof(grn_data_out_t));
    
    auto data_in = (grn_conf_t *) grn_acc.getInputQueue(0);
    
    for(int i = 0; i < 8; i++){
        data_in[i].id = 1;
        data_in[i].init_state[0] = i*4;
        data_in[i].end_state[0] = ((i+1)*4) - 1;
    }
            
    grn_acc.execute();
    
    //print the outputs
    
    auto data_out = (grn_data_out_t *) grn_acc.getOutputQueue(0); 
    
    for(int i = 0; i < 8; i++){
        printf("id: %d\n",data_out[i].id);
        printf("transient: %d\n",data_out[i].transient);
        printf("period: %d\n",data_out[i].transient);
        printf("state: %d\n",data_out[i].state[0]);
        printf("------------------------------------\n");
    }
    
    grn_acc.print_report();
    
    grn_acc.cleanup();
    
    return 0;
}

