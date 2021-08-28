# NVCC compiler options:
NVCC=nvcc
NVCC_FLAGS= -std=c++14
NVCC_LIBS=

main.exe: main.o
	$(NVCC) $(NVCC_FLAGS) main.o -o $@ $(NVCC_LIBS)
	@$(RM) main.o

main.o:
	$(NVCC) $(NVCC_FLAGS) -c main.cu -o $@ $(NVCC_LIBS) -I"./"
# Clean objects in object directory.
clean:
	$(RM) main.exe


