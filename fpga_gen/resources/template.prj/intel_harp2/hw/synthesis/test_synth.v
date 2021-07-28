module test_synth(
  input clk,
  input rst,
  output dout
);

 top_level_synth uut(
    .clk(clk),
	.rst(rst),
	.out(dout)
 );


endmodule
