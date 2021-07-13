
module gnr_harp
(
  input clk_gnr,
  input rst,
  input start,
  input [512-1:0] afu_context,
  input fifoin_empty,
  input fifoin_almost_empty,
  input [512-1:0] rd_fifoin_data,
  input fifoout_full,
  input fifo_out_almostfull,
  input fifoout_empty,
  output rd_fifoin_en,
  output wr_fifoout_en,
  output [512-1:0] wr_fifoout_data,
  output done
);

  wire [32-1:0] num_data_in;
  wire [32-1:0] num_data_out;
  wire end_data_in;
  wire [32-1:0] task_done;
  wire [32-1:0] has_data;
  wire [32-1:0] has_lst3_data;
  wire [246-1:0] data_out0;
  wire [246-1:0] data_out1;
  wire [246-1:0] data_out2;
  wire [246-1:0] data_out3;
  wire [246-1:0] data_out4;
  wire [246-1:0] data_out5;
  wire [246-1:0] data_out6;
  wire [246-1:0] data_out7;
  wire [246-1:0] data_out8;
  wire [246-1:0] data_out9;
  wire [246-1:0] data_out10;
  wire [246-1:0] data_out11;
  wire [246-1:0] data_out12;
  wire [246-1:0] data_out13;
  wire [246-1:0] data_out14;
  wire [246-1:0] data_out15;
  wire [246-1:0] data_out16;
  wire [246-1:0] data_out17;
  wire [246-1:0] data_out18;
  wire [246-1:0] data_out19;
  wire [246-1:0] data_out20;
  wire [246-1:0] data_out21;
  wire [246-1:0] data_out22;
  wire [246-1:0] data_out23;
  wire [246-1:0] data_out24;
  wire [246-1:0] data_out25;
  wire [246-1:0] data_out26;
  wire [246-1:0] data_out27;
  wire [246-1:0] data_out28;
  wire [246-1:0] data_out29;
  wire [246-1:0] data_out30;
  wire [246-1:0] data_out31;
  wire [512-1:0] data_in;
  wire [32-1:0] read_data_en;
  wire data_in_valid;
  assign num_data_in = afu_context[287:256];
  assign num_data_out = afu_context[319:288];

  control_data_in
  control_data_in
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .num_data_in(num_data_in),
    .has_data_in(~fifoin_empty),
    .has_lst3_data_in(fifoin_almost_empty),
    .data_in(rd_fifoin_data),
    .rd_request_en(rd_fifoin_en),
    .data_valid(data_in_valid),
    .data_out(data_in),
    .done(end_data_in)
  );


  regulator_network
  #(
    .ID(1)
  )
  rn0
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
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
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
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
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
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
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
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
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
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
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
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
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
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
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[7]),
    .has_data_out(has_data[7]),
    .has_lst3_data_out(has_lst3_data[7]),
    .data_out(data_out7),
    .task_done(task_done[7])
  );


  regulator_network
  #(
    .ID(9)
  )
  rn8
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[8]),
    .has_data_out(has_data[8]),
    .has_lst3_data_out(has_lst3_data[8]),
    .data_out(data_out8),
    .task_done(task_done[8])
  );


  regulator_network
  #(
    .ID(10)
  )
  rn9
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[9]),
    .has_data_out(has_data[9]),
    .has_lst3_data_out(has_lst3_data[9]),
    .data_out(data_out9),
    .task_done(task_done[9])
  );


  regulator_network
  #(
    .ID(11)
  )
  rn10
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[10]),
    .has_data_out(has_data[10]),
    .has_lst3_data_out(has_lst3_data[10]),
    .data_out(data_out10),
    .task_done(task_done[10])
  );


  regulator_network
  #(
    .ID(12)
  )
  rn11
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[11]),
    .has_data_out(has_data[11]),
    .has_lst3_data_out(has_lst3_data[11]),
    .data_out(data_out11),
    .task_done(task_done[11])
  );


  regulator_network
  #(
    .ID(13)
  )
  rn12
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[12]),
    .has_data_out(has_data[12]),
    .has_lst3_data_out(has_lst3_data[12]),
    .data_out(data_out12),
    .task_done(task_done[12])
  );


  regulator_network
  #(
    .ID(14)
  )
  rn13
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[13]),
    .has_data_out(has_data[13]),
    .has_lst3_data_out(has_lst3_data[13]),
    .data_out(data_out13),
    .task_done(task_done[13])
  );


  regulator_network
  #(
    .ID(15)
  )
  rn14
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[14]),
    .has_data_out(has_data[14]),
    .has_lst3_data_out(has_lst3_data[14]),
    .data_out(data_out14),
    .task_done(task_done[14])
  );


  regulator_network
  #(
    .ID(16)
  )
  rn15
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[15]),
    .has_data_out(has_data[15]),
    .has_lst3_data_out(has_lst3_data[15]),
    .data_out(data_out15),
    .task_done(task_done[15])
  );


  regulator_network
  #(
    .ID(17)
  )
  rn16
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[16]),
    .has_data_out(has_data[16]),
    .has_lst3_data_out(has_lst3_data[16]),
    .data_out(data_out16),
    .task_done(task_done[16])
  );


  regulator_network
  #(
    .ID(18)
  )
  rn17
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[17]),
    .has_data_out(has_data[17]),
    .has_lst3_data_out(has_lst3_data[17]),
    .data_out(data_out17),
    .task_done(task_done[17])
  );


  regulator_network
  #(
    .ID(19)
  )
  rn18
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[18]),
    .has_data_out(has_data[18]),
    .has_lst3_data_out(has_lst3_data[18]),
    .data_out(data_out18),
    .task_done(task_done[18])
  );


  regulator_network
  #(
    .ID(20)
  )
  rn19
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[19]),
    .has_data_out(has_data[19]),
    .has_lst3_data_out(has_lst3_data[19]),
    .data_out(data_out19),
    .task_done(task_done[19])
  );


  regulator_network
  #(
    .ID(21)
  )
  rn20
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[20]),
    .has_data_out(has_data[20]),
    .has_lst3_data_out(has_lst3_data[20]),
    .data_out(data_out20),
    .task_done(task_done[20])
  );


  regulator_network
  #(
    .ID(22)
  )
  rn21
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[21]),
    .has_data_out(has_data[21]),
    .has_lst3_data_out(has_lst3_data[21]),
    .data_out(data_out21),
    .task_done(task_done[21])
  );


  regulator_network
  #(
    .ID(23)
  )
  rn22
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[22]),
    .has_data_out(has_data[22]),
    .has_lst3_data_out(has_lst3_data[22]),
    .data_out(data_out22),
    .task_done(task_done[22])
  );


  regulator_network
  #(
    .ID(24)
  )
  rn23
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[23]),
    .has_data_out(has_data[23]),
    .has_lst3_data_out(has_lst3_data[23]),
    .data_out(data_out23),
    .task_done(task_done[23])
  );


  regulator_network
  #(
    .ID(25)
  )
  rn24
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[24]),
    .has_data_out(has_data[24]),
    .has_lst3_data_out(has_lst3_data[24]),
    .data_out(data_out24),
    .task_done(task_done[24])
  );


  regulator_network
  #(
    .ID(26)
  )
  rn25
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[25]),
    .has_data_out(has_data[25]),
    .has_lst3_data_out(has_lst3_data[25]),
    .data_out(data_out25),
    .task_done(task_done[25])
  );


  regulator_network
  #(
    .ID(27)
  )
  rn26
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[26]),
    .has_data_out(has_data[26]),
    .has_lst3_data_out(has_lst3_data[26]),
    .data_out(data_out26),
    .task_done(task_done[26])
  );


  regulator_network
  #(
    .ID(28)
  )
  rn27
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[27]),
    .has_data_out(has_data[27]),
    .has_lst3_data_out(has_lst3_data[27]),
    .data_out(data_out27),
    .task_done(task_done[27])
  );


  regulator_network
  #(
    .ID(29)
  )
  rn28
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[28]),
    .has_data_out(has_data[28]),
    .has_lst3_data_out(has_lst3_data[28]),
    .data_out(data_out28),
    .task_done(task_done[28])
  );


  regulator_network
  #(
    .ID(30)
  )
  rn29
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[29]),
    .has_data_out(has_data[29]),
    .has_lst3_data_out(has_lst3_data[29]),
    .data_out(data_out29),
    .task_done(task_done[29])
  );


  regulator_network
  #(
    .ID(31)
  )
  rn30
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[30]),
    .has_data_out(has_data[30]),
    .has_lst3_data_out(has_lst3_data[30]),
    .data_out(data_out30),
    .task_done(task_done[30])
  );


  regulator_network
  #(
    .ID(32)
  )
  rn31
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .data_in_valid(data_in_valid),
    .data_in(data_in[381:0]),
    .end_data_in(end_data_in),
    .read_data_en(read_data_en[31]),
    .has_data_out(has_data[31]),
    .has_lst3_data_out(has_lst3_data[31]),
    .data_out(data_out31),
    .task_done(task_done[31])
  );


  control_data_out
  control_data_out
  (
    .clk(clk_gnr),
    .rst(rst),
    .start(start),
    .num_data_out(num_data_out),
    .fifo_out_full(fifoout_full),
    .fifo_out_almostfull(fifo_out_almostfull),
    .fifo_out_empty(fifoout_empty),
    .has_data(has_data),
    .has_lst3_data(has_lst3_data),
    .din0({ 10'd0, data_out0 }),
    .din1({ 10'd0, data_out1 }),
    .din2({ 10'd0, data_out2 }),
    .din3({ 10'd0, data_out3 }),
    .din4({ 10'd0, data_out4 }),
    .din5({ 10'd0, data_out5 }),
    .din6({ 10'd0, data_out6 }),
    .din7({ 10'd0, data_out7 }),
    .din8({ 10'd0, data_out8 }),
    .din9({ 10'd0, data_out9 }),
    .din10({ 10'd0, data_out10 }),
    .din11({ 10'd0, data_out11 }),
    .din12({ 10'd0, data_out12 }),
    .din13({ 10'd0, data_out13 }),
    .din14({ 10'd0, data_out14 }),
    .din15({ 10'd0, data_out15 }),
    .din16({ 10'd0, data_out16 }),
    .din17({ 10'd0, data_out17 }),
    .din18({ 10'd0, data_out18 }),
    .din19({ 10'd0, data_out19 }),
    .din20({ 10'd0, data_out20 }),
    .din21({ 10'd0, data_out21 }),
    .din22({ 10'd0, data_out22 }),
    .din23({ 10'd0, data_out23 }),
    .din24({ 10'd0, data_out24 }),
    .din25({ 10'd0, data_out25 }),
    .din26({ 10'd0, data_out26 }),
    .din27({ 10'd0, data_out27 }),
    .din28({ 10'd0, data_out28 }),
    .din29({ 10'd0, data_out29 }),
    .din30({ 10'd0, data_out30 }),
    .din31({ 10'd0, data_out31 }),
    .read_data_en(read_data_en),
    .task_done(task_done),
    .wr_fifo_out_en(wr_fifoout_en),
    .wr_fifo_out_data(wr_fifoout_data),
    .done(done)
  );


  initial begin
    $dumpfile("dump.vcd");
    $dumpvars(0, "gnr_harp");
  end


endmodule
