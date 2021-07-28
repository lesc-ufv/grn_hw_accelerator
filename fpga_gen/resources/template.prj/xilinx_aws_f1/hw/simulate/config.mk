
include num_m_axis.mk

$(TEMP_DIR)/$(kernel_name).xo: ../scripts/package_kernel.tcl ../scripts/gen_xo.tcl $(hdl_files)
	mkdir -p "$(TEMP_DIR)"
	$(VIVADO) -mode batch -source ../scripts/gen_xo.tcl -tclargs "$(TEMP_DIR)/$(kernel_name).xo" $(kernel_name) $(TARGET) $(DEVICE) $(XSA) $(NUM_M_AXIS)
	
