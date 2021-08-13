TARGET := hw_emu
DEVICE := $(AWS_PLATFORM)
HOST_ARCH = x86

CXXFLAGS += $(opencl_CXXFLAGS) -Wall -O3 -g -std=c++14
LDFLAGS += $(opencl_LDFLAGS)

CXXFLAGS += -I$(shell readlink -f ./include)
LDFLAGS += -lrt -lstdc++ 

CXXFLAGS += -fmessage-length=0 -fPIC

LIB_NAME=grnfpga

SRC_FILES = $(shell find ./src -iname *.cpp)

O_FILES = $(patsubst %.cpp,build/%.o,$(SRC_FILES))

all: check-all lib/lib$(LIB_NAME).so

include opencl.mk
include simconf.mk
include checks.mk


lib/lib$(LIB_NAME).so: $(O_FILES)
	mkdir -p $(@D)
	$(CXX) $^ -shared -Wl,-soname,lib$(LIB_NAME).so -o $@

build/%.o: %.cpp
	mkdir -p $(@D)
	$(CXX) -c $(CXXFLAGS) $< -o $@
	
install: all
	@sudo cp lib/lib$(LIB_NAME).so /usr/local/lib
	@echo Installed at /usr/local/lib/lib$(LIB_NAME).so
	
uninstall:
	rm -rf /usr/local/lib/lib$(LIB_NAME).so

clean:
	rm -rf build lib

CXXFLAGS += -MMD
-include $(shell find build -name "*.d" 2> /dev/null)

