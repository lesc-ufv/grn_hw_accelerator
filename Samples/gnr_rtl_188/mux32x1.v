
module mux32x1 #
(
  parameter WIDTH = 256
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
  input [WIDTH-1:0] in8,
  input [WIDTH-1:0] in9,
  input [WIDTH-1:0] in10,
  input [WIDTH-1:0] in11,
  input [WIDTH-1:0] in12,
  input [WIDTH-1:0] in13,
  input [WIDTH-1:0] in14,
  input [WIDTH-1:0] in15,
  input [WIDTH-1:0] in16,
  input [WIDTH-1:0] in17,
  input [WIDTH-1:0] in18,
  input [WIDTH-1:0] in19,
  input [WIDTH-1:0] in20,
  input [WIDTH-1:0] in21,
  input [WIDTH-1:0] in22,
  input [WIDTH-1:0] in23,
  input [WIDTH-1:0] in24,
  input [WIDTH-1:0] in25,
  input [WIDTH-1:0] in26,
  input [WIDTH-1:0] in27,
  input [WIDTH-1:0] in28,
  input [WIDTH-1:0] in29,
  input [WIDTH-1:0] in30,
  input [WIDTH-1:0] in31,
  input [5-1:0] s,
  output [WIDTH-1:0] out
);

  wire [WIDTH-1:0] ins [0:32-1];
  assign ins[0] = in0;
  assign ins[1] = in1;
  assign ins[2] = in2;
  assign ins[3] = in3;
  assign ins[4] = in4;
  assign ins[5] = in5;
  assign ins[6] = in6;
  assign ins[7] = in7;
  assign ins[8] = in8;
  assign ins[9] = in9;
  assign ins[10] = in10;
  assign ins[11] = in11;
  assign ins[12] = in12;
  assign ins[13] = in13;
  assign ins[14] = in14;
  assign ins[15] = in15;
  assign ins[16] = in16;
  assign ins[17] = in17;
  assign ins[18] = in18;
  assign ins[19] = in19;
  assign ins[20] = in20;
  assign ins[21] = in21;
  assign ins[22] = in22;
  assign ins[23] = in23;
  assign ins[24] = in24;
  assign ins[25] = in25;
  assign ins[26] = in26;
  assign ins[27] = in27;
  assign ins[28] = in28;
  assign ins[29] = in29;
  assign ins[30] = in30;
  assign ins[31] = in31;
  assign out = ins[s];

endmodule
