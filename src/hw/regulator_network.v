

module regulator_network #
(
  parameter id = 0
)
(
  input clk,
  input rst,
  input start,
  input data_in_valid,
  input [11-1:0] data_in,
  input end_data_in,
  input read_data_en,
  output has_data_out,
  output has_lst3_data_out,
  output [63-1:0] data_out,
  output task_done
);

  wire fifo_out_we;
  wire [63-1:0] fifo_out_data_in;
  wire fifo_out_empty;
  wire fifo_out_full;
  wire fifo_out_full_almostfull;
  wire fifo_in_we;
  wire [10-1:0] fifo_in_data_in;
  wire fifo_in_re;
  wire [10-1:0] fifo_in_data_out;
  wire fifo_in_empty;
  wire fifo_in_almostempty;
  wire fifo_in_full;
  wire fifo_in_full_almostfull;
  assign has_data_out = ~fifo_out_empty;

  control_fifo_data_in
  #(
    .id(id),
    .id_width(1),
    .width_data_in(11)
  )
  _control_fifo_data_in
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .fifo_in_full(fifo_in_full),
    .fifo_in_we(fifo_in_we),
    .fifo_in_data(fifo_in_data_in)
  );


  fifo
  #(
    .fifo_width(10),
    .fifo_depth_bits(4),
    .fifo_almost_full_threshold(14),
    .fifo_almost_empty_threshold(2)
  )
  fifo_in
  (
    .clk(clk),
    .rst(rst),
    .we(fifo_in_we),
    .din(fifo_in_data_in),
    .re(fifo_in_re),
    .dout(fifo_in_data_out),
    .empty(fifo_in_empty),
    .almostempty(fifo_in_almostempty),
    .full(fifo_in_full),
    .almostfull(fifo_in_full_almostfull)
  );


  fifo
  #(
    .fifo_width(63),
    .fifo_depth_bits(4),
    .fifo_almost_full_threshold(14),
    .fifo_almost_empty_threshold(2)
  )
  fifo_out
  (
    .clk(clk),
    .rst(rst),
    .we(fifo_out_we),
    .din(fifo_out_data_in),
    .re(read_data_en),
    .dout(data_out),
    .empty(fifo_out_empty),
    .almostempty(has_lst3_data_out),
    .full(fifo_out_full),
    .almostfull(fifo_out_full_almostfull)
  );


  gnr_control
  #(
    .ID(ID)
  )
  _gnr_control
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .fifo_out_full(fifo_out_full),
    .fifo_in_empty(fifo_in_empty),
    .fifo_data_in(fifo_in_data_out),
    .end_data_in(end_data_in),
    .fifo_in_re(fifo_in_re),
    .data_out(fifo_out_data_in),
    .fifo_out_we(fifo_out_we),
    .fifo_out_empty(fifo_out_empty),
    .done(task_done)
  );


endmodule



module control_fifo_data_in #
(
  parameter id = 0,
  parameter id_width = 1,
  parameter width_data_in = 10
)
(
  input clk,
  input rst,
  input start,
  input data_in_valid,
  input [width_data_in-1:0] data_in,
  input fifo_in_full,
  output reg fifo_in_we,
  output reg [width_data_in-id_width-1:0] fifo_in_data
);


  always @(posedge clk) begin
    if(rst) begin
      fifo_in_we <= 0;
      fifo_in_data <= 0;
    end else begin
      if(start) begin
        fifo_in_we <= 0;
        if(data_in_valid && (data_in[id_width-1:0] == id) && ~fifo_in_full) begin
          fifo_in_we <= 1;
          fifo_in_data <= data_in[width_data_in-1:id_width];
        end 
      end 
    end
  end


  initial begin
    fifo_in_we = 0;
    fifo_in_data = 0;
  end


endmodule



module fifo #
(
  parameter fifo_width = 32,
  parameter fifo_depth_bits = 8,
  parameter fifo_almost_full_threshold = 2**fifo_depth_bits - 4,
  parameter fifo_almost_empty_threshold = 2
)
(
  input clk,
  input rst,
  input we,
  input [fifo_width-1:0] din,
  input re,
  output reg [fifo_width-1:0] dout,
  output reg empty,
  output reg almostempty,
  output reg full,
  output reg almostfull
);

  reg [fifo_depth_bits-1:0] rp;
  reg [fifo_depth_bits-1:0] wp;
  reg [fifo_depth_bits-1:0] count;
  reg [fifo_width-1:0] mem [0:2**fifo_depth_bits-1];

  always @(posedge clk) begin
    if(rst) begin
      empty <= 1;
      almostempty <= 1;
      full <= 0;
      almostfull <= 0;
      rp <= 0;
      wp <= 0;
      count <= 0;
    end else begin
      case({ we, re })
        3: begin
          rp <= rp + 1;
          wp <= wp + 1;
        end
        2: begin
          if(~full) begin
            wp <= wp + 1;
            count <= count + 1;
            empty <= 0;
            if(count == fifo_almost_empty_threshold - 1) begin
              almostempty <= 0;
            end 
            if(count == 2**fifo_depth_bits-1) begin
              full <= 1;
            end 
            if(count == fifo_almost_full_threshold - 1) begin
              almostfull <= 1;
            end 
          end 
        end
        1: begin
          if(~empty) begin
            rp <= rp + 1;
            count <= count - 1;
            full <= 0;
            if(count == fifo_almost_full_threshold) begin
              almostfull <= 0;
            end 
            if(count == 1) begin
              empty <= 1;
            end 
            if(count == fifo_almost_empty_threshold) begin
              almostempty <= 1;
            end 
          end 
        end
      endcase
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      dout <= 0;
    end else begin
      if(we == 1) begin
        mem[wp] <= din;
      end 
      if(re == 1) begin
        dout <= mem[rp];
      end 
    end
  end

  integer i_initial;

  initial begin
    dout = 0;
    empty = 0;
    almostempty = 0;
    full = 0;
    almostfull = 0;
    rp = 0;
    wp = 0;
    count = 0;
    for(i_initial=0; i_initial<2**fifo_depth_bits; i_initial=i_initial+1) begin
      mem[i_initial] = 0;
    end
  end


endmodule



module gnr_control #
(
  parameter ID = 0
)
(
  input clk,
  input rst,
  input start,
  input fifo_out_full,
  input fifo_in_empty,
  input [10-1:0] fifo_data_in,
  input end_data_in,
  output reg fifo_in_re,
  output reg fifo_out_we,
  input fifo_out_empty,
  output reg [63-1:0] data_out,
  output reg done
);

  wire [5-1:0] s0;
  wire [5-1:0] s1;
  reg start_s0;
  reg start_s1;
  reg rst_nos;
  reg [5-1:0] init_state;
  reg [5-1:0] state_net;
  reg [29-1:0] period;
  reg [29-1:0] transient;
  reg [5-1:0] end_state_reg;
  reg [29-1:0] period_count;
  reg [29-1:0] transient_count;
  reg start_count_period;
  reg start_count_transient;
  reg reset_counts;
  reg pass_cycle;
  reg flag_rd;
  reg flag_wr;
  reg pass_cycle_attractor;
  reg [3-1:0] fsm_state;
  localparam IDLE = 0;
  localparam GET_STATE = 1;
  localparam RESET_NOS = 2;
  localparam START_NOS = 3;
  localparam FIND_ATTRACTOR = 4;
  localparam CALC_PERIOD_ATTRACTOR = 5;
  localparam FIND_NEXT_ATTRACTOR = 6;
  localparam DONE = 7;

  always @(posedge clk) begin
    if(rst) begin
      init_state <= 0;
      start_count_period <= 0;
      start_count_transient <= 0;
      done <= 0;
      start_s0 <= 0;
      start_s1 <= 0;
      fifo_out_we <= 0;
      reset_counts <= 0;
      state_net <= 0;
      period <= 0;
      transient <= 0;
      end_state_reg <= 0;
      fifo_in_re <= 0;
      flag_rd <= 0;
      flag_wr <= 0;
      rst_nos <= 0;
      data_out <= 0;
      fsm_state <= IDLE;
      pass_cycle_attractor <= 1;
    end else begin
      if(start) begin
        fifo_out_we <= 0;
        rst_nos <= 0;
        reset_counts <= 0;
        fifo_in_re <= 0;
        case(fsm_state)
          IDLE: begin
            if(~fifo_in_empty) begin
              fifo_in_re <= 1;
              flag_rd <= 0;
              fsm_state <= GET_STATE;
            end else if(end_data_in) begin
              fsm_state <= DONE;
            end 
          end
          GET_STATE: begin
            if(flag_rd) begin
              init_state <= fifo_data_in[4:0];
              end_state_reg <= fifo_data_in[9:5];
              flag_rd <= 0;
              fsm_state <= RESET_NOS;
            end else begin
              flag_rd <= 1;
            end
          end
          RESET_NOS: begin
            rst_nos <= 1;
            reset_counts <= 1;
            fsm_state <= START_NOS;
          end
          START_NOS: begin
            start_s0 <= 1;
            start_s1 <= 1;
            pass_cycle_attractor <= 1;
            fsm_state <= FIND_ATTRACTOR;
          end
          FIND_ATTRACTOR: begin
            if(pass_cycle_attractor) begin
              pass_cycle_attractor <= 0;
              if((s0 == s1) && start_count_transient) begin
                state_net <= s0;
                if(s0 == init_state) begin
                  transient <= 0;
                end else begin
                  transient <= transient_count;
                end
                start_count_transient <= 0;
                start_s0 <= 0;
                start_s1 <= 0;
                fsm_state <= CALC_PERIOD_ATTRACTOR;
              end else begin
                start_count_transient <= 1;
                fsm_state <= FIND_ATTRACTOR;
              end
            end else begin
              pass_cycle_attractor <= 1;
            end
          end
          CALC_PERIOD_ATTRACTOR: begin
            if((state_net == s1) && start_count_period) begin
              start_count_period <= 0;
              period <= period_count;
              start_s1 <= 0;
              fsm_state <= FIND_NEXT_ATTRACTOR;
            end else begin
              fsm_state <= CALC_PERIOD_ATTRACTOR;
              start_count_period <= 1;
              start_s1 <= 1;
            end
          end
          FIND_NEXT_ATTRACTOR: begin
            if(~fifo_out_full) begin
              fifo_out_we <= 1;
              data_out <= { state_net, transient, period };
              if(init_state < end_state_reg) begin
                init_state <= init_state + 1;
                fsm_state <= RESET_NOS;
              end else begin
                fsm_state <= DONE;
              end
            end 
          end
          DONE: begin
            if(fifo_in_empty) begin
              if(end_data_in) begin
                if(flag_wr) begin
                  if(fifo_out_empty) begin
                    done <= 1;
                  end 
                  flag_wr <= 0;
                end else begin
                  flag_wr <= 1;
                end
              end 
              fsm_state <= DONE;
            end else begin
              fifo_in_re <= 1;
              flag_rd <= 0;
              init_state <= 0;
              fsm_state <= GET_STATE;
            end
          end
        endcase
      end 
    end
  end


  always @(posedge clk) begin
    if(reset_counts) begin
      period_count <= 0;
      transient_count <= 0;
      pass_cycle <= 1;
    end else begin
      if(start_count_period) begin
        period_count <= period_count + 1;
      end 
      if(start_count_transient) begin
        transient_count <= transient_count + pass_cycle;
      end 
      pass_cycle <= ~pass_cycle;
    end
  end


  gnr_graph
  _gnr_graph
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .rst_nos(rst_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state),
    .s0(s0),
    .s1(s1)
  );


  initial begin
    fifo_in_re = 0;
    fifo_out_we = 0;
    data_out = 0;
    done = 0;
    start_s0 = 0;
    start_s1 = 0;
    rst_nos = 0;
    init_state = 0;
    state_net = 0;
    period = 0;
    transient = 0;
    end_state_reg = 0;
    period_count = 0;
    transient_count = 0;
    start_count_period = 0;
    start_count_transient = 0;
    reset_counts = 0;
    pass_cycle = 0;
    flag_rd = 0;
    flag_wr = 0;
    pass_cycle_attractor = 0;
    fsm_state = 0;
  end


endmodule



module gnr_graph
(
  input clk,
  input rst,
  input start,
  input rst_nos,
  input start_s0,
  input start_s1,
  input [5-1:0] init_state,
  output [5-1:0] s0,
  output [5-1:0] s1
);

  wire ctra_s0;
  wire ctra_s1;
  wire gcra_s0;
  wire gcra_s1;
  wire scip_s0;
  wire scip_s1;
  wire dnaa_s0;
  wire dnaa_s1;
  wire ccrm_s0;
  wire ccrm_s1;

  no_ctra
  _no_ctra
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .rst_nos(rst_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[0]),
    .gcra_s0(gcra_s0),
    .gcra_s1(gcra_s1),
    .ccrm_s0(ccrm_s0),
    .ccrm_s1(ccrm_s1),
    .scip_s0(scip_s0),
    .scip_s1(scip_s1),
    .s0(s0[0]),
    .s1(s1[0]),
    .ctra_s0(ctra_s0),
    .ctra_s1(ctra_s1)
  );


  no_gcra
  _no_gcra
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .rst_nos(rst_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[1]),
    .dnaa_s0(dnaa_s0),
    .dnaa_s1(dnaa_s1),
    .ctra_s0(ctra_s0),
    .ctra_s1(ctra_s1),
    .s0(s0[1]),
    .s1(s1[1]),
    .gcra_s0(gcra_s0),
    .gcra_s1(gcra_s1)
  );


  no_scip
  _no_scip
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .rst_nos(rst_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[2]),
    .ctra_s0(ctra_s0),
    .ctra_s1(ctra_s1),
    .dnaa_s0(dnaa_s0),
    .dnaa_s1(dnaa_s1),
    .s0(s0[2]),
    .s1(s1[2]),
    .scip_s0(scip_s0),
    .scip_s1(scip_s1)
  );


  no_dnaa
  _no_dnaa
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .rst_nos(rst_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[3]),
    .ctra_s0(ctra_s0),
    .ctra_s1(ctra_s1),
    .ccrm_s0(ccrm_s0),
    .ccrm_s1(ccrm_s1),
    .gcra_s0(gcra_s0),
    .gcra_s1(gcra_s1),
    .s0(s0[3]),
    .s1(s1[3]),
    .dnaa_s0(dnaa_s0),
    .dnaa_s1(dnaa_s1)
  );


  no_ccrm
  _no_ccrm
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .rst_nos(rst_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[4]),
    .ctra_s0(ctra_s0),
    .ctra_s1(ctra_s1),
    .scip_s0(scip_s0),
    .scip_s1(scip_s1),
    .s0(s0[4]),
    .s1(s1[4]),
    .ccrm_s0(ccrm_s0),
    .ccrm_s1(ccrm_s1)
  );


endmodule



module no_ctra
(
  input clk,
  input start,
  input rst,
  input rst_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] gcra_s0,
  input [1-1:0] gcra_s1,
  input [1-1:0] ccrm_s0,
  input [1-1:0] ccrm_s1,
  input [1-1:0] scip_s0,
  input [1-1:0] scip_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] ctra_s0,
  output [1-1:0] ctra_s1
);

  reg pass;

  always @(posedge clk) begin
    if(rst_nos) begin
      s0 <= init_state;
      pass <= 1;
    end else begin
      if(start_s0) begin
        if(pass) begin
          s0 <=  ( s0 | gcra_s0 ) & ( ~ ccrm_s0 ) & ( ~ scip_s0 ) ;
        end 
        pass <= ~pass;
      end 
    end
  end


  always @(posedge clk) begin
    if(rst_nos) begin
      s1 <= init_state;
    end else begin
      if(start_s1) begin
        s1 <=  ( s1 | gcra_s1 ) & ( ~ ccrm_s1 ) & ( ~ scip_s1 ) ;
      end 
    end
  end

  assign ctra_s0 = s0;
  assign ctra_s1 = s1;

  initial begin
    s0 = 0;
    s1 = 0;
    pass = 0;
  end


endmodule



module no_gcra
(
  input clk,
  input start,
  input rst,
  input rst_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] dnaa_s0,
  input [1-1:0] dnaa_s1,
  input [1-1:0] ctra_s0,
  input [1-1:0] ctra_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] gcra_s0,
  output [1-1:0] gcra_s1
);

  reg pass;

  always @(posedge clk) begin
    if(rst_nos) begin
      s0 <= init_state;
      pass <= 1;
    end else begin
      if(start_s0) begin
        if(pass) begin
          s0 <=  dnaa_s0 & ~ ctra_s0 ;
        end 
        pass <= ~pass;
      end 
    end
  end


  always @(posedge clk) begin
    if(rst_nos) begin
      s1 <= init_state;
    end else begin
      if(start_s1) begin
        s1 <=  dnaa_s1 & ~ ctra_s1 ;
      end 
    end
  end

  assign gcra_s0 = s0;
  assign gcra_s1 = s1;

  initial begin
    s0 = 0;
    s1 = 0;
    pass = 0;
  end


endmodule



module no_scip
(
  input clk,
  input start,
  input rst,
  input rst_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ctra_s0,
  input [1-1:0] ctra_s1,
  input [1-1:0] dnaa_s0,
  input [1-1:0] dnaa_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] scip_s0,
  output [1-1:0] scip_s1
);

  reg pass;

  always @(posedge clk) begin
    if(rst_nos) begin
      s0 <= init_state;
      pass <= 1;
    end else begin
      if(start_s0) begin
        if(pass) begin
          s0 <=  ctra_s0 & ~ dnaa_s0 ;
        end 
        pass <= ~pass;
      end 
    end
  end


  always @(posedge clk) begin
    if(rst_nos) begin
      s1 <= init_state;
    end else begin
      if(start_s1) begin
        s1 <=  ctra_s1 & ~ dnaa_s1 ;
      end 
    end
  end

  assign scip_s0 = s0;
  assign scip_s1 = s1;

  initial begin
    s0 = 0;
    s1 = 0;
    pass = 0;
  end


endmodule



module no_dnaa
(
  input clk,
  input start,
  input rst,
  input rst_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ctra_s0,
  input [1-1:0] ctra_s1,
  input [1-1:0] ccrm_s0,
  input [1-1:0] ccrm_s1,
  input [1-1:0] gcra_s0,
  input [1-1:0] gcra_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] dnaa_s0,
  output [1-1:0] dnaa_s1
);

  reg pass;

  always @(posedge clk) begin
    if(rst_nos) begin
      s0 <= init_state;
      pass <= 1;
    end else begin
      if(start_s0) begin
        if(pass) begin
          s0 <=  ctra_s0 & ccrm_s0 & ( ~ gcra_s0 ) & ( ~ s0 ) ;
        end 
        pass <= ~pass;
      end 
    end
  end


  always @(posedge clk) begin
    if(rst_nos) begin
      s1 <= init_state;
    end else begin
      if(start_s1) begin
        s1 <=  ctra_s1 & ccrm_s1 & ( ~ gcra_s1 ) & ( ~ s1 ) ;
      end 
    end
  end

  assign dnaa_s0 = s0;
  assign dnaa_s1 = s1;

  initial begin
    s0 = 0;
    s1 = 0;
    pass = 0;
  end


endmodule



module no_ccrm
(
  input clk,
  input start,
  input rst,
  input rst_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ctra_s0,
  input [1-1:0] ctra_s1,
  input [1-1:0] scip_s0,
  input [1-1:0] scip_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] ccrm_s0,
  output [1-1:0] ccrm_s1
);

  reg pass;

  always @(posedge clk) begin
    if(rst_nos) begin
      s0 <= init_state;
      pass <= 1;
    end else begin
      if(start_s0) begin
        if(pass) begin
          s0 <=  ctra_s0 & ( ~ s0 ) & ( ~ scip_s0 ) ;
        end 
        pass <= ~pass;
      end 
    end
  end


  always @(posedge clk) begin
    if(rst_nos) begin
      s1 <= init_state;
    end else begin
      if(start_s1) begin
        s1 <=  ctra_s1 & ( ~ s1 ) & ( ~ scip_s1 ) ;
      end 
    end
  end

  assign ccrm_s0 = s0;
  assign ccrm_s1 = s1;

  initial begin
    s0 = 0;
    s1 = 0;
    pass = 0;
  end


endmodule

