
module regulator_network #
(
  parameter ID = 0
)
(
  input clk,
  input rst,
  input start,
  input data_in_valid,
  input [382-1:0] data_in,
  input end_data_in,
  input read_data_en,
  output has_data_out,
  output has_lst3_data_out,
  output [246-1:0] data_out,
  output task_done
);

  wire [188-1:0] s0;
  wire [188-1:0] s1;
  wire start_s0;
  wire start_s1;
  wire reset_nos;
  wire [188-1:0] init_state;
  wire fifo_out_we;
  wire [246-1:0] fifo_out_data_in;
  wire fifo_out_empty;
  wire fifo_out_full;
  wire fifo_out_full_almostfull;
  wire fifo_in_we;
  wire [376-1:0] fifo_in_data_in;
  wire fifo_in_re;
  wire [376-1:0] fifo_in_data_out;
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
    .FIFO_WIDTH(376),
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
    .FIFO_WIDTH(246),
    .FIFO_DEPTH_BITS(12),
    .FIFO_ALMOSTFULL_THRESHOLD(4094),
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
