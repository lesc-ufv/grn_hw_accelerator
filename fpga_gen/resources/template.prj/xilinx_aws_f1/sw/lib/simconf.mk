DEBUG_MODE:=batch 
simconf:
	@echo "[Emulation]\n\tdebug_mode=$(DEBUG_MODE)\n\tuser_pre_sim_script=$(PWD)/xsim.tcl\n[Debug]\n\tprofile=true\n\ttimeline_trace=true\n\tdata_transfer_trace=fine" > xrt.ini

	@echo "log_wave -recursive *" > xsim.tcl
