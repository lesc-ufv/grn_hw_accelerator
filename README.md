# An open-source cloud-fpga gene regulatory accelerator

### Abstract:
<p align="justify">
FPGAs are suitable to speed up gene regulatory network (GRN) algorithms with high throughput and energy efficiency. In addition, virtualizing FPGA using hardware generators and cloud resources increases the computing ability to achieve on-demand accelerations across multiple users. Recently, Amazon AWS provides high-performance Cloud's FPGAs. This work proposes an open source accelerator generator for Boolean gene regulatory networks. The generator automatically creates all hardware and software pieces from a high-level GRN description. We evaluate the accelerator performance and cost for CPU, GPU, and Cloud FPGA implementations by considering six GRN models proposed in the literature. As a result, the FPGA accelerator is at least 12x faster than the best GPU accelerator. Furthermore, the FPGA reaches the best performance per dollar in cloud services, at least 5x better than the best GPU accelerator.
</p>

### Cite this:

```
@inproceedings{wscad,
 author = {Lucas Bragança and Jeronimo Penha and Michael Canesche and Dener Ribeiro and José Nacif and Ricardo Ferreira},
 title = {An Open-Source Cloud-FPGA Gene Regulatory Accelerator},
 booktitle = {Anais do XXII Simpósio em Sistemas Computacionais de Alto Desempenho},
 location = {Belo Horizonte},
 year = {2021},
 keywords = {},
 issn = {0000-0000},
 pages = {240--251},
 publisher = {SBC},
 address = {Porto Alegre, RS, Brasil},
 doi = {10.5753/wscad.2021.18527},
 url = {https://sol.sbc.org.br/index.php/wscad/article/view/18527}
}

```
### Usage:

```
python3 create_project.py -g <GRN descrition file> -c <Copies> -n <Project Name> -o <Project location>
```

### Dependencies

- [Python 3](https://www.python.org/downloads/)
- [Veriloggen](https://github.com/PyHDI/veriloggen) 


