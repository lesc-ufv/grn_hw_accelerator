#!/bin/bash

init_time=$(date +%s)

quartus_ipgenerate test_synth -c test_synth --run_default_mode_op
quartus_syn --read_settings_files=off --write_settings_files=off test_synth -c test_synth
quartus_fit --read_settings_files=off --write_settings_files=off test_synth -c test_synth
quartus_asm --read_settings_files=off --write_settings_files=off test_synth -c test_synth
quartus_sta test_synth -c test_synth

end_time=$(date +%s)
diff=$(expr $end_time - $init_time)
result=$(expr 10800 + $diff)
time=$(date -d @$result +%H:%M:%S)
echo "Total time spend: $time " >time_spend.txt
