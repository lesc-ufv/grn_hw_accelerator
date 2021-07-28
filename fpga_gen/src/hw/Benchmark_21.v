

module gnr_acc
(
  input clk,
  input rst,
  input start,
  input [5-1:0] acc_user_done_rd_data,
  input [5-1:0] acc_user_done_wr_data,
  output [5-1:0] acc_user_request_read,
  input [5-1:0] acc_user_read_data_valid,
  input [320-1:0] acc_user_read_data,
  input [5-1:0] acc_user_available_write,
  output [5-1:0] acc_user_request_write,
  output [520-1:0] acc_user_write_data,
  output acc_user_done
);

  wire [5-1:0] gnr_done;

  gnr_aws_8
  gnr_aws_8_0
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .gnr_done_rd_data(acc_user_done_rd_data[0]),
    .gnr_done_wr_data(acc_user_done_wr_data[0]),
    .gnr_request_read(acc_user_request_read[0]),
    .gnr_read_data_valid(acc_user_read_data_valid[0]),
    .gnr_read_data(acc_user_read_data[511:0]),
    .gnr_available_write(acc_user_available_write[0]),
    .gnr_request_write(acc_user_request_write[0]),
    .gnr_write_data(acc_user_write_data[511:0]),
    .gnr_done(gnr_done[0])
  );


  gnr_aws_8
  gnr_aws_8_1
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .gnr_done_rd_data(acc_user_done_rd_data[1]),
    .gnr_done_wr_data(acc_user_done_wr_data[1]),
    .gnr_request_read(acc_user_request_read[1]),
    .gnr_read_data_valid(acc_user_read_data_valid[1]),
    .gnr_read_data(acc_user_read_data[1023:512]),
    .gnr_available_write(acc_user_available_write[1]),
    .gnr_request_write(acc_user_request_write[1]),
    .gnr_write_data(acc_user_write_data[1023:512]),
    .gnr_done(gnr_done[1])
  );


  gnr_aws_8
  gnr_aws_8_2
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .gnr_done_rd_data(acc_user_done_rd_data[2]),
    .gnr_done_wr_data(acc_user_done_wr_data[2]),
    .gnr_request_read(acc_user_request_read[2]),
    .gnr_read_data_valid(acc_user_read_data_valid[2]),
    .gnr_read_data(acc_user_read_data[1535:1024]),
    .gnr_available_write(acc_user_available_write[2]),
    .gnr_request_write(acc_user_request_write[2]),
    .gnr_write_data(acc_user_write_data[1535:1024]),
    .gnr_done(gnr_done[2])
  );


  gnr_aws_8
  gnr_aws_8_3
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .gnr_done_rd_data(acc_user_done_rd_data[3]),
    .gnr_done_wr_data(acc_user_done_wr_data[3]),
    .gnr_request_read(acc_user_request_read[3]),
    .gnr_read_data_valid(acc_user_read_data_valid[3]),
    .gnr_read_data(acc_user_read_data[2047:1536]),
    .gnr_available_write(acc_user_available_write[3]),
    .gnr_request_write(acc_user_request_write[3]),
    .gnr_write_data(acc_user_write_data[2047:1536]),
    .gnr_done(gnr_done[3])
  );


  gnr_aws_1
  gnr_aws_1_4
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .gnr_done_rd_data(acc_user_done_rd_data[4]),
    .gnr_done_wr_data(acc_user_done_wr_data[4]),
    .gnr_request_read(acc_user_request_read[4]),
    .gnr_read_data_valid(acc_user_read_data_valid[4]),
    .gnr_read_data(acc_user_read_data[2559:2048]),
    .gnr_available_write(acc_user_available_write[4]),
    .gnr_request_write(acc_user_request_write[4]),
    .gnr_write_data(acc_user_write_data[2559:2048]),
    .gnr_done(gnr_done[4])
  );

  assign acc_user_done = &gnr_done;

endmodule



module gnr_aws_8
(
  input clk,
  input rst,
  input start,
  input gnr_done_rd_data,
  input gnr_done_wr_data,
  output gnr_request_read,
  input gnr_read_data_valid,
  input [64-1:0] gnr_read_data,
  input gnr_available_write,
  output gnr_request_write,
  output [104-1:0] gnr_write_data,
  output gnr_done
);

  wire control_data_in_done;
  wire [104-1:0] data_out0;
  wire [104-1:0] data_out1;
  wire [104-1:0] data_out2;
  wire [104-1:0] data_out3;
  wire [104-1:0] data_out4;
  wire [104-1:0] data_out5;
  wire [104-1:0] data_out6;
  wire [104-1:0] data_out7;
  wire [64-1:0] data_in;
  wire data_in_valid;
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
    .gnr_read_data_valid(gnr_read_data_valid),
    .gnr_read_data(gnr_read_data),
    .gnr_done_rd_data(gnr_done_rd_data),
    .gnr_request_read(gnr_request_read),
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


endmodule



module control_data_in
(
  input clk,
  input rst,
  input start,
  input gnr_read_data_valid,
  input [64-1:0] gnr_read_data,
  input gnr_done_rd_data,
  output reg gnr_request_read,
  output reg data_valid,
  output reg [64-1:0] data_out,
  output reg done
);

  localparam [2-1:0] FSM_SEND_DATA = 0;
  localparam [2-1:0] FSM_DONE = 1;
  reg [2-1:0] fms_cs;

  always @(posedge clk) begin
    if(rst) begin
      gnr_request_read <= 0;
      done <= 0;
      data_valid <= 0;
      fms_cs <= FSM_SEND_DATA;
    end else begin
      if(start) begin
        data_valid <= 0;
        gnr_request_read <= 0;
        case(fms_cs)
          FSM_SEND_DATA: begin
            if(gnr_done_rd_data) begin
              fms_cs <= FSM_DONE;
            end else if(gnr_read_data_valid) begin
              data_out <= gnr_read_data;
              gnr_request_read <= 1;
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
    gnr_request_read = 0;
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
  input [64-1:0] data_in,
  input end_data_in,
  input read_data_en,
  output has_data_out,
  output has_lst3_data_out,
  output [104-1:0] data_out,
  output task_done
);

  wire [21-1:0] s0;
  wire [21-1:0] s1;
  wire start_s0;
  wire start_s1;
  wire reset_nos;
  wire [21-1:0] init_state;
  wire fifo_out_we;
  wire [104-1:0] fifo_out_data_in;
  wire fifo_out_empty;
  wire fifo_out_full;
  wire fifo_out_full_almostfull;
  wire fifo_in_we;
  wire [48-1:0] fifo_in_data_in;
  wire fifo_in_re;
  wire [48-1:0] fifo_in_data_out;
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
    .FIFO_WIDTH(48),
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


  control_gnr
  #(
    .ID(ID)
  )
  control_gnr
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
  input [64-1:0] data_in,
  input fifo_in_full,
  input fifo_in_amostfull,
  output reg fifo_in_we,
  output reg [63-1:0] fifo_in_data
);


  always @(posedge clk) begin
    if(rst) begin
      fifo_in_we <= 1'b0;
      fifo_in_data <= 63'd0;
    end else begin
      if(start) begin
        fifo_in_we <= 1'b0;
        if(data_in_valid && (data_in[0:0] == ID) && ~fifo_in_full) begin
          fifo_in_we <= 1'b1;
          fifo_in_data <= data_in[63:1];
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



module control_gnr #
(
  parameter ID = 0
)
(
  input clk,
  input rst,
  input start,
  input [21-1:0] s0,
  input [21-1:0] s1,
  input fifo_out_full,
  input fifo_in_empty,
  input [42-1:0] fifo_data_in,
  input end_data_in,
  output reg fifo_in_re,
  output reg start_s0,
  output reg start_s1,
  output reg reset_nos,
  output reg [21-1:0] init_state,
  output reg fifo_out_we,
  input fifo_out_empty,
  output reg [79-1:0] data_out,
  output reg done
);

  reg [21-1:0] state_net;
  reg [29-1:0] period;
  reg [29-1:0] transient;
  reg [21-1:0] end_state_reg;
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
      init_state <= 21'd0;
      start_count_period <= 1'b0;
      start_count_transient <= 1'b0;
      done <= 1'b0;
      start_s0 <= 1'b0;
      start_s1 <= 1'b0;
      fifo_out_we <= 1'b0;
      reset_counts <= 1'b0;
      state_net <= 21'd0;
      period <= 29'd0;
      transient <= 29'd0;
      end_state_reg <= 21'd0;
      fifo_in_re <= 1'b0;
      flag_rd <= 1'b0;
      flag_wr <= 1'b0;
      reset_nos <= 1'b0;
      data_out <= 79'd0;
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
              init_state <= fifo_data_in[20:0];
              end_state_reg <= fifo_data_in[41:21];
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
                init_state <= init_state + 21'd1;
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
              init_state <= 21'd0;
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
  input [21-1:0] init_state,
  output [21-1:0] s0,
  output [21-1:0] s1
);

  wire akt_s0;
  wire akt_s1;
  wire bcatenin_s0;
  wire bcatenin_s1;
  wire ctl_s0;
  wire ctl_s1;
  wire cyclind1_s0;
  wire cyclind1_s1;
  wire gsk3b_s0;
  wire gsk3b_s1;
  wire ifng_s0;
  wire ifng_s1;
  wire ikk_s0;
  wire ikk_s1;
  wire il10_s0;
  wire il10_s1;
  wire jak_s0;
  wire jak_s1;
  wire jnk_s0;
  wire jnk_s1;
  wire jun_s0;
  wire jun_s1;
  wire mac_s0;
  wire mac_s1;
  wire mdm2_s0;
  wire mdm2_s1;
  wire nfkb_s0;
  wire nfkb_s1;
  wire p21_s0;
  wire p21_s1;
  wire p53_s0;
  wire p53_s1;
  wire pten_s0;
  wire pten_s1;
  wire socs_s0;
  wire socs_s1;
  wire stat3_s0;
  wire stat3_s1;
  wire tnfr_s0;
  wire tnfr_s1;
  wire proliferation_s0;
  wire proliferation_s1;

  no_akt
  _no_akt
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[0]),
    .pten_s0(pten_s0),
    .pten_s1(pten_s1),
    .s0(s0[0]),
    .s1(s1[0]),
    .akt_s0(akt_s0),
    .akt_s1(akt_s1)
  );


  no_bcatenin
  _no_bcatenin
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[1]),
    .p53_s0(p53_s0),
    .p53_s1(p53_s1),
    .gsk3b_s0(gsk3b_s0),
    .gsk3b_s1(gsk3b_s1),
    .s0(s0[1]),
    .s1(s1[1]),
    .bcatenin_s0(bcatenin_s0),
    .bcatenin_s1(bcatenin_s1)
  );


  no_ctl
  _no_ctl
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[2]),
    .ifng_s0(ifng_s0),
    .ifng_s1(ifng_s1),
    .il10_s0(il10_s0),
    .il10_s1(il10_s1),
    .s0(s0[2]),
    .s1(s1[2]),
    .ctl_s0(ctl_s0),
    .ctl_s1(ctl_s1)
  );


  no_cyclind1
  _no_cyclind1
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[3]),
    .bcatenin_s0(bcatenin_s0),
    .bcatenin_s1(bcatenin_s1),
    .stat3_s0(stat3_s0),
    .stat3_s1(stat3_s1),
    .jun_s0(jun_s0),
    .jun_s1(jun_s1),
    .gsk3b_s0(gsk3b_s0),
    .gsk3b_s1(gsk3b_s1),
    .s0(s0[3]),
    .s1(s1[3]),
    .cyclind1_s0(cyclind1_s0),
    .cyclind1_s1(cyclind1_s1)
  );


  no_gsk3b
  _no_gsk3b
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[4]),
    .tnfr_s0(tnfr_s0),
    .tnfr_s1(tnfr_s1),
    .akt_s0(akt_s0),
    .akt_s1(akt_s1),
    .s0(s0[4]),
    .s1(s1[4]),
    .gsk3b_s0(gsk3b_s0),
    .gsk3b_s1(gsk3b_s1)
  );


  no_ifng
  _no_ifng
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[5]),
    .ctl_s0(ctl_s0),
    .ctl_s1(ctl_s1),
    .s0(s0[5]),
    .s1(s1[5]),
    .ifng_s0(ifng_s0),
    .ifng_s1(ifng_s1)
  );


  no_ikk
  _no_ikk
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[6]),
    .akt_s0(akt_s0),
    .akt_s1(akt_s1),
    .tnfr_s0(tnfr_s0),
    .tnfr_s1(tnfr_s1),
    .s0(s0[6]),
    .s1(s1[6]),
    .ikk_s0(ikk_s0),
    .ikk_s1(ikk_s1)
  );


  no_il10
  _no_il10
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[7]),
    .ifng_s0(ifng_s0),
    .ifng_s1(ifng_s1),
    .s0(s0[7]),
    .s1(s1[7]),
    .il10_s0(il10_s0),
    .il10_s1(il10_s1)
  );


  no_jak
  _no_jak
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[8]),
    .socs_s0(socs_s0),
    .socs_s1(socs_s1),
    .s0(s0[8]),
    .s1(s1[8]),
    .jak_s0(jak_s0),
    .jak_s1(jak_s1)
  );


  no_jnk
  _no_jnk
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[9]),
    .tnfr_s0(tnfr_s0),
    .tnfr_s1(tnfr_s1),
    .s0(s0[9]),
    .s1(s1[9]),
    .jnk_s0(jnk_s0),
    .jnk_s1(jnk_s1)
  );


  no_jun
  _no_jun
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[10]),
    .jnk_s0(jnk_s0),
    .jnk_s1(jnk_s1),
    .gsk3b_s0(gsk3b_s0),
    .gsk3b_s1(gsk3b_s1),
    .s0(s0[10]),
    .s1(s1[10]),
    .jun_s0(jun_s0),
    .jun_s1(jun_s1)
  );


  no_mac
  _no_mac
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[11]),
    .ifng_s0(ifng_s0),
    .ifng_s1(ifng_s1),
    .nfkb_s0(nfkb_s0),
    .nfkb_s1(nfkb_s1),
    .il10_s0(il10_s0),
    .il10_s1(il10_s1),
    .s0(s0[11]),
    .s1(s1[11]),
    .mac_s0(mac_s0),
    .mac_s1(mac_s1)
  );


  no_mdm2
  _no_mdm2
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[12]),
    .p53_s0(p53_s0),
    .p53_s1(p53_s1),
    .akt_s0(akt_s0),
    .akt_s1(akt_s1),
    .gsk3b_s0(gsk3b_s0),
    .gsk3b_s1(gsk3b_s1),
    .s0(s0[12]),
    .s1(s1[12]),
    .mdm2_s0(mdm2_s0),
    .mdm2_s1(mdm2_s1)
  );


  no_nfkb
  _no_nfkb
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[13]),
    .ikk_s0(ikk_s0),
    .ikk_s1(ikk_s1),
    .s0(s0[13]),
    .s1(s1[13]),
    .nfkb_s0(nfkb_s0),
    .nfkb_s1(nfkb_s1)
  );


  no_p21
  _no_p21
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[14]),
    .p53_s0(p53_s0),
    .p53_s1(p53_s1),
    .gsk3b_s0(gsk3b_s0),
    .gsk3b_s1(gsk3b_s1),
    .s0(s0[14]),
    .s1(s1[14]),
    .p21_s0(p21_s0),
    .p21_s1(p21_s1)
  );


  no_p53
  _no_p53
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[15]),
    .pten_s0(pten_s0),
    .pten_s1(pten_s1),
    .jnk_s0(jnk_s0),
    .jnk_s1(jnk_s1),
    .mdm2_s0(mdm2_s0),
    .mdm2_s1(mdm2_s1),
    .s0(s0[15]),
    .s1(s1[15]),
    .p53_s0(p53_s0),
    .p53_s1(p53_s1)
  );


  no_pten
  _no_pten
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[16]),
    .p53_s0(p53_s0),
    .p53_s1(p53_s1),
    .nfkb_s0(nfkb_s0),
    .nfkb_s1(nfkb_s1),
    .jun_s0(jun_s0),
    .jun_s1(jun_s1),
    .s0(s0[16]),
    .s1(s1[16]),
    .pten_s0(pten_s0),
    .pten_s1(pten_s1)
  );


  no_socs
  _no_socs
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[17]),
    .stat3_s0(stat3_s0),
    .stat3_s1(stat3_s1),
    .s0(s0[17]),
    .s1(s1[17]),
    .socs_s0(socs_s0),
    .socs_s1(socs_s1)
  );


  no_stat3
  _no_stat3
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[18]),
    .jak_s0(jak_s0),
    .jak_s1(jak_s1),
    .s0(s0[18]),
    .s1(s1[18]),
    .stat3_s0(stat3_s0),
    .stat3_s1(stat3_s1)
  );


  no_tnfr
  _no_tnfr
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[19]),
    .mac_s0(mac_s0),
    .mac_s1(mac_s1),
    .s0(s0[19]),
    .s1(s1[19]),
    .tnfr_s0(tnfr_s0),
    .tnfr_s1(tnfr_s1)
  );


  no_proliferation
  _no_proliferation
  (
    .clk(clk),
    .start(start),
    .rst(rst),
    .reset_nos(reset_nos),
    .start_s0(start_s0),
    .start_s1(start_s1),
    .init_state(init_state[20]),
    .cyclind1_s0(cyclind1_s0),
    .cyclind1_s1(cyclind1_s1),
    .p21_s0(p21_s0),
    .p21_s1(p21_s1),
    .s0(s0[20]),
    .s1(s1[20]),
    .proliferation_s0(proliferation_s0),
    .proliferation_s1(proliferation_s1)
  );


endmodule



module no_akt
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] pten_s0,
  input [1-1:0] pten_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] akt_s0,
  output [1-1:0] akt_s1
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
            s0 <=  ~ pten_s0 ;
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
          s1 <=  ~ pten_s1 ;
        end 
      end
    end
  end

  assign akt_s0 = s0;
  assign akt_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_bcatenin
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] p53_s0,
  input [1-1:0] p53_s1,
  input [1-1:0] gsk3b_s0,
  input [1-1:0] gsk3b_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] bcatenin_s0,
  output [1-1:0] bcatenin_s1
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
            s0 <=  ~ ( p53_s0 & gsk3b_s0 ) ;
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
          s1 <=  ~ ( p53_s1 & gsk3b_s1 ) ;
        end 
      end
    end
  end

  assign bcatenin_s0 = s0;
  assign bcatenin_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_ctl
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ifng_s0,
  input [1-1:0] ifng_s1,
  input [1-1:0] il10_s0,
  input [1-1:0] il10_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] ctl_s0,
  output [1-1:0] ctl_s1
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
            s0 <=  ifng_s0 & ~ il10_s0 ;
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
          s1 <=  ifng_s1 & ~ il10_s1 ;
        end 
      end
    end
  end

  assign ctl_s0 = s0;
  assign ctl_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_cyclind1
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] bcatenin_s0,
  input [1-1:0] bcatenin_s1,
  input [1-1:0] stat3_s0,
  input [1-1:0] stat3_s1,
  input [1-1:0] jun_s0,
  input [1-1:0] jun_s1,
  input [1-1:0] gsk3b_s0,
  input [1-1:0] gsk3b_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] cyclind1_s0,
  output [1-1:0] cyclind1_s1
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
            s0 <=  ( bcatenin_s0 | stat3_s0 | jun_s0 ) & ~ gsk3b_s0 ;
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
          s1 <=  ( bcatenin_s1 | stat3_s1 | jun_s1 ) & ~ gsk3b_s1 ;
        end 
      end
    end
  end

  assign cyclind1_s0 = s0;
  assign cyclind1_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_gsk3b
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] tnfr_s0,
  input [1-1:0] tnfr_s1,
  input [1-1:0] akt_s0,
  input [1-1:0] akt_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] gsk3b_s0,
  output [1-1:0] gsk3b_s1
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
            s0 <=  ~ ( tnfr_s0 | akt_s0 ) ;
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
          s1 <=  ~ ( tnfr_s1 | akt_s1 ) ;
        end 
      end
    end
  end

  assign gsk3b_s0 = s0;
  assign gsk3b_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_ifng
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ctl_s0,
  input [1-1:0] ctl_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] ifng_s0,
  output [1-1:0] ifng_s1
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
            s0 <=  ctl_s0 ;
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
          s1 <=  ctl_s1 ;
        end 
      end
    end
  end

  assign ifng_s0 = s0;
  assign ifng_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_ikk
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] akt_s0,
  input [1-1:0] akt_s1,
  input [1-1:0] tnfr_s0,
  input [1-1:0] tnfr_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] ikk_s0,
  output [1-1:0] ikk_s1
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
            s0 <=  akt_s0 | tnfr_s0 ;
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
          s1 <=  akt_s1 | tnfr_s1 ;
        end 
      end
    end
  end

  assign ikk_s0 = s0;
  assign ikk_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_il10
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ifng_s0,
  input [1-1:0] ifng_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] il10_s0,
  output [1-1:0] il10_s1
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
            s0 <=  ~ ifng_s0 ;
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
          s1 <=  ~ ifng_s1 ;
        end 
      end
    end
  end

  assign il10_s0 = s0;
  assign il10_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_jak
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] socs_s0,
  input [1-1:0] socs_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] jak_s0,
  output [1-1:0] jak_s1
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
            s0 <=  ~ socs_s0 ;
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
          s1 <=  ~ socs_s1 ;
        end 
      end
    end
  end

  assign jak_s0 = s0;
  assign jak_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_jnk
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] tnfr_s0,
  input [1-1:0] tnfr_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] jnk_s0,
  output [1-1:0] jnk_s1
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
            s0 <=  tnfr_s0 ;
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
          s1 <=  tnfr_s1 ;
        end 
      end
    end
  end

  assign jnk_s0 = s0;
  assign jnk_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_jun
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] jnk_s0,
  input [1-1:0] jnk_s1,
  input [1-1:0] gsk3b_s0,
  input [1-1:0] gsk3b_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] jun_s0,
  output [1-1:0] jun_s1
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
            s0 <=  jnk_s0 & ~ gsk3b_s0 ;
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
          s1 <=  jnk_s1 & ~ gsk3b_s1 ;
        end 
      end
    end
  end

  assign jun_s0 = s0;
  assign jun_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_mac
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ifng_s0,
  input [1-1:0] ifng_s1,
  input [1-1:0] nfkb_s0,
  input [1-1:0] nfkb_s1,
  input [1-1:0] il10_s0,
  input [1-1:0] il10_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] mac_s0,
  output [1-1:0] mac_s1
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
            s0 <=  ( ifng_s0 | nfkb_s0 ) & ~ il10_s0 ;
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
          s1 <=  ( ifng_s1 | nfkb_s1 ) & ~ il10_s1 ;
        end 
      end
    end
  end

  assign mac_s0 = s0;
  assign mac_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_mdm2
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] p53_s0,
  input [1-1:0] p53_s1,
  input [1-1:0] akt_s0,
  input [1-1:0] akt_s1,
  input [1-1:0] gsk3b_s0,
  input [1-1:0] gsk3b_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] mdm2_s0,
  output [1-1:0] mdm2_s1
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
            s0 <=  ( p53_s0 & akt_s0 ) & ~ gsk3b_s0 ;
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
          s1 <=  ( p53_s1 & akt_s1 ) & ~ gsk3b_s1 ;
        end 
      end
    end
  end

  assign mdm2_s0 = s0;
  assign mdm2_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_nfkb
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] ikk_s0,
  input [1-1:0] ikk_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] nfkb_s0,
  output [1-1:0] nfkb_s1
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
            s0 <=  ikk_s0 ;
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
          s1 <=  ikk_s1 ;
        end 
      end
    end
  end

  assign nfkb_s0 = s0;
  assign nfkb_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_p21
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] p53_s0,
  input [1-1:0] p53_s1,
  input [1-1:0] gsk3b_s0,
  input [1-1:0] gsk3b_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] p21_s0,
  output [1-1:0] p21_s1
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
            s0 <=  p53_s0 & ~ gsk3b_s0 ;
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
          s1 <=  p53_s1 & ~ gsk3b_s1 ;
        end 
      end
    end
  end

  assign p21_s0 = s0;
  assign p21_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_p53
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] pten_s0,
  input [1-1:0] pten_s1,
  input [1-1:0] jnk_s0,
  input [1-1:0] jnk_s1,
  input [1-1:0] mdm2_s0,
  input [1-1:0] mdm2_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] p53_s0,
  output [1-1:0] p53_s1
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
            s0 <=  ( pten_s0 | jnk_s0 ) & ~ mdm2_s0 ;
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
          s1 <=  ( pten_s1 | jnk_s1 ) & ~ mdm2_s1 ;
        end 
      end
    end
  end

  assign p53_s0 = s0;
  assign p53_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_pten
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] p53_s0,
  input [1-1:0] p53_s1,
  input [1-1:0] nfkb_s0,
  input [1-1:0] nfkb_s1,
  input [1-1:0] jun_s0,
  input [1-1:0] jun_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] pten_s0,
  output [1-1:0] pten_s1
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
            s0 <=  p53_s0 & ~ ( nfkb_s0 | jun_s0 ) ;
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
          s1 <=  p53_s1 & ~ ( nfkb_s1 | jun_s1 ) ;
        end 
      end
    end
  end

  assign pten_s0 = s0;
  assign pten_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_socs
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] stat3_s0,
  input [1-1:0] stat3_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] socs_s0,
  output [1-1:0] socs_s1
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
            s0 <=  stat3_s0 ;
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
          s1 <=  stat3_s1 ;
        end 
      end
    end
  end

  assign socs_s0 = s0;
  assign socs_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_stat3
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] jak_s0,
  input [1-1:0] jak_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] stat3_s0,
  output [1-1:0] stat3_s1
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
            s0 <=  jak_s0 ;
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
          s1 <=  jak_s1 ;
        end 
      end
    end
  end

  assign stat3_s0 = s0;
  assign stat3_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_tnfr
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] mac_s0,
  input [1-1:0] mac_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] tnfr_s0,
  output [1-1:0] tnfr_s1
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
            s0 <=  mac_s0 ;
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
          s1 <=  mac_s1 ;
        end 
      end
    end
  end

  assign tnfr_s0 = s0;
  assign tnfr_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module no_proliferation
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] cyclind1_s0,
  input [1-1:0] cyclind1_s1,
  input [1-1:0] p21_s0,
  input [1-1:0] p21_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] proliferation_s0,
  output [1-1:0] proliferation_s1
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
            s0 <=  cyclind1_s0 & ~ p21_s0 ;
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
          s1 <=  cyclind1_s1 & ~ p21_s1 ;
        end 
      end
    end
  end

  assign proliferation_s0 = s0;
  assign proliferation_s1 = s1;

  initial begin
    pass = 0;
    s0 = 0;
    s1 = 0;
  end


endmodule



module gnr_aws_1
(
  input clk,
  input rst,
  input start,
  input gnr_done_rd_data,
  input gnr_done_wr_data,
  output gnr_request_read,
  input gnr_read_data_valid,
  input [64-1:0] gnr_read_data,
  input gnr_available_write,
  output gnr_request_write,
  output [104-1:0] gnr_write_data,
  output gnr_done
);

  wire control_data_in_done;
  wire [104-1:0] data_out0;
  wire [64-1:0] data_in;
  wire data_in_valid;
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
    .gnr_read_data_valid(gnr_read_data_valid),
    .gnr_read_data(gnr_read_data),
    .gnr_done_rd_data(gnr_done_rd_data),
    .gnr_request_read(gnr_request_read),
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


endmodule

