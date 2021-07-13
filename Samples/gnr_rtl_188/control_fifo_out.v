
module control_fifo_out
(
  input clk,
  input rst,
  input start,
  input [32-1:0] num_data_out,
  input [32-1:0] task_done,
  input wr_en,
  input [256-1:0] wr_data,
  input fifoout_full,
  input fifoout_almostfull,
  input fifoout_empty,
  output reg wr_fifoout_en,
  output [512-1:0] wr_fifoout_data,
  output reg done
);

  reg [2-1:0] index_data;
  reg [256-1:0] data [0:2-1];
  reg [3-1:0] count_empty;
  reg [32-1:0] cont_data;
  reg [3-1:0] fms_cs;
  reg [256-1:0] buffer;
  genvar i;

  generate for(i=0; i<2; i=i+1) begin : gen_1
    assign wr_fifoout_data[i*256+256-1:i*256] = data[i];
  end
  endgenerate

  localparam [3-1:0] FSM_FIFO_WR0 = 1;
  localparam [3-1:0] FSM_FIFO_FULL = 2;
  localparam [3-1:0] FSM_END_DATA = 3;
  localparam [3-1:0] FSM_DONE = 4;

  always @(posedge clk) begin
    if(rst) begin
      fms_cs <= FSM_FIFO_WR0;
      index_data <= 2'd0;
      wr_fifoout_en <= 1'b0;
      done <= 1'b0;
      count_empty <= 3'd0;
      buffer <= 256'd0;
      cont_data <= 32'd0;
    end else begin
      if(start) begin
        wr_fifoout_en <= 1'b0;
        case(fms_cs)
          FSM_FIFO_WR0: begin
            if((~task_done == 32'd0) || (cont_data >= num_data_out)) begin
              if(index_data > 0) begin
                if(~fifoout_full) begin
                  wr_fifoout_en <= 1'b1;
                  index_data <= 2'd0;
                  fms_cs <= FSM_END_DATA;
                end 
              end else begin
                fms_cs <= FSM_END_DATA;
              end
            end else if(wr_en) begin
              if(index_data < 1) begin
                data[index_data] <= wr_data;
                index_data <= index_data + 2'd1;
              end else if(~fifoout_full) begin
                data[index_data] <= wr_data;
                wr_fifoout_en <= 1'b1;
                index_data <= 2'd0;
              end else begin
                data[index_data] <= wr_data;
                fms_cs <= FSM_FIFO_FULL;
              end
              cont_data <= cont_data + 32'd1;
            end 
          end
          FSM_FIFO_FULL: begin
            if(wr_en) begin
              cont_data <= cont_data + 32'd1;
              buffer <= wr_data;
            end 
            if(~fifoout_full) begin
              if(index_data >= 1) begin
                wr_fifoout_en <= 1'b1;
                index_data <= 2'd0;
              end else begin
                data[index_data] <= buffer;
                index_data <= index_data + 2'd1;
                fms_cs <= FSM_FIFO_WR0;
              end
            end 
          end
          FSM_END_DATA: begin
            if(count_empty > 2) begin
              fms_cs <= FSM_DONE;
              done <= 1'b1;
            end else if(fifoout_empty) begin
              count_empty <= count_empty + 3'd1;
            end 
          end
          FSM_DONE: begin
            fms_cs <= FSM_DONE;
            done <= 1'b1;
          end
        endcase
      end 
    end
  end


endmodule
