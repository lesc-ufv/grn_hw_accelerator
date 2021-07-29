

module grn_acc
(
  input clk,
  input rst,
  input start,
  input [2-1:0] acc_user_done_rd_data,
  input [2-1:0] acc_user_done_wr_data,
  output [2-1:0] acc_user_request_read,
  input [2-1:0] acc_user_read_data_valid,
  input [64-1:0] acc_user_read_data,
  input [2-1:0] acc_user_available_write,
  output [2-1:0] acc_user_request_write,
  output [176-1:0] acc_user_write_data,
  output acc_user_done
);

  wire [2-1:0] grn_done;
  assign acc_user_done = &grn_done;

  grn_aws_8
  grn_aws_8_0
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .grn_done_rd_data(acc_user_done_rd_data[0]),
    .grn_done_wr_data(acc_user_done_wr_data[0]),
    .grn_request_read(acc_user_request_read[0]),
    .grn_read_data_valid(acc_user_read_data_valid[0]),
    .grn_read_data(acc_user_read_data[31:0]),
    .grn_available_write(acc_user_available_write[0]),
    .grn_request_write(acc_user_request_write[0]),
    .grn_write_data(acc_user_write_data[87:0]),
    .grn_done(grn_done[0])
  );


  grn_aws_1
  grn_aws_1_1
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .grn_done_rd_data(acc_user_done_rd_data[1]),
    .grn_done_wr_data(acc_user_done_wr_data[1]),
    .grn_request_read(acc_user_request_read[1]),
    .grn_read_data_valid(acc_user_read_data_valid[1]),
    .grn_read_data(acc_user_read_data[63:32]),
    .grn_available_write(acc_user_available_write[1]),
    .grn_request_write(acc_user_request_write[1]),
    .grn_write_data(acc_user_write_data[175:88]),
    .grn_done(grn_done[1])
  );


endmodule



module grn_aws_8
(
  input clk,
  input rst,
  input start,
  input grn_done_rd_data,
  input grn_done_wr_data,
  output grn_request_read,
  input grn_read_data_valid,
  input [32-1:0] grn_read_data,
  input grn_available_write,
  output grn_request_write,
  output [88-1:0] grn_write_data,
  output grn_done
);

  wire data_in_valid;
  wire control_data_in_done;
  wire [88-1:0] data_out0;
  wire [88-1:0] data_out1;
  wire [88-1:0] data_out2;
  wire [88-1:0] data_out3;
  wire [88-1:0] data_out4;
  wire [88-1:0] data_out5;
  wire [88-1:0] data_out6;
  wire [88-1:0] data_out7;
  wire [32-1:0] data_in;
  wire [8-1:0] read_data_en;
  wire [8-1:0] has_data;
  wire [8-1:0] has_lst3_data;
  wire [8-1:0] task_done;

  control_data_in
  control_data_in
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .grn_read_data_valid(grn_read_data_valid),
    .grn_read_data(grn_read_data),
    .grn_done_rd_data(grn_done_rd_data),
    .grn_request_read(grn_request_read),
    .data_valid(data_in_valid),
    .data_out(data_in),
    .done(control_data_in_done)
  );


  regulator_network
  #(
    .ID(1)
  )
  rn0
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[0]),
    .has_data_out(has_data[0]),
    .has_lst3_data_out(has_lst3_data[0]),
    .data_out(data_out0),
    .task_done(task_done[0])
  );


  regulator_network
  #(
    .ID(2)
  )
  rn1
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[1]),
    .has_data_out(has_data[1]),
    .has_lst3_data_out(has_lst3_data[1]),
    .data_out(data_out1),
    .task_done(task_done[1])
  );


  regulator_network
  #(
    .ID(3)
  )
  rn2
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[2]),
    .has_data_out(has_data[2]),
    .has_lst3_data_out(has_lst3_data[2]),
    .data_out(data_out2),
    .task_done(task_done[2])
  );


  regulator_network
  #(
    .ID(4)
  )
  rn3
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[3]),
    .has_data_out(has_data[3]),
    .has_lst3_data_out(has_lst3_data[3]),
    .data_out(data_out3),
    .task_done(task_done[3])
  );


  regulator_network
  #(
    .ID(5)
  )
  rn4
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[4]),
    .has_data_out(has_data[4]),
    .has_lst3_data_out(has_lst3_data[4]),
    .data_out(data_out4),
    .task_done(task_done[4])
  );


  regulator_network
  #(
    .ID(6)
  )
  rn5
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[5]),
    .has_data_out(has_data[5]),
    .has_lst3_data_out(has_lst3_data[5]),
    .data_out(data_out5),
    .task_done(task_done[5])
  );


  regulator_network
  #(
    .ID(7)
  )
  rn6
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[6]),
    .has_data_out(has_data[6]),
    .has_lst3_data_out(has_lst3_data[6]),
    .data_out(data_out6),
    .task_done(task_done[6])
  );


  regulator_network
  #(
    .ID(8)
  )
  rn7
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[7]),
    .has_data_out(has_data[7]),
    .has_lst3_data_out(has_lst3_data[7]),
    .data_out(data_out7),
    .task_done(task_done[7])
  );


  control_data_out
  control_data_out
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .grn_done_wr_data(grn_done_wr_data),
    .grn_available_write(grn_available_write),
    .grn_request_write(grn_request_write),
    .grn_write_data(grn_write_data),
    .din0(data_out0),
    .din1(data_out1),
    .din2(data_out2),
    .din3(data_out3),
    .din4(data_out4),
    .din5(data_out5),
    .din6(data_out6),
    .din7(data_out7),
    .read_data_en(read_data_en),
    .task_done(task_done),
    .done(grn_done)
  );


  initial begin
    $dumpfile("uut.vcd");
    $dumpvars(0, "grn_aws");
  end


endmodule



module control_data_in
(
  input clk,
  input rst,
  input start,
  input grn_read_data_valid,
  input [32-1:0] grn_read_data,
  input grn_done_rd_data,
  output reg grn_request_read,
  output reg data_valid,
  output reg [32-1:0] data_out,
  output reg done
);

  localparam [2-1:0] FSM_SEND_DATA = 0;
  localparam [2-1:0] FSM_DONE = 1;
  reg [2-1:0] fms_cs;

  always @(posedge clk) begin
    if(rst) begin
      grn_request_read <= 0;
      done <= 0;
      data_valid <= 0;
      fms_cs <= FSM_SEND_DATA;
    end else begin
      if(start) begin
        data_valid <= 0;
        grn_request_read <= 0;
        case(fms_cs)
          FSM_SEND_DATA: begin
            if(grn_done_rd_data) begin
              fms_cs <= FSM_DONE;
            end else if(grn_read_data_valid) begin
              data_out <= grn_read_data;
              grn_request_read <= 1;
            end 
          end
          FSM_DONE: begin
            done <= 1;
          end
        endcase
      end 
    end
  end


  initial begin
    grn_request_read = 0;
    data_valid = 0;
    data_out = 0;
    done = 0;
    fms_cs = 0;
  end


endmodule



module regulator_network #
(
  parameter ID = 0
)
(
  input clk,
  input rst,
  input start,
  input control_data_in_done,
  input data_in_valid,
  input [32-1:0] data_in,
  input end_data_in,
  input read_data_en,
  output has_data_out,
  output has_lst3_data_out,
  output [88-1:0] data_out,
  output task_done
);

  wire [5-1:0] s0;
  wire [5-1:0] s1;
  wire start_s0;
  wire start_s1;
  wire reset_nos;
  wire [5-1:0] init_state;
  wire fifo_out_we;
  wire [88-1:0] fifo_out_data_in;
  wire fifo_out_empty;
  wire fifo_out_full;
  wire fifo_out_full_almostfull;
  wire fifo_in_we;
  wire [16-1:0] fifo_in_data_in;
  wire fifo_in_re;
  wire [16-1:0] fifo_in_data_out;
  wire fifo_in_empty;
  wire fifo_in_almostempty;
  wire fifo_in_full;
  wire fifo_in_full_almostfull;
  assign has_data_out = ~fifo_out_empty;

  control_fifo_data_in
  #(
    .ID(ID)
  )
  control_fifo_data_in_
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .fifo_in_full(fifo_in_full),
    .fifo_in_amostfull(fifo_in_full_almostfull),
    .fifo_in_we(fifo_in_we),
    .fifo_in_data(fifo_in_data_in)
  );


  fifo
  #(
    .FIFO_WIDTH(16),
    .FIFO_DEPTH_BITS(3),
    .FIFO_ALMOSTFULL_THRESHOLD(6),
    .FIFO_ALMOSTEMPTY_THRESHOLD(2)
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
    .FIFO_WIDTH(88),
    .FIFO_DEPTH_BITS(3),
    .FIFO_ALMOSTFULL_THRESHOLD(6),
    .FIFO_ALMOSTEMPTY_THRESHOLD(2)
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


  control_grn
  #(
    .ID(ID)
  )
  control_grn
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .s0(s0),
    .s1(s1),
    .fifo_out_full(fifo_out_full),
    .fifo_in_empty(fifo_in_empty),
    .fifo_data_in(fifo_in_data_out),
    .end_data_in(end_data_in),
    .fifo_in_re(fifo_in_re),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .reset_nos(reset_nos),
    .init_state(init_state),
    .data_out(fifo_out_data_in),
    .fifo_out_we(fifo_out_we),
    .fifo_out_empty(fifo_out_empty),
    .done(task_done)
  );


  network_graph
  network_graph
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state),
    .s0(s0),
    .s1(s1)
  );


endmodule



module control_fifo_data_in #
(
  parameter ID = 0
)
(
  input clk,
  input rst,
  input start,
  input data_in_valid,
  input [32-1:0] data_in,
  input fifo_in_full,
  input fifo_in_amostfull,
  output reg fifo_in_we,
  output reg [16-1:0] fifo_in_data
);


  always @(posedge clk) begin
    if(rst) begin
      fifo_in_we <= 1'b0;
      fifo_in_data <= 16'd0;
    end else begin
      if(start) begin
        fifo_in_we <= 1'b0;
        if(data_in_valid && (data_in[31:16] == ID) && ~fifo_in_full) begin
          fifo_in_we <= 1'b1;
          fifo_in_data <= data_in[15:0];
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
  parameter FIFO_WIDTH = 32,
  parameter FIFO_DEPTH_BITS = 8,
  parameter FIFO_ALMOSTFULL_THRESHOLD = 2**FIFO_DEPTH_BITS - 4,
  parameter FIFO_ALMOSTEMPTY_THRESHOLD = 2
)
(
  input clk,
  input rst,
  input we,
  input [FIFO_WIDTH-1:0] din,
  input re,
  output reg [FIFO_WIDTH-1:0] dout,
  output reg empty,
  output reg almostempty,
  output reg full,
  output reg almostfull
);

  reg [FIFO_DEPTH_BITS-1:0] rp;
  reg [FIFO_DEPTH_BITS-1:0] wp;
  reg [FIFO_DEPTH_BITS-1:0] count;
  reg [FIFO_WIDTH-1:0] mem [0:2**FIFO_DEPTH_BITS-1];

  always @(posedge clk) begin
    if(rst) begin
      empty <= 1'b1;
      almostempty <= 1'b1;
      full <= 1'b0;
      almostfull <= 1'b0;
      rp <= 0;
      wp <= 0;
      count <= 0;
    end else begin
      case({ we, re })
        2'b11: begin
          rp <= rp + 1;
          wp <= wp + 1;
        end
        2'b10: begin
          if(~full) begin
            wp <= wp + 1;
            count <= count + 1;
            empty <= 1'b0;
            if(count == FIFO_ALMOSTEMPTY_THRESHOLD - 1) begin
              almostempty <= 1'b0;
            end 
            if(count == 2**FIFO_DEPTH_BITS-1) begin
              full <= 1'b1;
            end 
            if(count == FIFO_ALMOSTFULL_THRESHOLD - 1) begin
              almostfull <= 1'b1;
            end 
          end 
        end
        2'b1: begin
          if(~empty) begin
            rp <= rp + 1;
            count <= count - 1;
            full <= 1'b0;
            if(count == FIFO_ALMOSTFULL_THRESHOLD) begin
              almostfull <= 1'b0;
            end 
            if(count == 1) begin
              empty <= 1'b1;
            end 
            if(count == FIFO_ALMOSTEMPTY_THRESHOLD) begin
              almostempty <= 1'b1;
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
      if(we == 1'b1) begin
        mem[wp] <= din;
      end 
      if(re == 1'b1) begin
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
    for(i_initial=0; i_initial<2**FIFO_DEPTH_BITS; i_initial=i_initial+1) begin
      mem[i_initial] = 0;
    end
  end


endmodule



module control_grn #
(
  parameter ID = 0
)
(
  input clk,
  input rst,
  input start,
  input [5-1:0] s0,
  input [5-1:0] s1,
  input fifo_out_full,
  input fifo_in_empty,
  input [10-1:0] fifo_data_in,
  input end_data_in,
  output reg fifo_in_re,
  output reg start_s0,
  output reg start_s1,
  output reg reset_nos,
  output reg [5-1:0] init_state,
  output reg fifo_out_we,
  input fifo_out_empty,
  output reg [63-1:0] data_out,
  output reg done
);

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
  reg [3-1:0] fsm_state;
  reg flag_rd;
  reg flag_wr;
  reg pass_cycle_attractor;
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
      init_state <= 5'd0;
      start_count_period <= 1'b0;
      start_count_transient <= 1'b0;
      done <= 1'b0;
      start_s0 <= 1'b0;
      start_s1 <= 1'b0;
      fifo_out_we <= 1'b0;
      reset_counts <= 1'b0;
      state_net <= 5'd0;
      period <= 29'd0;
      transient <= 29'd0;
      end_state_reg <= 5'd0;
      fifo_in_re <= 1'b0;
      flag_rd <= 1'b0;
      flag_wr <= 1'b0;
      reset_nos <= 1'b0;
      data_out <= 63'd0;
      fsm_state <= IDLE;
      pass_cycle_attractor <= 1'b1;
    end else begin
      if(start) begin
        fifo_out_we <= 1'b0;
        reset_nos <= 1'b0;
        reset_counts <= 1'b0;
        fifo_in_re <= 1'b0;
        case(fsm_state)
          IDLE: begin
            if(~fifo_in_empty) begin
              fifo_in_re <= 1'b1;
              flag_rd <= 1'b0;
              fsm_state <= GET_STATE;
            end else if(end_data_in) begin
              fsm_state <= DONE;
            end 
          end
          GET_STATE: begin
            if(flag_rd) begin
              init_state <= fifo_data_in[4:0];
              end_state_reg <= fifo_data_in[9:5];
              flag_rd <= 1'b0;
              fsm_state <= RESET_NOS;
            end else begin
              flag_rd <= 1'b1;
            end
          end
          RESET_NOS: begin
            reset_nos <= 1'b1;
            reset_counts <= 1'b1;
            fsm_state <= START_NOS;
          end
          START_NOS: begin
            start_s0 <= 1'b1;
            start_s1 <= 1'b1;
            pass_cycle_attractor <= 1'b1;
            fsm_state <= FIND_ATTRACTOR;
          end
          FIND_ATTRACTOR: begin
            if(pass_cycle_attractor) begin
              pass_cycle_attractor <= 1'b0;
              if((s0 == s1) && start_count_transient) begin
                state_net <= s0;
                if(s0 == init_state) begin
                  transient <= 29'd0;
                end else begin
                  transient <= transient_count;
                end
                start_count_transient <= 1'b0;
                start_s0 <= 1'b0;
                start_s1 <= 1'b0;
                fsm_state <= CALC_PERIOD_ATTRACTOR;
              end else begin
                start_count_transient <= 1'b1;
                fsm_state <= FIND_ATTRACTOR;
              end
            end else begin
              pass_cycle_attractor <= 1'b1;
            end
          end
          CALC_PERIOD_ATTRACTOR: begin
            if((state_net == s1) && start_count_period) begin
              start_count_period <= 1'b0;
              period <= period_count;
              start_s1 <= 1'b0;
              fsm_state <= FIND_NEXT_ATTRACTOR;
            end else begin
              fsm_state <= CALC_PERIOD_ATTRACTOR;
              start_count_period <= 1'b1;
              start_s1 <= 1'b1;
            end
          end
          FIND_NEXT_ATTRACTOR: begin
            if(~fifo_out_full) begin
              fifo_out_we <= 1'b1;
              data_out <= { state_net, transient, period };
              if(init_state < end_state_reg) begin
                init_state <= init_state + 5'd1;
                fsm_state <= RESET_NOS;
              end else begin
                fsm_state <= DONE;
                $display("%d: ID: %d DONE %d", 0, ID, (init_state + 1));
              end
            end 
          end
          DONE: begin
            if(fifo_in_empty) begin
              if(end_data_in) begin
                if(flag_wr) begin
                  if(fifo_out_empty) begin
                    done <= 1'b1;
                  end 
                  flag_wr <= 1'b0;
                end else begin
                  flag_wr <= 1'b1;
                end
              end 
              fsm_state <= DONE;
            end else begin
              fifo_in_re <= 1'b1;
              flag_rd <= 1'b0;
              init_state <= 5'd0;
              fsm_state <= GET_STATE;
            end
          end
        endcase
      end 
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      period_count <= 29'd0;
      transient_count <= 29'd0;
      pass_cycle <= 1'b0;
    end else begin
      if(start) begin
        if(reset_counts) begin
          period_count <= 29'd0;
          transient_count <= 29'd0;
          pass_cycle <= 1'b1;
        end else begin
          if(pass_cycle) begin
            if(start_count_period) begin
              period_count <= period_count + 29'd1;
            end 
            if(start_count_transient) begin
              transient_count <= transient_count + 29'd1;
              pass_cycle <= 1'b0;
            end 
          end else begin
            pass_cycle <= 1'b1;
          end
        end
      end 
    end
  end


  initial begin
    fifo_in_re = 0;
    start_s0 = 0;
    start_s1 = 0;
    reset_nos = 0;
    init_state = 0;
    fifo_out_we = 0;
    data_out = 0;
    done = 0;
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
    fsm_state = 0;
    flag_rd = 0;
    flag_wr = 0;
    pass_cycle_attractor = 0;
  end


endmodule



module network_graph
(
  input clk,
  input rst,
  input start,
  input reset_nos,
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
    .reset_nos(reset_nos),
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
    .reset_nos(reset_nos),
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
    .reset_nos(reset_nos),
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
    .reset_nos(reset_nos),
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
    .reset_nos(reset_nos),
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
  input reset_nos,
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
    if(rst) begin
      s0 <= 1'd0;
      pass <= 1'b0;
    end else begin
      if(reset_nos) begin
        s0 <= init_state;
        pass <= 1;
      end else begin
        if(start_s0) begin
          if(pass) begin
            s0 <=  ( s0 | gcra_s0 ) & ( ~ ccrm_s0 ) & ( ~ scip_s0 ) ;
            pass <= 0;
          end else begin
            pass <= 1;
          end
        end 
      end
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      s1 <= 1'd0;
    end else begin
      if(reset_nos) begin
        s1 <= init_state;
      end else begin
        if(start_s1) begin
          s1 <=  ( s1 | gcra_s1 ) & ( ~ ccrm_s1 ) & ( ~ scip_s1 ) ;
        end 
      end
    end
  end

  assign ctra_s0 = s0;
  assign ctra_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_gcra
(
  input clk,
  input start,
  input rst,
  input reset_nos,
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
    if(rst) begin
      s0 <= 1'd0;
      pass <= 1'b0;
    end else begin
      if(reset_nos) begin
        s0 <= init_state;
        pass <= 1;
      end else begin
        if(start_s0) begin
          if(pass) begin
            s0 <=  dnaa_s0 & ~ ctra_s0 ;
            pass <= 0;
          end else begin
            pass <= 1;
          end
        end 
      end
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      s1 <= 1'd0;
    end else begin
      if(reset_nos) begin
        s1 <= init_state;
      end else begin
        if(start_s1) begin
          s1 <=  dnaa_s1 & ~ ctra_s1 ;
        end 
      end
    end
  end

  assign gcra_s0 = s0;
  assign gcra_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_scip
(
  input clk,
  input start,
  input rst,
  input reset_nos,
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
    if(rst) begin
      s0 <= 1'd0;
      pass <= 1'b0;
    end else begin
      if(reset_nos) begin
        s0 <= init_state;
        pass <= 1;
      end else begin
        if(start_s0) begin
          if(pass) begin
            s0 <=  ctra_s0 & ~ dnaa_s0 ;
            pass <= 0;
          end else begin
            pass <= 1;
          end
        end 
      end
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      s1 <= 1'd0;
    end else begin
      if(reset_nos) begin
        s1 <= init_state;
      end else begin
        if(start_s1) begin
          s1 <=  ctra_s1 & ~ dnaa_s1 ;
        end 
      end
    end
  end

  assign scip_s0 = s0;
  assign scip_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_dnaa
(
  input clk,
  input start,
  input rst,
  input reset_nos,
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
    if(rst) begin
      s0 <= 1'd0;
      pass <= 1'b0;
    end else begin
      if(reset_nos) begin
        s0 <= init_state;
        pass <= 1;
      end else begin
        if(start_s0) begin
          if(pass) begin
            s0 <=  ctra_s0 & ccrm_s0 & ( ~ gcra_s0 ) & ( ~ s0 ) ;
            pass <= 0;
          end else begin
            pass <= 1;
          end
        end 
      end
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      s1 <= 1'd0;
    end else begin
      if(reset_nos) begin
        s1 <= init_state;
      end else begin
        if(start_s1) begin
          s1 <=  ctra_s1 & ccrm_s1 & ( ~ gcra_s1 ) & ( ~ s1 ) ;
        end 
      end
    end
  end

  assign dnaa_s0 = s0;
  assign dnaa_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_ccrm
(
  input clk,
  input start,
  input rst,
  input reset_nos,
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
    if(rst) begin
      s0 <= 1'd0;
      pass <= 1'b0;
    end else begin
      if(reset_nos) begin
        s0 <= init_state;
        pass <= 1;
      end else begin
        if(start_s0) begin
          if(pass) begin
            s0 <=  ctra_s0 & ( ~ s0 ) & ( ~ scip_s0 ) ;
            pass <= 0;
          end else begin
            pass <= 1;
          end
        end 
      end
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      s1 <= 1'd0;
    end else begin
      if(reset_nos) begin
        s1 <= init_state;
      end else begin
        if(start_s1) begin
          s1 <=  ctra_s1 & ( ~ s1 ) & ( ~ scip_s1 ) ;
        end 
      end
    end
  end

  assign ccrm_s0 = s0;
  assign ccrm_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module control_data_out
(
  input clk,
  input rst,
  input start,
  input grn_done_wr_data,
  input grn_available_write,
  output grn_request_write,
  output [88-1:0] grn_write_data,
  input [1-1:0] has_data,
  input [1-1:0] has_lst3_data,
  input [88-1:0] din0,
  input [1-1:0] task_done,
  output done,
  output reg [1-1:0] read_data_en
);


endmodule



module control_arbiter
(
  input clk,
  input rst,
  input start,
  input [8-1:0] has_data_out,
  input [8-1:0] has_lst3_data,
  input grn_available_write,
  output reg [8-1:0] read_data_en,
  output reg wr_fifo_out,
  output reg [3-1:0] mux_control
);

  localparam FSM_IDLE = 0;
  localparam FSM_RD_REQ = 1;
  localparam FSM_WR_REQ = 2;
  reg [3-1:0] fsm_state;
  reg [8-1:0] request;
  reg [3-1:0] grant_index_reg;
  wire [8-1:0] grant;
  wire [3-1:0] grant_index;
  wire grant_valid;

  arbiter
  #(
    .PORTS(8),
    .TYPE("ROUND_ROBIN"),
    .BLOCK("NONE"),
    .LSB_PRIORITY("LOW")
  )
  arbiter_inst
  (
    .clk(clk),
    .rst(rst),
    .request(request),
    .acknowledge(8'd0),
    .grant(grant),
    .grant_valid(grant_valid),
    .grant_encoded(grant_index)
  );


  always @(posedge clk) begin
    if(rst) begin
      fsm_state <= FSM_IDLE;
      request <= 8'd0;
      read_data_en <= 1'b0;
      grant_index_reg <= 3'd0;
      wr_fifo_out <= 1'b0;
      mux_control <= 3'd0;
    end else begin
      if(start) begin
        request <= 8'd0;
        read_data_en <= 1'b0;
        wr_fifo_out <= 1'b0;
        mux_control <= 3'd0;
        case(fsm_state)
          FSM_IDLE: begin
            if(|has_data_out && grn_available_write) begin
              request <= has_data_out;
              fsm_state <= FSM_RD_REQ;
            end 
          end
          FSM_RD_REQ: begin
            if(grant_valid) begin
              read_data_en <= grant;
              grant_index_reg <= grant_index;
              fsm_state <= FSM_WR_REQ;
            end 
          end
          FSM_WR_REQ: begin
            wr_fifo_out <= 1'b1;
            mux_control <= grant_index_reg;
            fsm_state <= FSM_IDLE;
          end
        endcase
      end 
    end
  end


  initial begin
    read_data_en = 0;
    wr_fifo_out = 0;
    mux_control = 0;
    fsm_state = 0;
    request = 0;
    grant_index_reg = 0;
  end


endmodule



module arbiter #
(
  parameter PORTS = 4,
  parameter TYPE = "ROUND_ROBIN",
  parameter BLOCK = "NONE",
  parameter LSB_PRIORITY = "LOW"
)
(
  input clk,
  input rst,
  input [PORTS-1:0] request,
  input [PORTS-1:0] acknowledge,
  output [PORTS-1:0] grant,
  output grant_valid,
  output [$clog2(PORTS)-1:0] grant_encoded
);

  reg [PORTS-1:0] grant_reg;
  reg [PORTS-1:0] grant_next;
  reg grant_valid_reg;
  reg grant_valid_next;
  reg [$clog2(PORTS)-1:0] grant_encoded_reg;
  reg [$clog2(PORTS)-1:0] grant_encoded_next;
  assign grant_valid = grant_valid_reg;
  assign grant = grant_reg;
  assign grant_encoded = grant_encoded_reg;
  wire request_valid;
  wire [$clog2(PORTS)-1:0] request_index;
  wire [PORTS-1:0] request_mask;

  priority_encoder
  #(
    .WIDTH(PORTS),
    .LSB_PRIORITY(LSB_PRIORITY)
  )
  priority_encoder_inst
  (
    .input_unencoded(request),
    .output_valid(request_valid),
    .output_encoded(request_index),
    .output_unencoded(request_mask)
  );

  reg [PORTS-1:0] mask_reg;
  reg [PORTS-1:0] mask_next;
  wire masked_request_valid;
  wire [$clog2(PORTS)-1:0] masked_request_index;
  wire [PORTS-1:0] masked_request_mask;

  priority_encoder
  #(
    .WIDTH(PORTS),
    .LSB_PRIORITY(LSB_PRIORITY)
  )
  priority_encoder_masked
  (
    .input_unencoded(request & mask_reg),
    .output_valid(masked_request_valid),
    .output_encoded(masked_request_index),
    .output_unencoded(masked_request_mask)
  );


  always @(*) begin
    grant_next = 0;
    grant_valid_next = 0;
    grant_encoded_next = 0;
    mask_next = mask_reg;
    if((BLOCK == "REQUEST") && grant_reg & request) begin
      grant_valid_next = grant_valid_reg;
      grant_next = grant_reg;
      grant_encoded_next = grant_encoded_reg;
    end else if((BLOCK == "ACKNOWLEDGE") && grant_valid && !(grant_reg & acknowledge)) begin
      grant_valid_next = grant_valid_reg;
      grant_next = grant_reg;
      grant_encoded_next = grant_encoded_reg;
    end else if(request_valid) begin
      if(TYPE == "PRIORITY") begin
        grant_valid_next = 1;
        grant_next = request_mask;
        grant_encoded_next = request_index;
      end else if(TYPE == "ROUND_ROBIN") begin
        if(masked_request_valid) begin
          grant_valid_next = 1;
          grant_next = masked_request_mask;
          grant_encoded_next = masked_request_index;
          if(LSB_PRIORITY == "LOW") begin
            mask_next = {PORTS{1'b1}} >> (PORTS - masked_request_index);
          end else begin
            mask_next = {PORTS{1'b1}} << (masked_request_index + 1);
          end
        end else begin
          grant_valid_next = 1;
          grant_next = request_mask;
          grant_encoded_next = request_index;
          if(LSB_PRIORITY == "LOW") begin
            mask_next = {PORTS{1'b1}} >> (PORTS - request_index);
          end else begin
            mask_next = {PORTS{1'b1}} << (request_index + 1);
          end
        end
      end 
    end 
  end


  always @(posedge clk) begin
    if(rst) begin
      grant_reg <= 0;
      grant_valid_reg <= 0;
      grant_encoded_reg <= 0;
      mask_reg <= 0;
    end else begin
      grant_reg <= grant_next;
      grant_valid_reg <= grant_valid_next;
      grant_encoded_reg <= grant_encoded_next;
      mask_reg <= mask_next;
    end
  end


  initial begin
    grant_reg = 0;
    grant_next = 0;
    grant_valid_reg = 0;
    grant_valid_next = 0;
    grant_encoded_reg = 0;
    grant_encoded_next = 0;
    mask_reg = 0;
    mask_next = 0;
  end


endmodule



module priority_encoder #
(
  parameter WIDTH = 4,
  parameter LSB_PRIORITY = "LOW"
)
(
  input [WIDTH-1:0] input_unencoded,
  output [1-1:0] output_valid,
  output [$clog2(WIDTH)-1:0] output_encoded,
  output [WIDTH-1:0] output_unencoded
);

  localparam W1 = 2**$clog2(WIDTH);
  localparam W2 = W1/2;

  generate if(WIDTH == 2) begin : if_width
    assign output_valid = input_unencoded[0] | input_unencoded[1];
    if(LSB_PRIORITY == "LOW") begin : if_low
      assign output_encoded = input_unencoded[1];
    end else begin : else_low
      assign output_encoded = ~input_unencoded[0];
    end
  end else begin : else_width
    wire [$clog2(W2)-1:0] out1;
    wire [$clog2(W2)-1:0] out2;
    wire valid1;
    wire valid2;
    wire [WIDTH-1:0] out_un;
    priority_encoder #(
                        .WIDTH(W2),
                        .LSB_PRIORITY(LSB_PRIORITY)
                    )
                    priority_encoder_inst1 (
                        .input_unencoded(input_unencoded[W2-1:0]),
                        .output_valid(valid1),
                        .output_encoded(out1),
                        .output_unencoded(out_un[W2-1:0])
                    );
                    priority_encoder #(
                        .WIDTH(W2),
                        .LSB_PRIORITY(LSB_PRIORITY)
                    )
                    priority_encoder_inst2 (
                        .input_unencoded({{W1-WIDTH{1'b0}}, input_unencoded[WIDTH-1:W2]}),
                        .output_valid(valid2),
                        .output_encoded(out2),
                        .output_unencoded(out_un[WIDTH-1:W2])
                    );
           assign output_valid = valid1 | valid2;
                    if (LSB_PRIORITY == "LOW") begin
                        assign output_encoded = valid2 ? {1'b1, out2} : {1'b0, out1};
                    end else begin
                        assign output_encoded = valid1 ? {1'b0, out1} : {1'b1, out2};
                    end
  end
  endgenerate

  assign output_unencoded = 1 << output_encoded;

endmodule



module mux8x1 #
(
  parameter WIDTH = 88
)
(
  input [WIDTH-1:0] in0,
  input [WIDTH-1:0] in1,
  input [WIDTH-1:0] in2,
  input [WIDTH-1:0] in3,
  input [WIDTH-1:0] in4,
  input [WIDTH-1:0] in5,
  input [WIDTH-1:0] in6,
  input [WIDTH-1:0] in7,
  input [3-1:0] s,
  output [WIDTH-1:0] out
);

  wire [WIDTH-1:0] ins [0:8-1];
  assign ins[0] = in0;
  assign ins[1] = in1;
  assign ins[2] = in2;
  assign ins[3] = in3;
  assign ins[4] = in4;
  assign ins[5] = in5;
  assign ins[6] = in6;
  assign ins[7] = in7;
  assign out = ins[s];

endmodule



module control_fifo_out
(
  input clk,
  input rst,
  input start,
  input [8-1:0] task_done,
  input wr_en,
  input [88-1:0] wr_data,
  input grn_available_write,
  input grn_done_wr_data,
  output reg grn_request_write,
  output reg [512-1:0] grn_write_data,
  output reg done
);

  reg [3-1:0] count_empty;
  reg [2-1:0] fms_cs;
  localparam [2-1:0] FSM_FIFO_WR0 = 0;
  localparam [2-1:0] FSM_DONE = 1;

  always @(posedge clk) begin
    if(rst) begin
      fms_cs <= FSM_FIFO_WR0;
      grn_request_write <= 0;
      done <= 0;
      count_empty <= 0;
    end else begin
      if(start) begin
        grn_request_write <= 0;
        case(fms_cs)
          FSM_FIFO_WR0: begin
            if(wr_en) begin
              grn_write_data <= wr_data;
              grn_request_write <= 1;
            end else if(&task_done && grn_done_wr_data) begin
              fms_cs <= FSM_DONE;
            end 
          end
        endcase
        FSM_DONE: begin
          done <= 1;
        end
      end 
    end
  end


  initial begin
    grn_request_write = 0;
    grn_write_data = 0;
    done = 0;
    count_empty = 0;
    fms_cs = 0;
  end


endmodule



module grn_aws_1
(
  input clk,
  input rst,
  input start,
  input grn_done_rd_data,
  input grn_done_wr_data,
  output grn_request_read,
  input grn_read_data_valid,
  input [32-1:0] grn_read_data,
  input grn_available_write,
  output grn_request_write,
  output [88-1:0] grn_write_data,
  output grn_done
);

  wire data_in_valid;
  wire control_data_in_done;
  wire [88-1:0] data_out0;
  wire [32-1:0] data_in;
  wire [1-1:0] read_data_en;
  wire [1-1:0] has_data;
  wire [1-1:0] has_lst3_data;
  wire [1-1:0] task_done;

  control_data_in
  control_data_in
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .grn_read_data_valid(grn_read_data_valid),
    .grn_read_data(grn_read_data),
    .grn_done_rd_data(grn_done_rd_data),
    .grn_request_read(grn_request_read),
    .data_valid(data_in_valid),
    .data_out(data_in),
    .done(control_data_in_done)
  );


  regulator_network
  #(
    .ID(1)
  )
  rn0
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in),
    .control_data_in_done(control_data_in_done),
    .read_data_en(read_data_en[0]),
    .has_data_out(has_data[0]),
    .has_lst3_data_out(has_lst3_data[0]),
    .data_out(data_out0),
    .task_done(task_done[0])
  );


  control_data_out
  control_data_out
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .grn_done_wr_data(grn_done_wr_data),
    .grn_available_write(grn_available_write),
    .grn_request_write(grn_request_write),
    .grn_write_data(grn_write_data),
    .din0(data_out0),
    .read_data_en(read_data_en),
    .task_done(task_done),
    .done(grn_done)
  );


  initial begin
    $dumpfile("uut.vcd");
    $dumpvars(0, "grn_aws");
  end


endmodule

