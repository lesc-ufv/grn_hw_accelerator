
module control_fifo_data_in #
(
  parameter ID = 0
)
(
  input clk,
  input rst,
  input start,
  input data_in_valid,
  input [382-1:0] data_in,
  input fifo_in_full,
  input fifo_in_amostfull,
  output reg fifo_in_we,
  output reg [376-1:0] fifo_in_data
);


  always @(posedge clk) begin
    if(rst) begin
      fifo_in_we <= 1'b0;
      fifo_in_data <= 376'd0;
    end else begin
      if(start) begin
        fifo_in_we <= 1'b0;
        if(data_in_valid && (data_in[5:0] == ID) && ~fifo_in_full) begin
          fifo_in_we <= 1'b1;
          fifo_in_data <= data_in[381:6];
        end 
      end 
    end
  end


endmodule
