from veriloggen import *

from src.hw.utils import initialize_regs, bits


class AccAXIInterface:
    def __init__(self, accelerator):
        self.acc = accelerator
        self.cache = {}

    def get_connectivity_config(self, name):
        num_m_axis = self.acc.get_num_in()
        num_ddr = min(num_m_axis, 4)
        sp = '[connectivity]\n'
        ddr = [i % num_ddr for i in range(num_m_axis)]
        ddr.sort()
        for axi in range(num_m_axis):
            sp += 'sp=%s_1.in%d:DDR[%d]\n' % (name, axi, ddr[axi])
            sp += 'sp=%s_1.out%d:DDR[%d]\n' % (name, axi, ddr[axi])

        return sp

    def create_app_top(self):
        num_m_axis = self.acc.get_num_in()

        name = 'app_top'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        C_M_AXI_ADDR_WIDTH = m.Parameter('C_M_AXI_ADDR_WIDTH', 64)
        C_M_AXI_DATA_WIDTH = m.Parameter('C_M_AXI_DATA_WIDTH', self.acc.axi_bus_data_width)

        ap_clk = m.Input('ap_clk')
        ap_rst_n = m.Input('ap_rst_n')

        m_axis_signals = {}
        for i in range(num_m_axis):
            n = '%02d' % i
            m_axis_signals['m%s_axi_awvalid' % n] = m.Output('m%s_axi_awvalid' % n)
            m_axis_signals['m%s_axi_awready' % n] = m.Input('m%s_axi_awready' % n)
            m_axis_signals['m%s_axi_awaddr' % n] = m.Output('m%s_axi_awaddr' % n, C_M_AXI_ADDR_WIDTH)
            m_axis_signals['m%s_axi_awlen' % n] = m.Output('m%s_axi_awlen' % n, 8)
            m_axis_signals['m%s_axi_wvalid' % n] = m.Output('m%s_axi_wvalid' % n)
            m_axis_signals['m%s_axi_wready' % n] = m.Input('m%s_axi_wready' % n)
            m_axis_signals['m%s_axi_wdata' % n] = m.Output('m%s_axi_wdata' % n, C_M_AXI_DATA_WIDTH)
            m_axis_signals['m%s_axi_wstrb' % n] = m.Output('m%s_axi_wstrb' % n, Div(C_M_AXI_DATA_WIDTH, 8))
            m_axis_signals['m%s_axi_wlast' % n] = m.Output('m%s_axi_wlast' % n)
            m_axis_signals['m%s_axi_bvalid' % n] = m.Input('m%s_axi_bvalid' % n)
            m_axis_signals['m%s_axi_bready' % n] = m.Output('m%s_axi_bready' % n)
            m_axis_signals['m%s_axi_arvalid' % n] = m.Output('m%s_axi_arvalid' % n)
            m_axis_signals['m%s_axi_arready' % n] = m.Input('m%s_axi_arready' % n)
            m_axis_signals['m%s_axi_araddr' % n] = m.Output('m%s_axi_araddr' % n, C_M_AXI_ADDR_WIDTH)
            m_axis_signals['m%s_axi_arlen' % n] = m.Output('m%s_axi_arlen' % n, 8)
            m_axis_signals['m%s_axi_rvalid' % n] = m.Input('m%s_axi_rvalid' % n)
            m_axis_signals['m%s_axi_rready' % n] = m.Output('m%s_axi_rready' % n)
            m_axis_signals['m%s_axi_rdata' % n] = m.Input('m%s_axi_rdata' % n, C_M_AXI_DATA_WIDTH)
            m_axis_signals['m%s_axi_rlast' % n] = m.Input('m%s_axi_rlast' % n)

        ap_start = m.Input('ap_start')
        ap_idle = m.Output('ap_idle')
        ap_done = m.Output('ap_done')
        ap_ready = m.Output('ap_ready')

        vin_s = [m.Input('in_s%d' % i, 32) for i in range(num_m_axis)]
        vout_s = [m.Input('out_s%d' % i, 32) for i in range(num_m_axis)]
        viin = []
        vout = []
        for i in range(num_m_axis):
            viin.append(m.Input('in%d' % i, 64))
            vout.append(m.Input('out%d' % i, 64))

        LP_NUM_EXAMPLES = m.Localparam('LP_NUM_EXAMPLES', num_m_axis)
        LP_RD_MAX_OUTSTANDING = m.Localparam('LP_RD_MAX_OUTSTANDING', 16)
        LP_WR_MAX_OUTSTANDING = m.Localparam('LP_WR_MAX_OUTSTANDING', 16)

        m.EmbeddedCode('(* KEEP = "yes" *)')
        reset = m.Reg('reset')
        ap_idle_r = m.Reg('ap_idle_r')
        ap_done_r = m.Reg('ap_done_r')

        rd_ctrl_done = m.Wire('rd_ctrl_done', LP_NUM_EXAMPLES)
        wr_ctrl_done = m.Wire('wr_ctrl_done', LP_NUM_EXAMPLES)

        acc_user_done_rd_data = m.Reg('acc_user_done_rd_data', LP_NUM_EXAMPLES)
        acc_user_done_wr_data = m.Reg('acc_user_done_wr_data', LP_NUM_EXAMPLES)

        acc_user_request_read = m.Wire('acc_user_request_read', LP_NUM_EXAMPLES)
        acc_user_read_data_valid = m.Wire('acc_user_read_data_valid', LP_NUM_EXAMPLES)
        acc_user_read_data = m.Wire('acc_user_read_data', Mul(C_M_AXI_DATA_WIDTH, LP_NUM_EXAMPLES))

        acc_user_available_write = m.Wire('acc_user_available_write', LP_NUM_EXAMPLES)
        acc_user_request_write = m.Wire('acc_user_request_write', LP_NUM_EXAMPLES)
        acc_user_write_data = m.Wire('acc_user_write_data', Mul(C_M_AXI_DATA_WIDTH, LP_NUM_EXAMPLES))

        acc_user_done = m.Wire('acc_user_done')

        rd_tvalid = {}
        rd_tready = {}
        rd_tlast = {}
        rd_tdata = {}
        for i in range(num_m_axis):
            n = 'rd_tvalid%d' % i
            rd_tvalid[n] = m.Wire(n)
            n = 'rd_tready%d' % i
            rd_tready[n] = m.Wire(n)
            n = 'rd_tlast%d' % i
            rd_tlast[n] = m.Wire(n)
            n = 'rd_tdata%d' % i
            rd_tdata[n] = m.Wire(n, C_M_AXI_DATA_WIDTH)

        wr_tvalid = {}
        wr_tready = {}
        wr_tdata = {}
        for i in range(num_m_axis):
            n = 'wr_tvalid%d' % i
            wr_tvalid[n] = m.Wire(n)
            n = 'wr_tready%d' % i
            wr_tready[n] = m.Wire(n)
            n = 'wr_tdata%d' % i
            wr_tdata[n] = m.Wire(n, C_M_AXI_DATA_WIDTH)

        fsm_reset = m.Reg('fsm_reset', 2)
        areset = m.Reg('areset')
        ap_start_pulse = m.Reg('ap_start_pulse')
        FSM_STATE_START = m.Localparam('FSM_STATE_START', Int(0, 2, 2))
        FSM_STATE_RESET = m.Localparam('FSM_STATE_RESET', Int(1, 2, 2))
        FSM_STATE_RUNNING = m.Localparam('FSM_STATE_RUNNING', Int(2, 2, 2))

        m.Always(Posedge(ap_clk))(
            reset(~ap_rst_n)
        )

        m.Always(Posedge(ap_clk))(
            If(reset)(
                areset(Int(0, 1, 2)),
                fsm_reset(FSM_STATE_START),
                ap_start_pulse(Int(0, 1, 2))
            ).Else(
                areset(Int(0, 1, 2)),
                ap_start_pulse(Int(0, 1, 2)),
                Case(fsm_reset)(
                    When(FSM_STATE_START)(
                        If(ap_start)(
                            areset(Int(1, 1, 2)),
                            fsm_reset(FSM_STATE_RESET)
                        )
                    ),
                    When(FSM_STATE_RESET)(
                        ap_start_pulse(Int(1, 1, 2)),
                        fsm_reset(FSM_STATE_RUNNING)
                    ),
                    When(FSM_STATE_RUNNING)(
                        If(~ap_start)(
                            fsm_reset(FSM_STATE_START)
                        )
                    )
                )
            )
        )
        m.Always(Posedge(ap_clk))(
            If(areset)(
                ap_idle_r(Int(1, 1, 2))
            ).Else(
                ap_idle_r(Mux(ap_done, Int(1, 1, 2), Mux(ap_start_pulse, Int(0, 1, 2), ap_idle)))
            )
        )
        ap_idle.assign(ap_idle_r)

        m.Always(Posedge(ap_clk))(
            If(areset)(
                ap_done_r(Int(0, 1, 2))
            ).Else(
                ap_done_r(Mux(ap_done, Int(0, 1, 2), Or(ap_done_r, acc_user_done)))
            )
        )
        ap_done.assign(ap_done_r)
        ap_ready.assign(ap_done)

        ii = m.Integer('i')
        m.Always(Posedge(ap_clk))(
            If(areset)(
                acc_user_done_rd_data(Repeat(Int(0, 1, 2), LP_NUM_EXAMPLES)),
                acc_user_done_wr_data(Repeat(Int(0, 1, 2), LP_NUM_EXAMPLES)),
            ).Else(
                For(ii(0), ii < LP_NUM_EXAMPLES, ii.inc())(
                    acc_user_done_rd_data[ii](Mux(rd_ctrl_done[ii], Int(1, 1, 2), acc_user_done_rd_data[ii])),
                    acc_user_done_wr_data[ii](Mux(wr_ctrl_done[ii], Int(1, 1, 2), acc_user_done_wr_data[ii])),
                )
            )
        )

        rd_data_code = "{" + "".join(['rd_tdata%d,' % i for i in reversed(range(num_m_axis))])[:-1] + "}"
        rd_valid_code = "{" + "".join(['rd_tvalid%d,' % i for i in reversed(range(num_m_axis))])[:-1] + "}"
        wr_tready_code = "{" + "".join(['wr_tready%d,' % i for i in reversed(range(num_m_axis))])[:-1] + "}"

        for i in range(num_m_axis):
            rd_tready['rd_tready%d' % i].assign(acc_user_request_read[i])

        acc_user_read_data_valid.assign(EmbeddedCode(rd_valid_code)),
        acc_user_read_data.assign(EmbeddedCode(rd_data_code))

        m.EmbeddedCode('')

        acc_user_available_write.assign(EmbeddedCode(wr_tready_code))
        for i in range(num_m_axis):
            wr_tvalid['wr_tvalid%d' % i].assign(acc_user_request_write[i])
            wr_tdata['wr_tdata%d' % i].assign(
                acc_user_write_data[Mul(i, C_M_AXI_DATA_WIDTH):Mul((i + 1), C_M_AXI_DATA_WIDTH)])

        axi_reader = self.create_axi_reader_wrapper()
        axi_writer = self.create_axi_writer_wrapper()
        for i in range(num_m_axis):
            n = '%02d' % i
            param = [('C_M_AXI_ADDR_WIDTH', C_M_AXI_ADDR_WIDTH),
                     ('C_M_AXI_DATA_WIDTH', C_M_AXI_DATA_WIDTH),
                     ('C_XFER_SIZE_WIDTH', 32),
                     ('C_MAX_OUTSTANDING', LP_RD_MAX_OUTSTANDING),
                     ('C_INCLUDE_DATA_FIFO', 1)
                     ]
            con = [('aclk', ap_clk),
                   ('areset', areset),
                   ('ctrl_start', ap_start_pulse),
                   ('ctrl_done', rd_ctrl_done[i]),
                   ('ctrl_addr_offset', viin[i]),
                   ('ctrl_xfer_size_in_bytes', vin_s[i]),
                   ('m_axi_arvalid', m_axis_signals['m%s_axi_arvalid' % n]),
                   ('m_axi_arready', m_axis_signals['m%s_axi_arready' % n]),
                   ('m_axi_araddr', m_axis_signals['m%s_axi_araddr' % n]),
                   ('m_axi_arlen', m_axis_signals['m%s_axi_arlen' % n]),
                   ('m_axi_rvalid', m_axis_signals['m%s_axi_rvalid' % n]),
                   ('m_axi_rready', m_axis_signals['m%s_axi_rready' % n]),
                   ('m_axi_rdata', m_axis_signals['m%s_axi_rdata' % n]),
                   ('m_axi_rlast', m_axis_signals['m%s_axi_rlast' % n]),
                   ('m_axis_aclk', ap_clk),
                   ('m_axis_areset', areset),
                   ('m_axis_tvalid', rd_tvalid['rd_tvalid%d' % i]),
                   ('m_axis_tready', rd_tready['rd_tready%d' % i]),
                   ('m_axis_tlast', rd_tlast['rd_tlast%d' % i]),
                   ('m_axis_tdata', rd_tdata['rd_tdata%d' % i])
                   ]
            m.Instance(axi_reader, 'axi_reader_%d' % i, param, con)

        for i in range(num_m_axis):
            n = '%02d' % i
            param = [('C_M_AXI_ADDR_WIDTH', C_M_AXI_ADDR_WIDTH),
                     ('C_M_AXI_DATA_WIDTH', C_M_AXI_DATA_WIDTH),
                     ('C_XFER_SIZE_WIDTH', 32),
                     ('C_MAX_OUTSTANDING', LP_WR_MAX_OUTSTANDING),
                     ('C_INCLUDE_DATA_FIFO', 1)]
            con = [
                ('aclk', ap_clk),
                ('areset', areset),
                ('ctrl_start', ap_start_pulse),
                ('ctrl_done', wr_ctrl_done[i]),
                ('ctrl_addr_offset', vout[i]),
                ('ctrl_xfer_size_in_bytes', vout_s[i]),
                ('m_axi_awvalid', m_axis_signals['m%s_axi_awvalid' % n]),
                ('m_axi_awready', m_axis_signals['m%s_axi_awready' % n]),
                ('m_axi_awaddr', m_axis_signals['m%s_axi_awaddr' % n]),
                ('m_axi_awlen', m_axis_signals['m%s_axi_awlen' % n]),
                ('m_axi_wvalid', m_axis_signals['m%s_axi_wvalid' % n]),
                ('m_axi_wready', m_axis_signals['m%s_axi_wready' % n]),
                ('m_axi_wdata', m_axis_signals['m%s_axi_wdata' % n]),
                ('m_axi_wstrb', m_axis_signals['m%s_axi_wstrb' % n]),
                ('m_axi_wlast', m_axis_signals['m%s_axi_wlast' % n]),
                ('m_axi_bvalid', m_axis_signals['m%s_axi_bvalid' % n]),
                ('m_axi_bready', m_axis_signals['m%s_axi_bready' % n]),
                ('s_axis_aclk', ap_clk),
                ('s_axis_areset', areset),
                ('s_axis_tvalid', wr_tvalid['wr_tvalid%d' % i]),
                ('s_axis_tready', wr_tready['wr_tready%d' % i]),
                ('s_axis_tdata', wr_tdata['wr_tdata%d' % i])
            ]
            m.Instance(axi_writer, 'axi_writer_%d' % i, param, con)

        param = []
        con = [
            ('clk', ap_clk),
            ('rst', areset),
            ('start', ap_start_pulse),
            ('acc_user_done_rd_data', acc_user_done_rd_data),
            ('acc_user_done_wr_data', acc_user_done_wr_data),
            ('acc_user_request_read', acc_user_request_read),
            ('acc_user_read_data_valid', acc_user_read_data_valid),
            ('acc_user_read_data', acc_user_read_data),
            ('acc_user_available_write', acc_user_available_write),
            ('acc_user_request_write', acc_user_request_write),
            ('acc_user_write_data', acc_user_write_data),
            ('acc_user_done', acc_user_done)
        ]

        m.Instance(self.acc.get(), 'acc', param, con)

        initialize_regs(m, {'ap_idle_r': Int(1, 1, 2), 'areset': Int(1, 1, 2), 'reset': Int(1, 1, 2),
                            'fsm_reset': FSM_STATE_START})
        self.cache[name] = m

        return m

    def create_kernel_top(self, name):
        num_m_axis = self.acc.get_num_in()

        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        C_S_AXI_CONTROL_ADDR_WIDTH = m.Parameter('C_S_AXI_CONTROL_ADDR_WIDTH', 12)
        C_S_AXI_CONTROL_DATA_WIDTH = m.Parameter('C_S_AXI_CONTROL_DATA_WIDTH', 32)
        C_M_AXI_ADDR_WIDTH = m.Parameter('C_M_AXI_ADDR_WIDTH', 64)
        C_M_AXI_DATA_WIDTH = m.Parameter('C_M_AXI_DATA_WIDTH', self.acc.axi_bus_data_width)

        ap_clk = m.Input('ap_clk')
        ap_rst_n = m.Input('ap_rst_n')

        s_axi_control_awvalid = m.Input('s_axi_control_awvalid')
        s_axi_control_awready = m.Output('s_axi_control_awready')
        s_axi_control_awaddr = m.Input('s_axi_control_awaddr', C_S_AXI_CONTROL_ADDR_WIDTH)
        s_axi_control_wvalid = m.Input('s_axi_control_wvalid')
        s_axi_control_wready = m.Output('s_axi_control_wready')
        s_axi_control_wdata = m.Input('s_axi_control_wdata', C_S_AXI_CONTROL_DATA_WIDTH)
        s_axi_control_wstrb = m.Input('s_axi_control_wstrb', Div(C_S_AXI_CONTROL_DATA_WIDTH, 8))
        s_axi_control_arvalid = m.Input('s_axi_control_arvalid')
        s_axi_control_arready = m.Output('s_axi_control_arready')
        s_axi_control_araddr = m.Input('s_axi_control_araddr', C_S_AXI_CONTROL_ADDR_WIDTH)
        s_axi_control_rvalid = m.Output('s_axi_control_rvalid')
        s_axi_control_rready = m.Input('s_axi_control_rready')
        s_axi_control_rdata = m.Output('s_axi_control_rdata', C_S_AXI_CONTROL_DATA_WIDTH)
        s_axi_control_rresp = m.Output('s_axi_control_rresp', 2)
        s_axi_control_bvalid = m.Output('s_axi_control_bvalid')
        s_axi_control_bready = m.Input('s_axi_control_bready')
        s_axi_control_bresp = m.Output('s_axi_control_bresp', 2)
        interrupt = m.Output('interrupt')

        m_axis_signals = {}
        for i in range(num_m_axis):
            n = '%02d' % i
            m_axis_signals['m%s_axi_awvalid' % n] = m.Output('m%s_axi_awvalid' % n)
            m_axis_signals['m%s_axi_awready' % n] = m.Input('m%s_axi_awready' % n)
            m_axis_signals['m%s_axi_awaddr' % n] = m.Output('m%s_axi_awaddr' % n, C_M_AXI_ADDR_WIDTH)
            m_axis_signals['m%s_axi_awlen' % n] = m.Output('m%s_axi_awlen' % n, 8)
            m_axis_signals['m%s_axi_wvalid' % n] = m.Output('m%s_axi_wvalid' % n)
            m_axis_signals['m%s_axi_wready' % n] = m.Input('m%s_axi_wready' % n)
            m_axis_signals['m%s_axi_wdata' % n] = m.Output('m%s_axi_wdata' % n, C_M_AXI_DATA_WIDTH)
            m_axis_signals['m%s_axi_wstrb' % n] = m.Output('m%s_axi_wstrb' % n, Div(C_M_AXI_DATA_WIDTH, 8))
            m_axis_signals['m%s_axi_wlast' % n] = m.Output('m%s_axi_wlast' % n)
            m_axis_signals['m%s_axi_bvalid' % n] = m.Input('m%s_axi_bvalid' % n)
            m_axis_signals['m%s_axi_bready' % n] = m.Output('m%s_axi_bready' % n)
            m_axis_signals['m%s_axi_arvalid' % n] = m.Output('m%s_axi_arvalid' % n)
            m_axis_signals['m%s_axi_arready' % n] = m.Input('m%s_axi_arready' % n)
            m_axis_signals['m%s_axi_araddr' % n] = m.Output('m%s_axi_araddr' % n, C_M_AXI_ADDR_WIDTH)
            m_axis_signals['m%s_axi_arlen' % n] = m.Output('m%s_axi_arlen' % n, 8)
            m_axis_signals['m%s_axi_rvalid' % n] = m.Input('m%s_axi_rvalid' % n)
            m_axis_signals['m%s_axi_rready' % n] = m.Output('m%s_axi_rready' % n)
            m_axis_signals['m%s_axi_rdata' % n] = m.Input('m%s_axi_rdata' % n, C_M_AXI_DATA_WIDTH)
            m_axis_signals['m%s_axi_rlast' % n] = m.Input('m%s_axi_rlast' % n)

        m.EmbeddedCode('(* DONT_TOUCH = "yes" *)')
        areset = m.Reg('areset')
        ap_start = m.Wire('ap_start')
        ap_idle = m.Wire('ap_idle')
        ap_done = m.Wire('ap_done')
        ap_ready = m.Wire('ap_ready')
        in_s = [m.Wire('in_s%d' % i, 32) for i in range(num_m_axis)]
        out_s = [m.Wire('out_s%d' % i, 32) for i in range(num_m_axis)]
        iin = []
        out = []
        for i in range(num_m_axis):
            iin.append(m.Wire('in%d' % i, 64))
            out.append(m.Wire('out%d' % i, 64))

        m.Always(Posedge(ap_clk))(
            areset(~ap_rst_n)
        )

        control_s_axi = self.create_control_s_axi(num_m_axis)

        params = [('C_S_AXI_ADDR_WIDTH', C_S_AXI_CONTROL_ADDR_WIDTH),
                  ('C_S_AXI_DATA_WIDTH', C_S_AXI_CONTROL_DATA_WIDTH)]
        con = [('aclk', ap_clk), ('areset', areset), ('aclk_en', Int(1, 1, 2)),
               ('awvalid', s_axi_control_awvalid), ('awready', s_axi_control_awready),
               ('awaddr', s_axi_control_awaddr), ('wvalid', s_axi_control_wvalid),
               ('wready', s_axi_control_wready), ('wdata', s_axi_control_wdata),
               ('wstrb', s_axi_control_wstrb), ('arvalid', s_axi_control_arvalid),
               ('arready', s_axi_control_arready), ('araddr', s_axi_control_araddr),
               ('rvalid', s_axi_control_rvalid), ('rready', s_axi_control_rready),
               ('rdata', s_axi_control_rdata), ('rresp', s_axi_control_rresp),
               ('bvalid', s_axi_control_bvalid), ('bready', s_axi_control_bready),
               ('bresp', s_axi_control_bresp), ('interrupt', interrupt),
               ('ap_start', ap_start), ('ap_done', ap_done),
               ('ap_ready', ap_ready), ('ap_idle', ap_idle)
               ]
        con += [(s.name, s) for s in in_s] + [(s.name, s) for s in out_s]
        for sin, sout in zip(iin, out):
            con.append((sin.name, sin))
            con.append((sout.name, sout))

        m.Instance(control_s_axi, 'control_s_axi_inst', params, con)

        app = self.create_app_top()
        params = [('C_M_AXI_ADDR_WIDTH', C_M_AXI_ADDR_WIDTH),
                  ('C_M_AXI_DATA_WIDTH', C_M_AXI_DATA_WIDTH)]
        con = [('ap_clk', ap_clk), ('ap_rst_n', ap_rst_n), ('ap_start', ap_start), ('ap_done', ap_done),
               ('ap_idle', ap_idle), ('ap_ready', ap_ready)]

        con += [(s.name, s) for s in in_s] + [(s.name, s) for s in out_s]
        for sin, sout in zip(iin, out):
            con.append((sin.name, sin))
            con.append((sout.name, sout))

        con += [(sname, s) for sname, s in m_axis_signals.items()]

        m.Instance(app, 'app_inst', params, con)

        initialize_regs(m, {'areset': Int(1, 1, 2)})
        self.cache[name] = m

        return m

    def create_axi_reader_wrapper(self):
        name = 'axi_reader_wrapper'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        C_M_AXI_ADDR_WIDTH = m.Parameter('C_M_AXI_ADDR_WIDTH', 64)
        C_M_AXI_DATA_WIDTH = m.Parameter('C_M_AXI_DATA_WIDTH', self.acc.axi_bus_data_width)
        C_XFER_SIZE_WIDTH = m.Parameter('C_XFER_SIZE_WIDTH', C_M_AXI_ADDR_WIDTH)
        C_MAX_OUTSTANDING = m.Parameter('C_MAX_OUTSTANDING', 16)
        C_INCLUDE_DATA_FIFO = m.Parameter('C_INCLUDE_DATA_FIFO', 1)

        aclk = m.Input('aclk')
        areset = m.Input('areset')

        ctrl_start = m.Input('ctrl_start')
        ctrl_done = m.Output('ctrl_done')

        ctrl_addr_offset = m.Input('ctrl_addr_offset', C_M_AXI_ADDR_WIDTH)
        ctrl_xfer_size_in_bytes = m.Input('ctrl_xfer_size_in_bytes', C_XFER_SIZE_WIDTH)

        m_axi_arvalid = m.Output('m_axi_arvalid')
        m_axi_arready = m.Input('m_axi_arready')
        m_axi_araddr = m.Output('m_axi_araddr', C_M_AXI_ADDR_WIDTH)
        m_axi_arlen = m.Output('m_axi_arlen', 8)

        m_axi_rvalid = m.Input('m_axi_rvalid')
        m_axi_rready = m.Output('m_axi_rready')
        m_axi_rdata = m.Input('m_axi_rdata', C_M_AXI_DATA_WIDTH)
        m_axi_rlast = m.Input('m_axi_rlast')

        m_axis_aclk = m.Input('m_axis_aclk')
        m_axis_areset = m.Input('m_axis_areset')
        m_axis_tvalid = m.Output('m_axis_tvalid')
        m_axis_tready = m.Input('m_axis_tready')
        m_axis_tdata = m.Output('m_axis_tdata', C_M_AXI_DATA_WIDTH)
        m_axis_tlast = m.Output('m_axis_tlast')

        code = 'axi_reader #(\n\
          .C_M_AXI_ADDR_WIDTH  ( C_M_AXI_ADDR_WIDTH  ) ,\n\
          .C_M_AXI_DATA_WIDTH  ( C_M_AXI_DATA_WIDTH  ) ,\n\
          .C_XFER_SIZE_WIDTH   ( C_XFER_SIZE_WIDTH   ) ,\n\
          .C_MAX_OUTSTANDING   ( C_MAX_OUTSTANDING   ) ,\n\
          .C_INCLUDE_DATA_FIFO ( C_INCLUDE_DATA_FIFO )\n\
        )\n\
        inst_axi_reader (\n\
          .aclk                    ( aclk                   ) ,\n\
          .areset                  ( areset                 ) ,\n\
          .ctrl_start              ( ctrl_start             ) ,\n\
          .ctrl_done               ( ctrl_done              ) ,\n\
          .ctrl_addr_offset        ( ctrl_addr_offset       ) ,\n\
          .ctrl_xfer_size_in_bytes ( ctrl_xfer_size_in_bytes) ,\n\
          .m_axi_arvalid           ( m_axi_arvalid          ) ,\n\
          .m_axi_arready           ( m_axi_arready          ) ,\n\
          .m_axi_araddr            ( m_axi_araddr           ) ,\n\
          .m_axi_arlen             ( m_axi_arlen            ) ,\n\
          .m_axi_rvalid            ( m_axi_rvalid           ) ,\n\
          .m_axi_rready            ( m_axi_rready           ) ,\n\
          .m_axi_rdata             ( m_axi_rdata            ) ,\n\
          .m_axi_rlast             ( m_axi_rlast            ) ,\n\
          .m_axis_aclk             ( m_axis_aclk            ) ,\n\
          .m_axis_areset           ( m_axis_areset          ) ,\n\
          .m_axis_tvalid           ( m_axis_tvalid          ) ,\n\
          .m_axis_tready           ( m_axis_tready          ) ,\n\
          .m_axis_tlast            ( m_axis_tlast           ) ,\n\
          .m_axis_tdata            ( m_axis_tdata           )\n\
        );'
        m.EmbeddedCode(code)

        self.cache[name] = m
        return m

    def create_axi_writer_wrapper(self):
        name = 'axi_writer_wrapper'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        C_M_AXI_ADDR_WIDTH = m.Parameter('C_M_AXI_ADDR_WIDTH', 64)
        C_M_AXI_DATA_WIDTH = m.Parameter('C_M_AXI_DATA_WIDTH', self.acc.axi_bus_data_width)
        C_XFER_SIZE_WIDTH = m.Parameter('C_XFER_SIZE_WIDTH', C_M_AXI_ADDR_WIDTH)
        C_MAX_OUTSTANDING = m.Parameter('C_MAX_OUTSTANDING', 16)
        C_INCLUDE_DATA_FIFO = m.Parameter('C_INCLUDE_DATA_FIFO', 1)

        aclk = m.Input('aclk')
        areset = m.Input('areset')

        ctrl_start = m.Input('ctrl_start')
        ctrl_done = m.Output('ctrl_done')

        ctrl_addr_offset = m.Input('ctrl_addr_offset', C_M_AXI_ADDR_WIDTH)
        ctrl_xfer_size_in_bytes = m.Input('ctrl_xfer_size_in_bytes', C_XFER_SIZE_WIDTH)

        m_axi_awvalid = m.Output('m_axi_awvalid')
        m_axi_awready = m.Input('m_axi_awready')
        m_axi_awaddr = m.Output('m_axi_awaddr', C_M_AXI_ADDR_WIDTH)
        m_axi_awlen = m.Output('m_axi_awlen', 8)

        m_axi_wvalid = m.Output('m_axi_wvalid')
        m_axi_wready = m.Input('m_axi_wready')
        m_axi_wdata = m.Output('m_axi_wdata', C_M_AXI_DATA_WIDTH)
        m_axi_wstrb = m.Output('m_axi_wstrb', Div(C_M_AXI_DATA_WIDTH, 8))
        m_axi_wlast = m.Output('m_axi_wlast')

        m_axi_bvalid = m.Input('m_axi_bvalid')
        m_axi_bready = m.Output('m_axi_bready')

        s_axis_aclk = m.Input('s_axis_aclk')
        s_axis_areset = m.Input('s_axis_areset')
        s_axis_tvalid = m.Input('s_axis_tvalid')
        s_axis_tready = m.Output('s_axis_tready')
        s_axis_tdata = m.Input('s_axis_tdata', C_M_AXI_DATA_WIDTH)

        code = 'axi_writer #(\n\
          .C_M_AXI_ADDR_WIDTH  ( C_M_AXI_ADDR_WIDTH ) ,\n\
          .C_M_AXI_DATA_WIDTH  ( C_M_AXI_DATA_WIDTH ) ,\n\
          .C_XFER_SIZE_WIDTH   ( C_XFER_SIZE_WIDTH  ) ,\n\
          .C_MAX_OUTSTANDING   ( C_MAX_OUTSTANDING  ) ,\n\
          .C_INCLUDE_DATA_FIFO ( C_INCLUDE_DATA_FIFO)\n\
        )\n\
        inst_axi_writer (\n\
          .aclk                    ( aclk                   ) ,\n\
          .areset                  ( areset                 ) ,\n\
          .ctrl_start              ( ctrl_start             ) ,\n\
          .ctrl_done               ( ctrl_done              ) ,\n\
          .ctrl_addr_offset        ( ctrl_addr_offset       ) ,\n\
          .ctrl_xfer_size_in_bytes ( ctrl_xfer_size_in_bytes) ,\n\
          .m_axi_awvalid           ( m_axi_awvalid) ,\n\
          .m_axi_awready           ( m_axi_awready) ,\n\
          .m_axi_awaddr            ( m_axi_awaddr ) ,\n\
          .m_axi_awlen             ( m_axi_awlen  ) ,\n\
          .m_axi_wvalid            ( m_axi_wvalid ) ,\n\
          .m_axi_wready            ( m_axi_wready ) ,\n\
          .m_axi_wdata             ( m_axi_wdata  ) ,\n\
          .m_axi_wstrb             ( m_axi_wstrb  ) ,\n\
          .m_axi_wlast             ( m_axi_wlast  ) ,\n\
          .m_axi_bvalid            ( m_axi_bvalid ) ,\n\
          .m_axi_bready            ( m_axi_bready ) ,\n\
          .s_axis_aclk             ( s_axis_aclk  ) ,\n\
          .s_axis_areset           ( s_axis_areset) ,\n\
          .s_axis_tvalid           (s_axis_tvalid ) ,\n\
          .s_axis_tready           (s_axis_tready ) ,\n\
          .s_axis_tdata            (s_axis_tdata  )\n\
        );'

        m.EmbeddedCode(code)

        self.cache[name] = m
        return m

    def create_control_s_axi(self, num_m_axis):
        n = 4 * (4 + (4 * num_m_axis) + (6 * num_m_axis))
        bits_addr = bits(n)
        values = [Int(i, bits_addr, 16) for i in reversed(range(0, n, 4))]

        name = 'control_s_axi_%d' % num_m_axis
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        C_S_AXI_ADDR_WIDTH = m.Parameter('C_S_AXI_ADDR_WIDTH', bits_addr)
        C_S_AXI_DATA_WIDTH = m.Parameter('C_S_AXI_DATA_WIDTH', 32)

        aclk = m.Input('aclk')
        areset = m.Input('areset')
        aclk_en = m.Input('aclk_en')
        awaddr = m.Input('awaddr', C_S_AXI_ADDR_WIDTH)
        awvalid = m.Input('awvalid')
        awready = m.Output('awready')
        wdata = m.Input('wdata', C_S_AXI_DATA_WIDTH)
        wstrb = m.Input('wstrb', Div(C_S_AXI_DATA_WIDTH, 8))
        wvalid = m.Input('wvalid')
        wready = m.Output('wready')
        bresp = m.Output('bresp', 2)
        bvalid = m.Output('bvalid')
        bready = m.Input('bready')
        araddr = m.Input('araddr', C_S_AXI_ADDR_WIDTH)
        arvalid = m.Input('arvalid')
        arready = m.Output('arready')
        rdata = m.Output('rdata', C_S_AXI_DATA_WIDTH)
        rresp = m.Output('rresp', 2)
        rvalid = m.Output('rvalid')
        rready = m.Input('rready')
        interrupt = m.Output('interrupt')
        ap_start = m.Output('ap_start')
        ap_done = m.Input('ap_done')
        ap_ready = m.Input('ap_ready')
        ap_idle = m.Input('ap_idle')
        in_s = [m.Output('in_s%d' % i, 32) for i in range(num_m_axis)]
        out_s = [m.Output('out_s%d' % i, 32) for i in range(num_m_axis)]
        iin = [m.Output('in%d' % i, 64) for i in range(num_m_axis)]
        out = [m.Output('out%d' % i, 64) for i in range(num_m_axis)]

        ADDR_AP_CTRL = m.Localparam('ADDR_AP_CTRL', values.pop())
        ADDR_GIE = m.Localparam('ADDR_GIE', values.pop())
        ADDR_IER = m.Localparam('ADDR_IER', values.pop())
        ADDR_ISR = m.Localparam('ADDR_ISR', values.pop())
        ADDR_IN_S_DATA = []
        ADDR_IN_S_CTRL = []
        ADDR_OUT_S_DATA = []
        ADDR_OUT_S_CTRL = []
        ADDR_IN_DATA_0 = []
        ADDR_IN_DATA_1 = []
        ADDR_IN_CTRL = []
        ADDR_OUT_DATA_0 = []
        ADDR_OUT_DATA_1 = []
        ADDR_OUT_CTRL = []
        for i in range(num_m_axis):
            ADDR_IN_S_DATA.append(m.Localparam('ADDR_IN_S%d_DATA_0' % i, values.pop()))
            ADDR_IN_S_CTRL.append(m.Localparam('ADDR_IN_S%d_CTRL' % i, values.pop()))

        for i in range(num_m_axis):
            ADDR_OUT_S_DATA.append(m.Localparam('ADDR_OUT_S%d_DATA_0' % i, values.pop()))
            ADDR_OUT_S_CTRL.append(m.Localparam('ADDR_OUT_S%d_CTRL' % i, values.pop()))

        for i in range(num_m_axis):
            ADDR_IN_DATA_0.append(m.Localparam('ADDR_IN%d_DATA_0' % i, values.pop()))
            ADDR_IN_DATA_1.append(m.Localparam('ADDR_IN%d_DATA_1' % i, values.pop()))
            ADDR_IN_CTRL.append(m.Localparam('ADDR_IN%d_CTRL' % i, values.pop()))
            ADDR_OUT_DATA_0.append(m.Localparam('ADDR_OUT%d_DATA_0' % i, values.pop()))
            ADDR_OUT_DATA_1.append(m.Localparam('ADDR_OUT%d_DATA_1' % i, values.pop()))
            ADDR_OUT_CTRL.append(m.Localparam('ADDR_OUT%d_CTRL' % i, values.pop()))

        WRIDLE = m.Localparam('WRIDLE', Int(0, 2, 10))
        WRDATA = m.Localparam('WRDATA', Int(1, 2, 10))
        WRRESP = m.Localparam('WRRESP', Int(2, 2, 10))
        WRRESET = m.Localparam('WRRESET', Int(3, 2, 10))

        RDIDLE = m.Localparam('RDIDLE', Int(0, 2, 10))
        RDDATA = m.Localparam('RDDATA', Int(1, 2, 10))
        RDRESET = m.Localparam('RDRESET', Int(2, 2, 10))
        ADDR_BITS = m.Localparam('ADDR_BITS', bits_addr)

        wstate = m.Reg('wstate', 2)
        wnext = m.Reg('wnext', 2)
        waddr = m.Reg('waddr', ADDR_BITS)
        wmask = m.Wire('wmask', 32)
        aw_hs = m.Wire('aw_hs')
        w_hs = m.Wire('w_hs')
        rstate = m.Reg('rstate', 2)
        rnext = m.Reg('rnext', 2)
        rrdata = m.Reg('rrdata', 32)
        ar_hs = m.Wire('ar_hs')
        raddr = m.Wire('raddr', ADDR_BITS)

        int_ap_idle = m.Reg('int_ap_idle')
        int_ap_ready = m.Reg('int_ap_ready')
        int_ap_done = m.Reg('int_ap_done')
        int_ap_start = m.Reg('int_ap_start')
        int_auto_restart = m.Reg('int_auto_restart')
        int_gie = m.Reg('int_gie')
        int_ier = m.Reg('int_ier', 2)
        int_isr = m.Reg('int_isr', 2)
        int_in_s = [m.Reg('int_in_s%d' % i, 32) for i in range(num_m_axis)]
        int_out_s = [m.Reg('int_out_s%d' % i, 32) for i in range(num_m_axis)]
        int_in = []
        int_out = []
        for i in range(num_m_axis):
            int_in.append(m.Reg('int_in%d' % i, 64))
            int_out.append(m.Reg('int_out%d' % i, 64))

        awready.assign(wstate == WRIDLE)
        wready.assign(wstate == WRDATA)
        bresp.assign(Int(0, 2, 2))
        bvalid.assign(wstate == WRRESP)
        wmask.assign(Cat(Repeat(wstrb[3], 8), Repeat(wstrb[2], 8), Repeat(wstrb[1], 8), Repeat(wstrb[0], 8)))
        aw_hs.assign(awvalid & awready)
        w_hs.assign(wvalid & wready)

        m.Always(Posedge(aclk))(
            If(areset)(
                wstate(WRRESET)
            ).Elif(aclk_en)(
                wstate(wnext)
            )
        )
        m.Always()(
            Case(wstate)(
                When(WRIDLE)(
                    If(awvalid)(
                        wnext(WRDATA)
                    ).Else(
                        wnext(WRIDLE)
                    )
                ),
                When(WRDATA)(
                    If(wvalid)(
                        wnext(WRRESP)
                    ).Else(
                        wnext(WRDATA)
                    )
                ),
                When(WRRESP)(
                    If(bready)(
                        wnext(WRIDLE)
                    ).Else(
                        wnext(WRRESP)
                    )
                ),
                When()(
                    wnext(WRIDLE)
                )
            )
        )
        m.Always(Posedge(aclk))(
            If(aclk_en)(
                If(aw_hs)(
                    waddr(awaddr[0:ADDR_BITS])
                )
            )
        )

        arready.assign(rstate == RDIDLE)
        rdata.assign(rrdata)
        rresp.assign(Int(0, 2, 2))
        rvalid.assign(rstate == RDDATA)
        ar_hs.assign(arvalid & arready)
        raddr.assign(araddr[0:ADDR_BITS])

        m.Always(Posedge(aclk))(
            If(areset)(
                rstate(RDRESET)
            ).Elif(aclk_en)(
                rstate(rnext)
            )
        )
        m.Always()(
            Case(rstate)(
                When(RDIDLE)(
                    If(arvalid)(
                        rnext(RDDATA)
                    ).Else(
                        rnext(RDIDLE)
                    )
                ),
                When(RDDATA)(
                    If(rready & rvalid)(
                        rnext(RDIDLE)
                    ).Else(
                        rnext(RDDATA)
                    )
                ),
                When()(
                    rnext(RDIDLE)
                )
            )
        )

        case_fsm_rdata = Case(raddr)
        case_fsm_rdata.add(When(ADDR_AP_CTRL)(
            rrdata[0](int_ap_start),
            rrdata[1](int_ap_done),
            rrdata[2](int_ap_idle),
            rrdata[3](int_ap_ready),
            rrdata[7](int_auto_restart)
        ))
        case_fsm_rdata.add(When(ADDR_GIE)(
            rrdata(int_gie)
        ))
        case_fsm_rdata.add(When(ADDR_IER)(
            rrdata(int_ier)
        ))
        case_fsm_rdata.add(When(ADDR_ISR)(
            rrdata(int_isr)
        ))

        for i in range(len(ADDR_IN_S_DATA)):
            case_fsm_rdata.add(When(ADDR_IN_S_DATA[i])(
                rrdata(int_in_s[i][0:])
            ))

        for i in range(len(ADDR_OUT_S_DATA)):
            case_fsm_rdata.add(When(ADDR_OUT_S_DATA[i])(
                rrdata(int_out_s[i][0:])
            ))

        for i in range(len(ADDR_IN_DATA_0)):
            case_fsm_rdata.add(When(ADDR_IN_DATA_0[i])(
                rrdata(int_in[i][0:32])
            ))
            case_fsm_rdata.add(When(ADDR_IN_DATA_1[i])(
                rrdata(int_in[i][32:])
            ))

        for i in range(len(ADDR_OUT_DATA_0)):
            case_fsm_rdata.add(When(ADDR_OUT_DATA_0[i])(
                rrdata(int_out[i][0:32])
            ))
            case_fsm_rdata.add(When(ADDR_OUT_DATA_1[i])(
                rrdata(int_out[i][32:])
            ))

        m.Always(Posedge(aclk))(
            If(aclk_en)(
                If(ar_hs)(
                    rrdata(Int(0, 1, 2)),
                    case_fsm_rdata
                )
            )
        )

        interrupt.assign(int_gie & (Uor(int_isr)))
        ap_start.assign(int_ap_start)
        for i, j in zip(in_s, int_in_s):
            i.assign(j)

        for i, j in zip(out_s, int_out_s):
            i.assign(j)

        for i, j, k, l in zip(iin, int_in, out, int_out):
            i.assign(j)
            k.assign(l)

        m.Always(Posedge(aclk))(
            If(areset)(
                int_ap_start(Int(0, 1, 2))
            ).Elif(aclk_en)(
                If(AndList(w_hs, waddr == ADDR_AP_CTRL, wstrb[0], wdata[0]))(
                    int_ap_start(Int(1, 1, 2))
                ).Elif(ap_ready)(
                    int_ap_start(int_auto_restart)
                )
            )
        )
        m.Always(Posedge(aclk))(
            If(areset)(
                int_ap_done(Int(0, 1, 2))
            ).Elif(aclk_en)(
                If(ap_done)(
                    int_ap_done(Int(1, 1, 2))
                ).Elif(Land(ar_hs, raddr == ADDR_AP_CTRL))(
                    int_ap_done(Int(0, 1, 2))
                )
            )
        )

        m.Always(Posedge(aclk))(
            If(areset)(
                int_ap_idle(Int(1, 1, 2))
            ).Elif(aclk_en)(
                int_ap_idle(ap_idle)
            )
        )

        m.Always(Posedge(aclk))(
            If(areset)(
                int_ap_ready(Int(0, 1, 2))
            ).Elif(aclk_en)(
                int_ap_ready(ap_ready)
            )
        )

        m.Always(Posedge(aclk))(
            If(areset)(
                int_auto_restart(Int(0, 1, 2))
            ).Elif(aclk_en)(
                If(AndList(w_hs, waddr == ADDR_AP_CTRL, wstrb[0]))(
                    int_auto_restart(wdata[7])
                )
            )
        )
        m.Always(Posedge(aclk))(
            If(areset)(
                int_gie(Int(0, 1, 2))
            ).Elif(aclk_en)(
                If(AndList(w_hs, waddr == ADDR_GIE, wstrb[0]))(
                    int_gie(wdata[0])
                )
            )
        )
        m.Always(Posedge(aclk))(
            If(areset)(
                int_ier(Int(0, 2, 2))
            ).Elif(aclk_en)(
                If(AndList(w_hs, waddr == ADDR_IER, wstrb[0]))(
                    int_ier(wdata[0:2])
                )
            )
        )
        m.Always(Posedge(aclk))(
            If(areset)(
                int_isr[0](Int(0, 1, 2))
            ).Elif(aclk_en)(
                If(int_ier[0] & ap_done)(
                    int_isr[0](Int(1, 1, 2))
                ).Elif(AndList(w_hs, waddr == ADDR_ISR, wstrb[0]))(
                    int_isr[0](Xor(int_isr[0], wdata[0]))
                )
            )
        )
        m.Always(Posedge(aclk))(
            If(areset)(
                int_isr[1](Int(0, 1, 2))
            ).Elif(aclk_en)(
                If(int_ier[1] & ap_ready)(
                    int_isr[1](Int(1, 1, 2))
                ).Elif(AndList(w_hs, waddr == ADDR_ISR, wstrb[0]))(
                    int_isr[1](Xor(int_isr[1], wdata[1]))
                )
            )
        )

        for i in range(len(int_in_s)):
            m.Always(Posedge(aclk))(
                If(areset)(
                    int_in_s[i][0:32](Int(0, 32, 10))
                ).Elif(aclk_en)(
                    If(Land(w_hs, waddr == ADDR_IN_S_DATA[i]))(
                        int_in_s[i][0:32](Or(And(wdata[0:32], wmask), And(int_in_s[i][0:32], ~wmask)))
                    )
                )
            )

        for i in range(len(int_out_s)):
            m.Always(Posedge(aclk))(
                If(areset)(
                    int_out_s[i][0:32](Int(0, 32, 10))
                ).Elif(aclk_en)(
                    If(Land(w_hs, waddr == ADDR_OUT_S_DATA[i]))(
                        int_out_s[i][0:32](Or(And(wdata[0:32], wmask), And(int_out_s[i][0:32], ~wmask)))
                    )
                )
            )

        for i in range(len(int_in)):
            m.Always(Posedge(aclk))(
                If(areset)(
                    int_in[i][0:32](Int(0, 32, 10))
                ).Elif(aclk_en)(
                    If(Land(w_hs, waddr == ADDR_IN_DATA_0[i]))(
                        int_in[i][0:32](Or(And(wdata[0:32], wmask), And(int_in[i][0:32], ~wmask)))
                    )
                )
            )
            m.Always(Posedge(aclk))(
                If(areset)(
                    int_in[i][32:64](Int(0, 32, 10))
                ).Elif(aclk_en)(
                    If(Land(w_hs, waddr == ADDR_IN_DATA_1[i]))(
                        int_in[i][32:64](Or(And(wdata[0:32], wmask), And(int_in[i][32:64], ~wmask)))
                    )
                )
            )
            m.Always(Posedge(aclk))(
                If(areset)(
                    int_out[i][0:32](Int(0, 32, 10))
                ).Elif(aclk_en)(
                    If(Land(w_hs, waddr == ADDR_OUT_DATA_0[i]))(
                        int_out[i][0:32](Or(And(wdata[0:32], wmask), And(int_out[i][0:32], ~wmask)))
                    )
                )
            )
            m.Always(Posedge(aclk))(
                If(areset)(
                    int_out[i][32:64](Int(0, 32, 10))
                ).Elif(aclk_en)(
                    If(Land(w_hs, waddr == ADDR_OUT_DATA_1[i]))(
                        int_out[i][32:64](Or(And(wdata[0:32], wmask), And(int_out[i][32:64], ~wmask)))
                    )
                )
            )

        initialize_regs(m, {'wstate': WRRESET, 'rstate': RDRESET, 'int_ap_idle': Int(1, 1, 2)})
        self.cache[name] = m
        return m

    def create_xpm_fifo_sync_wrapper(self):
        name = 'xpm_fifo_sync_wrapper'
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)
        FIFO_MEMORY_TYPE = m.Parameter('FIFO_MEMORY_TYPE', "auto")
        ECC_MODE = m.Parameter('ECC_MODE', "no_ecc")
        FIFO_WRITE_DEPTH = m.Parameter('FIFO_WRITE_DEPTH', 32)
        WRITE_DATA_WIDTH = m.Parameter('WRITE_DATA_WIDTH', self.acc.axi_bus_data_width)
        WR_DATA_COUNT_WIDTH = m.Parameter('WR_DATA_COUNT_WIDTH', 6)
        PROG_FULL_THRESH = m.Parameter('PROG_FULL_THRESH', 2)
        FULL_RESET_VALUE = m.Parameter('FULL_RESET_VALUE', 1)
        READ_MODE = m.Parameter('READ_MODE', "std")
        FIFO_READ_LATENCY = m.Parameter('FIFO_READ_LATENCY', 1)
        READ_DATA_WIDTH = m.Parameter('READ_DATA_WIDTH', self.acc.axi_bus_data_width)
        RD_DATA_COUNT_WIDTH = m.Parameter('RD_DATA_COUNT_WIDTH', 6)
        PROG_EMPTY_THRESH = m.Parameter('PROG_EMPTY_THRESH', 10)
        DOUT_RESET_VALUE = m.Parameter('DOUT_RESET_VALUE', "0")
        WAKEUP_TIME = m.Parameter('WAKEUP_TIME', 0)
        sleep = m.Input('sleep')
        rst = m.Input('rst')
        wr_clk = m.Input('wr_clk')
        wr_en = m.Input('wr_en')
        din = m.Input('din', WRITE_DATA_WIDTH)
        full = m.Output('full')
        prog_full = m.Output('prog_full')
        wr_data_count = m.Output('wr_data_count', WR_DATA_COUNT_WIDTH)
        overflow = m.Output('overflow')
        wr_rst_busy = m.Output('wr_rst_busy')
        rd_en = m.Input('rd_en')
        dout = m.Output('dout', READ_DATA_WIDTH)
        empty = m.Output('empty')
        prog_empty = m.Output('prog_empty')
        rd_data_count = m.Output('rd_data_count', RD_DATA_COUNT_WIDTH)
        underflow = m.Output('underflow')
        rd_rst_busy = m.Output('rd_rst_busy')
        injectsbiterr = m.Input('injectsbiterr')
        injectdbiterr = m.Input('injectdbiterr')
        sbiterr = m.Output('sbiterr')
        dbiterr = m.Output('dbiterr')

        code = 'xpm_fifo_sync #(\n\
              .FIFO_MEMORY_TYPE(FIFO_MEMORY_TYPE),\n\
              .ECC_MODE(ECC_MODE),\n\
              .FIFO_WRITE_DEPTH(FIFO_WRITE_DEPTH),\n\
              .WRITE_DATA_WIDTH(WRITE_DATA_WIDTH),\n\
              .WR_DATA_COUNT_WIDTH(WR_DATA_COUNT_WIDTH),\n\
              .PROG_FULL_THRESH(PROG_FULL_THRESH),\n\
              .FULL_RESET_VALUE(FULL_RESET_VALUE),\n\
              .READ_MODE(READ_MODE),\n\
              .FIFO_READ_LATENCY(FIFO_READ_LATENCY),\n\
              .READ_DATA_WIDTH(READ_DATA_WIDTH),\n\
              .RD_DATA_COUNT_WIDTH(RD_DATA_COUNT_WIDTH),\n\
              .PROG_EMPTY_THRESH(PROG_EMPTY_THRESH),\n\
              .DOUT_RESET_VALUE(DOUT_RESET_VALUE),\n\
              .WAKEUP_TIME(WAKEUP_TIME)\n\
          )\n\
            inst_rd_fifo(\n\
              .sleep(sleep),\n\
              .rst(rst),\n\
              .wr_clk(wr_clk),\n\
              .wr_en(wr_en),\n\
              .din(din),\n\
              .full(full),\n\
              .prog_full(prog_full),\n\
              .wr_data_count(wr_data_count),\n\
              .overflow(overflow),\n\
              .wr_rst_busy(wr_rst_busy),\n\
              .rd_en(rd_en),\n\
              .dout(dout),\n\
              .empty(empty),\n\
              .prog_empty(prog_empty),\n\
              .rd_data_count(rd_data_count),\n\
              .underflow(underflow),\n\
              .rd_rst_busy(rd_rst_busy),\n\
              .injectsbiterr(injectsbiterr),\n\
              .injectdbiterr(injectdbiterr),\n\
              .sbiterr(sbiterr),\n\
              .dbiterr(dbiterr)\n\
            );\n'

        m.EmbeddedCode(code)
        self.cache[name] = m
        return m

    '''
    def create_axi_counter(self):
        name = 'axi_counter'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        C_WIDTH = m.Parameter('C_WIDTH', 4)
        C_INIT = m.Parameter('C_INIT', Repeat(Int(0, 1, 2), C_WIDTH), C_WIDTH)
        clk = m.Input('clk')
        clken = m.Input('clken')
        rst = m.Input('rst')
        load = m.Input('load')
        incr = m.Input('incr')
        decr = m.Input('decr')
        load_value = m.Input('load_value', C_WIDTH)
        count = m.Output('count', C_WIDTH)
        is_zero = m.Output('is_zero')

        LP_ZERO = m.Localparam('LP_ZERO', Repeat(Int(0, 1, 2), C_WIDTH))
        LP_ONE = m.Localparam('LP_ONE', Cat(Repeat(Int(0, 1, 2), C_WIDTH - 1), Int(1, 1, 2)))
        LP_MAX = m.Localparam('LP_MAX', Repeat(Int(1, 1, 2), C_WIDTH))

        count_r = m.Reg('count_r', C_WIDTH)
        is_zero_r = m.Reg('is_zero_r')

        count.assign(count_r)
        m.Always(Posedge(clk))(
            If(rst)(
                count_r(C_INIT)
            ).Elif(clken)(
                If(load)(
                    count_r(load_value)
                ).Elif(incr & ~decr)(
                    count_r.inc()
                ).Elif(decr & ~incr)(
                    count_r.dec()
                ).Else(
                    count_r(count_r)
                )
            )
        )
        is_zero.assign(is_zero_r)
        m.Always(Posedge(clk))(
            If(rst)(
                is_zero_r(C_INIT == LP_ZERO)
            ).Elif(clken)(
                If(load)(
                    is_zero_r(load_value == LP_ZERO)
                ).Else(
                    is_zero_r(Mux(Xor(incr, decr), Lor(Land(decr, count_r == LP_ONE), Land(incr, count_r == LP_MAX)),
                                  is_zero_r))
                )
            ).Else(
                is_zero_r(is_zero_r)
            )
        )
        initialize_regs(m, {'count_r': C_INIT, 'is_zero_r': EmbeddedCode('C_INIT == LP_ZERO')})
        self.cache[name] = m
        return m

    def create_axi_reader(self):
        name = 'axi_reader'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        C_ADDR_WIDTH = m.Parameter('C_ADDR_WIDTH', 64)
        C_DATA_WIDTH = m.Parameter('C_DATA_WIDTH', 32)
        C_LENGTH_WIDTH = m.Parameter('C_LENGTH_WIDTH', 32)
        C_BURST_LEN = m.Parameter('C_BURST_LEN', 256)
        C_LOG_BURST_LEN = m.Parameter('C_LOG_BURST_LEN', EmbeddedCode('$clog2(C_BURST_LEN)'))
        C_MAX_OUTSTANDING = m.Parameter('C_MAX_OUTSTANDING', 3)

        aclk = m.Input('aclk')
        areset = m.Input('areset')
        ctrl_start = m.Input('ctrl_start')
        ctrl_done = m.Output('ctrl_done')
        ctrl_offset = m.Input('ctrl_offset', C_ADDR_WIDTH)
        ctrl_length = m.Input('ctrl_length', C_LENGTH_WIDTH)
        ctrl_prog_full = m.Input('ctrl_prog_full')

        arvalid = m.Output('arvalid')
        arready = m.Input('arready')
        araddr = m.Output('araddr', C_ADDR_WIDTH)
        arlen = m.Output('arlen', 8)
        rvalid = m.Input('rvalid')
        rready = m.Output('rready')
        rdata = m.Input('rdata', C_DATA_WIDTH)
        rlast = m.Input('rlast')
        rresp = m.Input('rresp', 2)
        m_tvalid = m.Output('m_tvalid')
        m_tready = m.Input('m_tready')
        m_tdata = m.Output('m_tdata', C_DATA_WIDTH)

        LP_MAX_OUTSTANDING_CNTR_WIDTH = m.Localparam('LP_MAX_OUTSTANDING_CNTR_WIDTH',
                                                     EmbeddedCode('$clog2(C_MAX_OUTSTANDING+1)'))
        LP_TRANSACTION_CNTR_WIDTH = m.Localparam('LP_TRANSACTION_CNTR_WIDTH', C_LENGTH_WIDTH - C_LOG_BURST_LEN)

        done = m.Reg('done')
        num_full_bursts = m.Wire('num_full_bursts', LP_TRANSACTION_CNTR_WIDTH)
        num_partial_bursts = m.Wire('num_partial_bursts')
        start = m.Reg('start')
        num_transactions = m.Reg('num_transactions', LP_TRANSACTION_CNTR_WIDTH)
        has_partial_burst = m.Reg('has_partial_burst')
        final_burst_len = m.Reg('final_burst_len', C_LOG_BURST_LEN)
        single_transaction = m.Wire('single_transaction')
        ar_idle = m.Reg('ar_idle')
        ar_done = m.Wire('ar_done')

        fifo_stall = m.Wire('fifo_stall')
        arxfer = m.Wire('arxfer')
        arvalid_r = m.Reg('arvalid_r')
        addr = m.Reg('addr', C_ADDR_WIDTH)
        ar_transactions_to_go = m.Wire('ar_transactions_to_go', LP_TRANSACTION_CNTR_WIDTH)
        ar_final_transaction = m.Wire('ar_final_transaction')
        incr_ar_to_r_cnt = m.Wire('incr_ar_to_r_cnt')
        decr_ar_to_r_cnt = m.Wire('decr_ar_to_r_cnt')
        stall_ar = m.Wire('stall_ar')
        outstanding_vacancy_count = m.Wire('outstanding_vacancy_count', LP_MAX_OUTSTANDING_CNTR_WIDTH)

        tvalid = m.Wire('tvalid')
        tdata = m.Wire('tdata', C_DATA_WIDTH)
        rxfer = m.Wire('rxfer')
        decr_r_transaction_cntr = m.Wire('decr_r_transaction_cntr')
        r_transactions_to_go = m.Wire('r_transactions_to_go', LP_TRANSACTION_CNTR_WIDTH)
        r_final_transaction = m.Wire('r_final_transaction')

        m.Always(Posedge(aclk))(
            done(Mux(rxfer & rlast & r_final_transaction, Int(1, 1, 2), Mux(ctrl_done, Int(0, 1, 2), done)))
        )
        ctrl_done.assign(done)

        num_full_bursts.assign(ctrl_length[C_LOG_BURST_LEN:C_LENGTH_WIDTH - C_LOG_BURST_LEN])
        num_partial_bursts.assign(Mux(ctrl_length[0:C_LOG_BURST_LEN], Int(1, 1, 2), Int(0, 1, 2)))

        m.Always(Posedge(aclk))(
            start(ctrl_start),
            num_transactions(Mux(num_partial_bursts == Int(0, 1, 2), num_full_bursts - Int(1, 1, 2), num_full_bursts)),
            has_partial_burst(num_partial_bursts),
            final_burst_len(ctrl_length[0:C_LOG_BURST_LEN] - Int(1, 1, 2))
        )
        single_transaction.assign(
            Mux(num_transactions == Repeat(Int(0, 1, 2), LP_TRANSACTION_CNTR_WIDTH), Int(1, 1, 2), Int(0, 1, 2)))

        arvalid.assign(arvalid_r)
        araddr.assign(addr)
        arlen.assign(Mux(Lor(ar_final_transaction, start & single_transaction), final_burst_len, C_BURST_LEN - 1))
        arxfer.assign(arvalid & arready)
        fifo_stall.assign(ctrl_prog_full)

        m.Always(Posedge(aclk))(
            If(areset)(
                arvalid_r(Int(0, 1, 2))
            ).Else(
                arvalid_r(Mux(~ar_idle & ~stall_ar & ~arvalid_r & ~fifo_stall, Int(1, 1, 2),
                              Mux(arready, Int(0, 1, 2), arvalid_r)))
            )
        )

        m.Always(Posedge(aclk))(
            If(areset)(
                ar_idle(Int(1, 1, 2))
            ).Else(
                ar_idle(Mux(start, Int(0, 1, 2), Mux(ar_done, Int(1, 1, 2), ar_idle)))
            )
        )

        m.Always(Posedge(aclk))(
            addr(Mux(ctrl_start, ctrl_offset, Mux(arxfer, addr + C_BURST_LEN * C_DATA_WIDTH / 8, addr)))
        )

        ar_done.assign(Land(ar_final_transaction, arxfer))
        incr_ar_to_r_cnt.assign(rxfer & rlast)
        decr_ar_to_r_cnt.assign(arxfer)

        m_tvalid.assign(tvalid)
        m_tdata.assign(tdata)
        tvalid.assign(rvalid)
        tdata.assign(rdata)

        rready.assign(Int(1, 1, 2))
        rxfer.assign(rready & rvalid)
        decr_r_transaction_cntr.assign(rxfer & rlast)

        counter = self.create_axi_counter()
        param = [('C_WIDTH', LP_TRANSACTION_CNTR_WIDTH), ('C_INIT', Repeat(Int(0, 1, 2), LP_TRANSACTION_CNTR_WIDTH))]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', start), ('incr', Int(0, 1, 2)),
               ('decr', arxfer), ('load_value', num_transactions), ('count', ar_transactions_to_go),
               ('is_zero', ar_final_transaction)]
        m.Instance(counter, 'inst_ar_transaction_cntr', param, con)
        param = [('C_WIDTH', LP_MAX_OUTSTANDING_CNTR_WIDTH),
                 ('C_INIT', C_MAX_OUTSTANDING[0:LP_MAX_OUTSTANDING_CNTR_WIDTH])]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', Int(0, 1, 2)),
               ('incr', incr_ar_to_r_cnt),
               ('decr', decr_ar_to_r_cnt), ('load_value', Repeat(Int(0, 1, 2), LP_MAX_OUTSTANDING_CNTR_WIDTH)),
               ('count', outstanding_vacancy_count),
               ('is_zero', stall_ar)]
        m.Instance(counter, 'inst_ar_to_r_transaction_cntr', param, con)
        param = [('C_WIDTH', LP_TRANSACTION_CNTR_WIDTH), ('C_INIT', Repeat(Int(0, 1, 2), LP_TRANSACTION_CNTR_WIDTH))]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', start), ('incr', Int(0, 1, 2)),
               ('decr', decr_r_transaction_cntr), ('load_value', num_transactions), ('count', r_transactions_to_go),
               ('is_zero', r_final_transaction)]
        m.Instance(counter, 'inst_r_transaction_cntr', param, con)

        initialize_regs(m, {'ar_idle': Int(1, 1, 2)})
        self.cache[name] = m

        return m

    def create_axi_writer(self):
        name = 'axi_writer'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        C_ADDR_WIDTH = m.Parameter('C_ADDR_WIDTH', 64)
        C_DATA_WIDTH = m.Parameter('C_DATA_WIDTH', 32)
        C_MAX_LENGTH_WIDTH = m.Parameter('C_MAX_LENGTH_WIDTH', 32)
        C_BURST_LEN = m.Parameter('C_BURST_LEN', 256)
        C_LOG_BURST_LEN = m.Parameter('C_LOG_BURST_LEN', 8)

        aclk = m.Input('aclk')
        areset = m.Input('areset')
        ctrl_start = m.Input('ctrl_start')
        ctrl_offset = m.Input('ctrl_offset', C_ADDR_WIDTH)
        ctrl_length = m.Input('ctrl_length', C_MAX_LENGTH_WIDTH)
        ctrl_done = m.Output('ctrl_done')
        s_tvalid = m.Input('s_tvalid')
        s_tdata = m.Input('s_tdata', C_DATA_WIDTH)
        s_tready = m.Output('s_tready')
        awaddr = m.Output('awaddr', C_ADDR_WIDTH)
        awlen = m.Output('awlen', 8)
        awvalid = m.Output('awvalid')
        awready = m.Input('awready')
        wdata = m.Output('wdata', C_DATA_WIDTH)
        wstrb = m.Output('wstrb', Div(C_DATA_WIDTH, 8))
        wlast = m.Output('wlast')
        wvalid = m.Output('wvalid')
        wready = m.Input('wready')
        bvalid = m.Input('bvalid')
        bready = m.Output('bready')

        LP_LOG_MAX_W_TO_AW = m.Localparam('LP_LOG_MAX_W_TO_AW', 8)
        LP_TRANSACTION_CNTR_WIDTH = m.Localparam('LP_TRANSACTION_CNTR_WIDTH', C_MAX_LENGTH_WIDTH - C_LOG_BURST_LEN)

        num_full_bursts = m.Wire('num_full_bursts', LP_TRANSACTION_CNTR_WIDTH)
        num_partial_bursts = m.Wire('num_partial_bursts')
        start = m.Reg('start')
        num_transactions = m.Reg('num_transactions', LP_TRANSACTION_CNTR_WIDTH)
        has_partial_burst = m.Reg('has_partial_burst')
        final_burst_len = m.Reg('final_burst_len', C_LOG_BURST_LEN)
        single_transaction = m.Wire('single_transaction')

        wxfer = m.Wire('wxfer')
        wfirst = m.Reg('wfirst')
        load_burst_cntr = m.Wire('load_burst_cntr')
        wxfers_to_go = m.Wire('wxfers_to_go', C_LOG_BURST_LEN)
        w_transactions_to_go = m.Wire('w_transactions_to_go', LP_TRANSACTION_CNTR_WIDTH)
        w_final_transaction = m.Wire('w_final_transaction')
        w_almost_final_transaction = m.Reg('w_almost_final_transaction')
        awxfer = m.Wire('awxfer')
        awvalid_r = m.Reg('awvalid_r')
        addr = m.Reg('addr', C_ADDR_WIDTH)
        wfirst_d1 = m.Reg('wfirst_d1')
        wfirst_pulse = m.Reg('wfirst_pulse')
        dbg_w_to_aw_outstanding = m.Wire('dbg_w_to_aw_outstanding', LP_LOG_MAX_W_TO_AW)
        idle_aw = m.Wire('idle_aw')
        aw_transactions_to_go = m.Wire('aw_transactions_to_go', LP_TRANSACTION_CNTR_WIDTH)
        aw_final_transaction = m.Wire('aw_final_transaction')
        bxfer = m.Wire('bxfer')
        b_transactions_to_go = m.Wire('b_transactions_to_go', LP_TRANSACTION_CNTR_WIDTH)
        b_final_transaction = m.Wire('b_final_transaction')

        num_full_bursts.assign(ctrl_length[C_LOG_BURST_LEN:C_MAX_LENGTH_WIDTH - C_LOG_BURST_LEN])
        num_partial_bursts.assign(Mux(ctrl_length[0:C_LOG_BURST_LEN], Int(1, 1, 2), Int(0, 1, 2)))

        m.Always(Posedge(aclk))(
            start(ctrl_start),
            num_transactions(Mux(num_partial_bursts == Int(0, 1, 2), num_full_bursts - Int(1, 1, 2), num_full_bursts)),
            has_partial_burst(num_partial_bursts),
            final_burst_len(ctrl_length[0:C_LOG_BURST_LEN] - Int(1, 1, 2))
        )

        ctrl_done.assign(bxfer & b_final_transaction)
        single_transaction.assign(
            Mux(num_transactions == Repeat(Int(0, 1, 2), LP_TRANSACTION_CNTR_WIDTH), Int(1, 1, 2), Int(0, 1, 2)))

        wvalid.assign(s_tvalid)
        wdata.assign(s_tdata)
        wstrb.assign(Repeat(Int(1, 1, 2), Div(C_DATA_WIDTH, 8)))
        s_tready.assign(wready)
        wxfer.assign(wvalid & wready)
        m.Always(Posedge(aclk))(
            If(areset)(
                wfirst(Int(1, 1, 2))
            ).Else(
                wfirst(Mux(wxfer, wlast, wfirst))
            )
        )

        load_burst_cntr.assign(Lor(And(And(wxfer, wlast), w_almost_final_transaction), And(start, single_transaction)))

        m.Always(Posedge(aclk))(
            w_almost_final_transaction(Mux(w_transactions_to_go == 1, Int(1, 1, 2), Int(0, 1, 2)))
        )

        awvalid.assign(awvalid_r)
        awxfer.assign(awvalid & awready)

        m.Always(Posedge(aclk))(
            If(areset)(
                awvalid_r(Int(0, 1, 2))
            ).Else(
                awvalid_r(Mux(~idle_aw & ~awvalid_r, Int(1, 1, 2), Mux(awready, Int(0, 1, 2), awvalid_r)))
            )
        )
        awaddr.assign(addr)
        m.Always(Posedge(aclk))(
            addr(Mux(ctrl_start, ctrl_offset, Mux(awxfer, addr + C_BURST_LEN * C_DATA_WIDTH / 8, addr)))
        )
        awlen.assign(Mux(Lor(aw_final_transaction, And(start, single_transaction)), final_burst_len, C_BURST_LEN - 1))

        m.Always(Posedge(aclk))(
            wfirst_d1(wvalid & wfirst)
        )
        m.Always(Posedge(aclk))(
            wfirst_pulse(wvalid & wfirst & ~wfirst_d1)
        )
        bready.assign(Int(1, 1, 2))
        bxfer.assign(bready & bvalid)

        counter = self.create_axi_counter()
        param = [('C_WIDTH', C_LOG_BURST_LEN), ('C_INIT', Repeat(Int(1, 1, 2), C_LOG_BURST_LEN))]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', load_burst_cntr),
               ('incr', Int(0, 1, 2)),
               ('decr', wxfer), ('load_value', final_burst_len), ('count', wxfers_to_go),
               ('is_zero', wlast)]
        m.Instance(counter, 'inst_burst_cntr', param, con)

        param = [('C_WIDTH', LP_TRANSACTION_CNTR_WIDTH), ('C_INIT', Repeat(Int(0, 1, 2), LP_TRANSACTION_CNTR_WIDTH))]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', start),
               ('incr', Int(0, 1, 2)),
               ('decr', wxfer & wlast), ('load_value', num_transactions), ('count', w_transactions_to_go),
               ('is_zero', w_final_transaction)]
        m.Instance(counter, 'inst_w_transaction_cntr', param, con)

        param = [('C_WIDTH', LP_LOG_MAX_W_TO_AW), ('C_INIT', Repeat(Int(0, 1, 2), LP_LOG_MAX_W_TO_AW))]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', Int(0, 1, 2)),
               ('incr', wfirst_pulse),
               ('decr', awxfer), ('load_value', EmbeddedCode('')),
               ('count', dbg_w_to_aw_outstanding),
               ('is_zero', idle_aw)]
        m.Instance(counter, 'inst_w_to_aw_cntr', param, con)

        param = [('C_WIDTH', LP_TRANSACTION_CNTR_WIDTH), ('C_INIT', Repeat(Int(0, 1, 2), LP_TRANSACTION_CNTR_WIDTH))]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', start),
               ('incr', Int(0, 1, 2)),
               ('decr', awxfer), ('load_value', num_transactions),
               ('count', aw_transactions_to_go),
               ('is_zero', aw_final_transaction)]
        m.Instance(counter, 'inst_aw_transaction_cntr', param, con)

        param = [('C_WIDTH', LP_TRANSACTION_CNTR_WIDTH), ('C_INIT', Repeat(Int(0, 1, 2), LP_TRANSACTION_CNTR_WIDTH))]
        con = [('clk', aclk), ('clken', Int(1, 1, 2)), ('rst', areset), ('load', start),
               ('incr', Int(0, 1, 2)),
               ('decr', bxfer), ('load_value', num_transactions),
               ('count', b_transactions_to_go),
               ('is_zero', b_final_transaction)]
        m.Instance(counter, 'inst_b_transaction_cntr', param, con)

        initialize_regs(m, {'wfirst': Int(1, 1, 2)})
        self.cache[name] = m

        return m
    '''
