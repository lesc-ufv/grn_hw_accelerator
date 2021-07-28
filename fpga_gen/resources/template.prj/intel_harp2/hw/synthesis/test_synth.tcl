# Copyright (C) 1991-2016 Altera Corporation. All rights reserved.
# Your use of Altera Corporation's design tools, logic functions 
# and other software and tools, and its AMPP partner logic 
# functions, and any output files from any of the foregoing 
# (including device programming or simulation files), and any 
# associated documentation or information are expressly subject 
# to the terms and conditions of the Altera Program License 
# Subscription Agreement, the Altera Quartus Prime License Agreement,
# the Altera MegaCore Function License Agreement, or other 
# applicable license agreement, including, without limitation, 
# that your use is for the sole purpose of programming logic 
# devices manufactured by Altera and sold by Altera or its 
# authorized distributors.  Please refer to the applicable 
# agreement for further details.

# Quartus Prime: Generate Tcl File for Project
# File: test_synth.tcl
# Generated on: Thu Sep 20 15:38:06 2018

# Load Quartus Prime Tcl Project package
package require ::quartus::project

set need_to_close_project 0
set make_assignments 1

# Check that the right project is open
if {[is_project_open]} {
	if {[string compare $quartus(project) "test_synth"]} {
		puts "Project test_synth is not open"
		set make_assignments 0
	}
} else {
	# Only open if not already open
	if {[project_exists test_synth]} {
		project_open -revision test_synth test_synth
	} else {
		project_new -revision test_synth test_synth
	}
	set need_to_close_project 1
}

# Make assignments
if {$make_assignments} {
	set_global_assignment -name EDA_GENERATE_FUNCTIONAL_NETLIST ON -section_id eda_simulation
	set_global_assignment -name FAMILY "Arria 10"
	set_global_assignment -name DEVICE 10AX115U3F45E2SGE3
	set_global_assignment -name ERROR_CHECK_FREQUENCY_DIVISOR 256
	set_global_assignment -name DEVICE_FILTER_PACKAGE FBGA
	set_global_assignment -name DEVICE_FILTER_PIN_COUNT 1932
	set_global_assignment -name DEVICE_FILTER_SPEED_GRADE 2
	set_global_assignment -name VERILOG_INPUT_VERSION SYSTEMVERILOG_2005
	set_global_assignment -name VERILOG_SHOW_LMF_MAPPING_MESSAGES OFF
	set_global_assignment -name MIN_CORE_JUNCTION_TEMP 0
	set_global_assignment -name MAX_CORE_JUNCTION_TEMP 100
	set_global_assignment -name PROJECT_OUTPUT_DIRECTORY output_files
	set_global_assignment -name AUTO_RESERVE_CLKUSR_FOR_CALIBRATION OFF
	set_global_assignment -name SEED 0
	set_global_assignment -name ALLOW_ANY_RAM_SIZE_FOR_RECOGNITION ON
	set_global_assignment -name OPTIMIZATION_TECHNIQUE SPEED
	set_global_assignment -name SYNTH_TIMING_DRIVEN_SYNTHESIS ON
	set_global_assignment -name ADD_PASS_THROUGH_LOGIC_TO_INFERRED_RAMS OFF
	set_global_assignment -name USE_HIGH_SPEED_ADDER ON
	set_global_assignment -name TIMEQUEST_MULTICORNER_ANALYSIS ON
	set_global_assignment -name OPTIMIZE_HOLD_TIMING "ALL PATHS"
	set_global_assignment -name OPTIMIZE_MULTI_CORNER_TIMING ON
	set_global_assignment -name ROUTER_TIMING_OPTIMIZATION_LEVEL MAXIMUM
	set_global_assignment -name FITTER_EFFORT "STANDARD FIT"
	set_global_assignment -name ROUTER_LCELL_INSERTION_AND_LOGIC_DUPLICATION ON
	set_global_assignment -name QII_AUTO_PACKED_REGISTERS NORMAL
	set_global_assignment -name MUX_RESTRUCTURE ON
	set_global_assignment -name ADV_NETLIST_OPT_SYNTH_WYSIWYG_REMAP ON
	set_global_assignment -name OPTIMIZATION_MODE "HIGH PERFORMANCE EFFORT"
	set_global_assignment -name INI_VARS "hdd_disable_top_hub=on"
	set_global_assignment -name ENABLE_OCT_DONE OFF
	set_global_assignment -name USE_CONFIGURATION_DEVICE ON
	set_global_assignment -name CRC_ERROR_OPEN_DRAIN OFF
	set_global_assignment -name INTERNAL_SCRUBBING ON
	set_global_assignment -name OUTPUT_IO_TIMING_NEAR_END_VMEAS "HALF VCCIO" -rise
	set_global_assignment -name OUTPUT_IO_TIMING_NEAR_END_VMEAS "HALF VCCIO" -fall
	set_global_assignment -name OUTPUT_IO_TIMING_FAR_END_VMEAS "HALF SIGNAL SWING" -rise
	set_global_assignment -name OUTPUT_IO_TIMING_FAR_END_VMEAS "HALF SIGNAL SWING" -fall
	set_global_assignment -name ACTIVE_SERIAL_CLOCK FREQ_100MHZ
	set_global_assignment -name VCCT_L_USER_VOLTAGE 0.9V
	set_global_assignment -name VCCT_R_USER_VOLTAGE 0.9V
	set_global_assignment -name VCCR_L_USER_VOLTAGE 0.9V
	set_global_assignment -name VCCR_R_USER_VOLTAGE 0.9V
	set_global_assignment -name VCCA_L_USER_VOLTAGE 1.8V
	set_global_assignment -name VCCA_R_USER_VOLTAGE 1.8V
	set_global_assignment -name LAST_QUARTUS_VERSION 16.0.0
	set_global_assignment -name ALLOW_REGISTER_MERGING OFF
	set_global_assignment -name POWER_PRESET_COOLING_SOLUTION "23 MM HEAT SINK WITH 200 LFPM AIRFLOW"
	set_global_assignment -name POWER_BOARD_THERMAL_MODEL "NONE (CONSERVATIVE)"
	set_global_assignment -name VERILOG_FILE omega1024x1024/omega1024x1024_4.v
	set_global_assignment -name VERILOG_FILE omega1024x1024/mux_reg4x1.v
	set_global_assignment -name VERILOG_FILE omega1024x1024/switch_box4x4.v
	set_global_assignment -name SDC_FILE test_synth.sdc
	set_global_assignment -name VERILOG_FILE test_synth.v
	set_location_assignment PIN_E19 -to clk
	set_location_assignment PIN_J22 -to rst
	set_location_assignment PIN_H22 -to din[0]
	set_location_assignment PIN_H23 -to din[1]
	set_location_assignment PIN_H24 -to din[2]
	set_location_assignment PIN_H26 -to din[3]
	set_location_assignment PIN_G20 -to dout[0]
	set_location_assignment PIN_G21 -to dout[1]
	set_location_assignment PIN_G23 -to dout[2]
	set_location_assignment PIN_G24 -to dout[3]

	# Commit assignments
	export_assignments

	# Close project
	if {$need_to_close_project} {
		project_close
	}
}
