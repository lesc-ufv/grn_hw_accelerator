//
// Created by lucas on 11/08/2021.
//

#ifndef GRN_DEFS_H
#define GRN_DEFS_H

#include <cmath>
#include <algorithm>

#include <acc_config.h>

#define print(x) std::cout << (x) << std::endl

typedef struct grn_data_t{
    unsigned char data[ACC_DATA_BYTES];
}grn_data_t;

typedef struct grn_conf_t{
    union {
        struct{
            int id;
            unsigned char init_state[STATE_SIZE_BYTES];
            unsigned char end_state[STATE_SIZE_BYTES];
        };
        grn_data_t pad;
    };

}grn_conf_t;

typedef struct grn_data_out_t{
    union {
        struct{
            int id;
            int period;
            int transient;
            unsigned char state[STATE_SIZE_BYTES];
       };
        grn_data_t pad;
    };
}grn_data_out_t;

#endif //GRN_DEFS_H


