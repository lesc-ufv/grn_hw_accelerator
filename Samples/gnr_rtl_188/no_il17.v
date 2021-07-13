
module no_il17
(
  input clk,
  input start,
  input rst,
  input reset_nos,
  input start_s0,
  input start_s1,
  input init_state,
  input [1-1:0] nfat_s0,
  input [1-1:0] nfat_s1,
  input [1-1:0] stat3_s0,
  input [1-1:0] stat3_s1,
  input [1-1:0] nfkb_s0,
  input [1-1:0] nfkb_s1,
  input [1-1:0] proliferation_s0,
  input [1-1:0] proliferation_s1,
  input [1-1:0] rorgt_s0,
  input [1-1:0] rorgt_s1,
  input [1-1:0] stat1_s0,
  input [1-1:0] stat1_s1,
  input [1-1:0] foxp3_s0,
  input [1-1:0] foxp3_s1,
  input [1-1:0] stat6_s0,
  input [1-1:0] stat6_s1,
  input [1-1:0] stat5_s0,
  input [1-1:0] stat5_s1,
  output reg [1-1:0] s0,
  output reg [1-1:0] s1,
  output [1-1:0] il17_s0,
  output [1-1:0] il17_s1
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
            s0 <=  ( ( ( ( nfat_s0 & ( ( ( stat3_s0 & nfkb_s0 & proliferation_s0 & rorgt_s0 ) ) ) ) & ~ ( stat1_s0 & ( ( ( foxp3_s0 ) ) ) ) ) & ~ ( stat6_s0 & ( ( ( foxp3_s0 ) ) ) ) ) & ~ ( stat5_s0 & ( ( ( foxp3_s0 ) ) ) ) ) ;
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
          s1 <=  ( ( ( ( nfat_s1 & ( ( ( stat3_s1 & nfkb_s1 & proliferation_s1 & rorgt_s1 ) ) ) ) & ~ ( stat1_s1 & ( ( ( foxp3_s1 ) ) ) ) ) & ~ ( stat6_s1 & ( ( ( foxp3_s1 ) ) ) ) ) & ~ ( stat5_s1 & ( ( ( foxp3_s1 ) ) ) ) ) ;
        end 
      end
    end
  end

  assign il17_s0 = s0;
  assign il17_s1 = s1;

endmodule
