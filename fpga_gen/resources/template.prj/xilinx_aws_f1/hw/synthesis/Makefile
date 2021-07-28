
kernel_name = $(shell cat ./prj_name)

hdl_files=$(shell find ../src/ -iname *.v)
hdl_files+=$(shell find ../src/ -iname *.sv)

HOST_ARCH := x86
VPP := v++
VIVADO := $(XILINX_VIVADO)/bin/vivado
TARGET := hw
DEVICE := $(AWS_PLATFORM)

PROFILE := no
DEBUG := no

#Generates profile summary report
ifeq ($(PROFILE), yes)
LDCLFLAGS += --profile_kernel data:all:all:all
endif

#Generates debug summary report
ifeq ($(DEBUG), yes)
LDCLFLAGS += --dk list_ports
endif

CLFLAGS += -t $(TARGET) --platform $(DEVICE) --save-temps --config vitis_config.txt
PACKAGE_OUT = ./package.$(TARGET)
device2xsa = $(strip $(patsubst %.xpfm, % , $(shell basename $(DEVICE))))

XSA := $(call device2xsa, $(DEVICE))
TEMP_DIR := ./_x.$(TARGET).$(XSA)
BUILD_DIR := ./build_dir.$(TARGET).$(XSA)

BINARY_CONTAINERS += $(BUILD_DIR)/$(kernel_name).xclbin
BINARY_CONTAINER_kernel_rtl_OBJS += $(TEMP_DIR)/$(kernel_name).xo

.PHONY: first
first: build

include checks.mk
include config.mk
include aws.mk

.PHONY: build
build: check-vitis $(BINARY_CONTAINERS)

$(BUILD_DIR)/$(kernel_name).xclbin: $(BINARY_CONTAINER_kernel_rtl_OBJS)
	mkdir -p $(BUILD_DIR)
ifeq ($(HOST_ARCH), x86)
	$(VPP) -l $(LDCLFLAGS) $(CLFLAGS) --temp_dir $(BUILD_DIR)  -o'$(BUILD_DIR)/$(kernel_name).link.xclbin' $(+)
	$(VPP) -p $(BUILD_DIR)/$(kernel_name).link.xclbin -t $(TARGET) --platform $(DEVICE) --package.out_dir $(PACKAGE_OUT) -o $(BUILD_DIR)/$(kernel_name).xclbin
else
	$(VPP) -l $(LDCLFLAGS) $(CLFLAGS) --temp_dir $(BUILD_DIR) -o'$(BUILD_DIR)/$(kernel_name).xclbin' $(+)
endif

.PHONY: cleanall
cleanall: cleanlog cleanaws
	rm -rf $(TEMP_DIR)
	rm -rf $(BUILD_DIR) 
	rm -rf $(PACKAGE_OUT)
	rm -rf ./tmp_kernel_pack* 
	rm -rf ./packaged_kernel*
	rm -rf _x
	rm -rf .ipcache
	rm -rf .Xil

.PHONY: cleanlog
cleanlog:
	rm -rf *.log 
	rm -rf *.jou 
