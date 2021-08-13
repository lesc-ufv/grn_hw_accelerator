//
// Created by lucas on 11/08/2021.
//

#ifndef GRN_DEFS_H
#define GRN_DEFS_H

#include <acc_config.h>
#include <cmath>
#include <algorithm>

#define print(x) std::cout << (x) << std::endl

#define CEILING(x,y) (((x) + (y) - 1) / (y))
#define MAX(x,y) (x > y ? x : y)
#define STATE_SIZE_BYTES (CEILING(NUM_NOS,8))
#define DATA_IN  (4 + (2 * STATE_SIZE_BYTES)) // size id + size init_state + size end_state
#define DATA_OUT  (4 + 4 + 4 +(STATE_SIZE_BYTES)) // size id + size period + size transient + size state
#define ACC_DATA_WIDTH (MAX(DATA_IN,DATA_OUT))

typedef struct grn_data_t{
    unsigned char data[ACC_DATA_WIDTH];
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


