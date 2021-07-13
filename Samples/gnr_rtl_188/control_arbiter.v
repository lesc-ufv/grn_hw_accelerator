
module control_arbiter
(
  input clk,
  input rst,
  input start,
  input [32-1:0] has_data_out,
  input [32-1:0] has_lst3_data,
  input fifo_out_full,
  output reg [32-1:0] read_data_en,
  output reg wr_fifo_out,
  output reg [5-1:0] mux_control
);

  localparam FSM_IDLE = 0;
  localparam FSM_RD_REQ = 1;
  localparam FSM_WR_REQ = 2;
  reg [3-1:0] fsm_state;
  reg [32-1:0] request;
  reg [5-1:0] grant_index_reg;
  wire [32-1:0] grant;
  wire [5-1:0] grant_index;
  wire grant_valid;

  arbiter
  #(
    .PORTS(32),
    .TYPE("ROUND_ROBIN"),
    .BLOCK("NONE"),
    .LSB_PRIORITY("LOW")
  )
  arbiter_inst
  (
    .clk(clk),
    .rst(rst),
    .request(request),
    .acknowledge(32'd0),
    .grant(grant),
    .grant_valid(grant_valid),
    .grant_encoded(grant_index)
  );


  always @(posedge clk) begin
    if(rst) begin
      fsm_state <= FSM_IDLE;
      request <= 32'd0;
      read_data_en <= 1'b0;
      grant_index_reg <= 5'd0;
      wr_fifo_out <= 1'b0;
      mux_control <= 5'd0;
    end else begin
      if(start) begin
        request <= 32'd0;
        read_data_en <= 1'b0;
        wr_fifo_out <= 1'b0;
        mux_control <= 5'd0;
        case(fsm_state)
          FSM_IDLE: begin
            if((has_data_out != 32'd0) && !fifo_out_full) begin
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


endmodule
