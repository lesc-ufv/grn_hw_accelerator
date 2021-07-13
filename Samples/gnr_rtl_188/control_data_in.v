
module control_data_in
(
  input clk,
  input rst,
  input start,
  input [32-1:0] num_data_in,
  input has_data_in,
  input has_lst3_data_in,
  input [512-1:0] data_in,
  output reg rd_request_en,
  output reg data_valid,
  output reg [512-1:0] data_out,
  output reg done
);

  localparam [3-1:0] FSM_WAIT = 0;
  localparam [3-1:0] FSM_RD_DATA = 1;
  localparam [3-1:0] FSM_DONE = 2;
  reg [3-1:0] fms_cs;
  reg [32-1:0] cont_data;

  always @(posedge clk) begin
    if(rst) begin
      rd_request_en <= 1'b0;
      data_out <= 512'd0;
      cont_data <= 32'd0;
      done <= 1'b0;
      data_valid <= 1'b0;
      fms_cs <= FSM_WAIT;
    end else begin
      if(start) begin
        data_valid <= 1'b0;
        rd_request_en <= 1'b0;
        case(fms_cs)
          FSM_WAIT: begin
            if(cont_data < num_data_in) begin
              if(has_data_in) begin
                rd_request_en <= 1'b1;
                data_out <= 512'd0;
                fms_cs <= FSM_RD_DATA;
              end else begin
                data_out <= 512'd0;
                fms_cs <= FSM_WAIT;
              end
            end else begin
              data_out <= 512'd0;
              fms_cs <= FSM_DONE;
            end
          end
          FSM_RD_DATA: begin
            data_out <= data_in;
            cont_data <= cont_data + 32'd1;
            data_valid <= 1'b1;
            fms_cs <= FSM_WAIT;
          end
          FSM_DONE: begin
            data_out <= 512'd0;
            fms_cs <= FSM_DONE;
            done <= 1'b1;
          end
        endcase
      end 
    end
  end


endmodule
