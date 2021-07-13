
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


endmodule
