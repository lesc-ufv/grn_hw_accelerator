from math import ceil, log2

from veriloggen import *
from fpga_gen.src.hw import grn_accelerator_aws
from fpga_gen.src.hw.grn_accelerator_aws import GrnAccelerator
from fpga_gen.src.hw.utils import initialize_regs


class GrnTestBench:

    def __init__(self, num_networks, grn_functions_file, grn_input_files):
        self.grn_functions_file = grn_functions_file
        self.grn_input_files = grn_input_files
        self.num_networks = num_networks

    # TODO
    def start(self, num_data):
        grn_accelerator = GrnAccelerator(self.num_networks, self.grn_functions_file)
        grn_test_bench = self.create_testbench_sim(grn_accelerator, 1, self.grn_input_files)
        grn_test_bench.to_verilog("grn_test_bench.v")
        sim = simulation.Simulator(grn_test_bench, sim='iverilog')
        rslt = sim.run()
        '''lines = []
        for line in rslt.splitlines():
            if 'ID=' in line:
                line = line.replace(" ", "")
                line = line.replace('ID=', '')
                line = line.split(':')
                lines.append([line[0], line[1]])
        for i in range(cgra_acc.num_out):
            file = correct_directory_path(
                search_a_path("verilog_simul/output_files", paths)) + \
                   str(i) + ".txt"
            content = ""
            counter = 0
            for line in lines:
                if str(i) in line[0]:
                    values = line[1]
                    while len(values) > 0 and counter < tam_input_data:
                        content += values[len(values) - 4:len(values)] + "\n"
                        values = values[0:len(values) - 4]
                        counter += 1
            save_file(file, content, "w")'''

    def create_testbench_sim(self, grn_acc, num_data, files):
        num_in = grn_acc.get_num_in()
        num_out = grn_acc.get_num_out()
        data_producer = self.create_data_producer()
        data_consumer = self.create_data_consumer()

        m = Module('testbench_sim')

        INPUT_INTERFACE_DATA_WIDTH = m.Localparam('INPUT_INTERFACE_DATA_WIDTH', grn_acc.acc_data_in_width)
        OUTPUT_INTERFACE_DATA_WIDTH = m.Localparam('OUTPUT_INTERFACE_DATA_WIDTH', grn_acc.acc_data_out_width)

        clk = m.Reg('clk')
        rst = m.Reg('rst')
        start = m.Reg('start')

        rd_done = m.Wire('rd_done', num_in)
        wr_done = m.Wire('wr_done', num_out)

        rd_request = m.Wire('rd_request', num_in)
        rd_valid = m.Wire('rd_valid', num_in)
        rd_data = m.Wire('rd_data', Mul(INPUT_INTERFACE_DATA_WIDTH, num_in))

        wr_available = m.Wire('wr_available', num_out)
        wr_request = m.Wire('wr_request', num_out)
        wr_data = m.Wire('wr_data', Mul(OUTPUT_INTERFACE_DATA_WIDTH, num_out))

        acc_done = m.Wire('acc_done')

        for i in range(num_in):
            params = [('file', files[i]),
                      ('data_width', INPUT_INTERFACE_DATA_WIDTH),
                      ('num_data', num_data if i == 0 else num_data),
                      ('addr_width', 1 + ceil(log2(num_data if i == 0
                                                   else num_data)))]
            con = [('clk', clk),
                   ('rst', rst),
                   ('rd_request', rd_request[i]),
                   ('read_data_valid', rd_valid[i]),
                   ('rd_done', rd_done[i]),
                   ('read_data', rd_data[Mul(i, INPUT_INTERFACE_DATA_WIDTH):
                                         Mul(i + 1, INPUT_INTERFACE_DATA_WIDTH)])]

            m.Instance(data_producer, 'data_producer_%d' % i, params, con)

        for i in range(num_out):
            params = [('data_width', OUTPUT_INTERFACE_DATA_WIDTH),
                      ('id', i),
                      ('num_data', num_data),
                      ('counter_num_data_width', 1 + ceil(log2(num_data)))]
            con = [('clk', clk),
                   ('rst', rst),
                   ('wr_done', wr_done[i]),
                   ('wr_available', wr_available[i]),
                   ('wr_request', wr_request[i]),
                   ('wr_data', wr_data[Mul(i, OUTPUT_INTERFACE_DATA_WIDTH):
                                       Mul(i + 1, OUTPUT_INTERFACE_DATA_WIDTH)])]
            m.Instance(data_consumer, 'data_consumer_%d' % i, params, con)

        params = []
        con = [('clk', clk), ('rst', rst), ('start', start),
               ('acc_user_done_rd_data', rd_done),
               ('acc_user_done_wr_data', wr_done),
               ('acc_user_request_read', rd_request),
               ('acc_user_read_data_valid', rd_valid),
               ('acc_user_read_data', rd_data),
               ('acc_user_available_write', wr_available),
               ('acc_user_request_write', wr_request),
               ('acc_user_write_data', wr_data),
               ('acc_user_done', acc_done)
               ]
        module = grn_acc.get()

        m.Instance(module, module.name, params, con)

        initialize_regs(m, {'clk': 0, 'rst': 1, 'wr_available': 2 ** num_out - 1})

        simulation.setup_waveform(m)

        m.Initial(
            EmbeddedCode('@(posedge clk);'),
            EmbeddedCode('@(posedge clk);'),
            EmbeddedCode('@(posedge clk);'),
            rst(0),
            start(1),
            Delay(10000), Finish()
        )
        m.EmbeddedCode('always #5clk=~clk;')

        m.Always(Posedge(clk))(
            If(acc_done)(
                # Display('ACC DONE!'),
                Finish()
            )
        )

        return m

    def create_data_producer(self):
        name = 'data_producer'
        # if name in self.cache.keys():
        #    return self.cache[name]
        m = Module(name)
        file = m.Parameter('file', 'file.txt')
        data_width = m.Parameter('data_width', 512)
        num_data = m.Parameter('num_data', 16)
        addr_width = m.Parameter('addr_width', 4)

        # Control signals for the component
        clk = m.Input('clk')
        rst = m.Input('rst')

        # Ports for delivery of data to the consumer
        request_read = m.Input('rd_request')
        read_data_valid = m.OutputReg('read_data_valid')
        read_done = m.OutputReg('rd_done')
        read_data = m.Output('read_data', data_width)

        re = m.Reg('re')
        data_counter = m.Reg('data_counter', addr_width)

        m.EmbeddedCode("\n")

        fsm_produce_data = m.Reg('fsm_produce_data', 2)
        fsm_init = m.Localparam('fsm_init', Int(0, fsm_produce_data.width, 10))
        fsm_produce = m.Localparam('fsm_produce',
                                   Int(1, fsm_produce_data.width, 10))
        fsm_done = m.Localparam('fsm_done', Int(2, fsm_produce_data.width, 10))

        m.EmbeddedCode("\n")

        m.Always(Posedge(clk))(
            If(rst)(
                data_counter(0),
                read_data_valid(Int(0, 1, 10)),
                read_done(Int(0, 1, 10)),
                re(Int(0, 1, 10)),
                fsm_produce_data(fsm_init),
            ).Else(
                Case(fsm_produce_data)(
                    When(fsm_init)(
                        re(Int(1, 1, 10)),
                        fsm_produce_data(fsm_produce)
                    ),
                    When(fsm_produce)(
                        re(Int(0, 1, 10)),
                        read_data_valid(Int(1, 1, 10)),
                        If(request_read)(
                            re(Int(1, 1, 10)),
                            data_counter(data_counter + 1),
                            read_data_valid(Int(0, 1, 10)),
                        ),
                        If(data_counter == num_data)(
                            read_data_valid(Int(0, 1, 10)),
                            fsm_produce_data(fsm_done)
                        )
                    ),
                    When(fsm_done)(
                        read_done(Int(1, 1, 10))
                    ),
                )
            )
        )
        params = [('init_file', file), ('data_width', data_width),
                  ('addr_width', addr_width)]
        con = [('clk', clk),
               ('we', Int(0, 1, 2)),
               ('re', re),
               ('raddr', data_counter),
               ('waddr', data_counter),
               ('din', Repeat(Int(0, 1, 2), data_width)),
               ('dout', read_data)]
        mem = self.create_memory()
        m.Instance(mem, 'mem_rom', params, con)

        initialize_regs(m)
        # self.cache[name] = m

        return m

    def create_data_consumer(self):
        name = 'data_consumer'
        # if name in self.cache.keys():
        #    return self.cache[name]
        m = Module(name)
        id = m.Parameter('id', 0)
        data_width = m.Parameter('data_width', 512)
        num_data = m.Parameter('num_data', 16)
        counter_num_data_width = m.Parameter('counter_num_data_width', 4)

        # Control signals for the component
        clk = m.Input('clk')
        rst = m.Input('rst')

        # comunication buses for the cgra output data
        wr_available = m.OutputReg('wr_available')
        wr_request = m.Input('wr_request')
        wr_data = m.Input('wr_data', data_width)
        wr_done = m.OutputReg('wr_done')

        counter = m.Reg('counter', counter_num_data_width)

        m.Always(Posedge(clk))(
            If(rst)(
                counter(0),
                wr_done(Int(0, 1, 10)),
                wr_available(Int(0, wr_available.width, 10)),
            ).Else(
                wr_available(Int(1, wr_available.width, 10)),
                If(And(wr_request, Not(wr_done)))(
                    Display("ID=%d:%h", id, wr_data),
                    counter(counter + 1),
                ),
                If(counter == num_data)(
                    wr_done(Int(1, 1, 10)),
                    wr_available(Int(0, wr_available.width, 10)),
                )
            )
        )

        initialize_regs(m)
        # self.cache[name] = m

        return m

    def create_memory(self):
        name = 'memory'
        # if name in self.cache.keys():
        #    return self.cache[name]

        m = Module(name)
        init_file = m.Parameter('init_file', 'mem_file.txt')
        data_width = m.Parameter('data_width', 32)
        addr_width = m.Parameter('addr_width', 8)

        clk = m.Input('clk')

        we = m.Input('we')
        re = m.Input('re')

        raddr = m.Input('raddr', addr_width)
        waddr = m.Input('waddr', addr_width)
        din = m.Input('din', data_width)
        dout = m.OutputReg('dout', data_width)

        m.EmbeddedCode('(* ramstyle = "AUTO, no_rw_check" *) reg  [data_width-1:0] mem[0:2**addr_width-1];')
        m.EmbeddedCode('/*')
        mem = m.Reg('mem', data_width, Power(2, addr_width))
        m.EmbeddedCode('*/')

        m.Always(Posedge(clk))(
            If(we)(
                mem[waddr](din)
            ),
            If(re)(
                dout(mem[raddr])
            )
        )
        m.EmbeddedCode('//synthesis translate_off')

        i = m.Integer('i')
        m.Initial(
            dout(0),
            For(i(0), i < Power(2, addr_width), i.inc())(
                mem[i](0)
            ),
            Systask('readmemh', init_file, mem)
        )
        m.EmbeddedCode('//synthesis translate_on')
        # self.cache[name] = m
        return m


grn_path = '/home/jeronimo/Documentos/GIT/grn_hw_accelerator/benchmarks/Benchmark_5.txt'
grn_input_path = '/home/jeronimo/Documentos/GIT/grn_hw_accelerator/benchmarks/Benchmark_5_simul_input.txt'

grn_test_bench = GrnTestBench(1, grn_path, [grn_input_path])
grn_test_bench.start(1)
