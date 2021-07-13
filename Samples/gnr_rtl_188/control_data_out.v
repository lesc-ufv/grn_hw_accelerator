
module control_data_out
(
  input clk,
  input rst,
  input start,
  input [32-1:0] num_data_out,
  input fifo_out_full,
  input fifo_out_almostfull,
  input fifo_out_empty,
  input [32-1:0] has_data,
  input [32-1:0] has_lst3_data,
  input [256-1:0] din0,
  input [256-1:0] din1,
  input [256-1:0] din2,
  input [256-1:0] din3,
  input [256-1:0] din4,
  input [256-1:0] din5,
  input [256-1:0] din6,
  input [256-1:0] din7,
  input [256-1:0] din8,
  input [256-1:0] din9,
  input [256-1:0] din10,
  input [256-1:0] din11,
  input [256-1:0] din12,
  input [256-1:0] din13,
  input [256-1:0] din14,
  input [256-1:0] din15,
  input [256-1:0] din16,
  input [256-1:0] din17,
  input [256-1:0] din18,
  input [256-1:0] din19,
  input [256-1:0] din20,
  input [256-1:0] din21,
  input [256-1:0] din22,
  input [256-1:0] din23,
  input [256-1:0] din24,
  input [256-1:0] din25,
  input [256-1:0] din26,
  input [256-1:0] din27,
  input [256-1:0] din28,
  input [256-1:0] din29,
  input [256-1:0] din30,
  input [256-1:0] din31,
  input [32-1:0] task_done,
  output wr_fifo_out_en,
  output [512-1:0] wr_fifo_out_data,
  output [32-1:0] read_data_en,
  output done
);

  wire wr_fifo_out;
  wire [5-1:0] mux_control;
  wire [256-1:0] mux_data_out;

  control_arbiter
  control_arbiter
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .has_data_out(has_data),
    .has_lst3_data(has_lst3_data),
    .fifo_out_full(fifo_out_full),
    .read_data_en(read_data_en),
    .wr_fifo_out(wr_fifo_out),
    .mux_control(mux_control)
  );


  mux32x1
  #(
    .WIDTH(256)
  )
  mux_wr_fifo_out
  (
    .in0(din0),
    .in1(din1),
    .in2(din2),
    .in3(din3),
    .in4(din4),
    .in5(din5),
    .in6(din6),
    .in7(din7),
    .in8(din8),
    .in9(din9),
    .in10(din10),
    .in11(din11),
    .in12(din12),
    .in13(din13),
    .in14(din14),
    .in15(din15),
    .in16(din16),
    .in17(din17),
    .in18(din18),
    .in19(din19),
    .in20(din20),
    .in21(din21),
    .in22(din22),
    .in23(din23),
    .in24(din24),
    .in25(din25),
    .in26(din26),
    .in27(din27),
    .in28(din28),
    .in29(din29),
    .in30(din30),
    .in31(din31),
    .s(mux_control),
    .out(mux_data_out)
  );


  control_fifo_out
  control_fifo_out
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .num_data_out(num_data_out),
    .task_done(task_done),
    .wr_en(wr_fifo_out),
    .wr_data(mux_data_out),
    .fifoout_full(fifo_out_full),
    .fifoout_almostfull(fifo_out_almostfull),
    .fifoout_empty(fifo_out_empty),
    .wr_fifoout_en(wr_fifo_out_en),
    .wr_fifoout_data(wr_fifo_out_data),
    .done(done)
  );


endmodule
