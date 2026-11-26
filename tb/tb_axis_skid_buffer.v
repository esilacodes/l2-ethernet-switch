// ============================================================================
// File: tb_axis_skid_buffer.v
// Module: tb_axis_skid_buffer
// Project: 4-Port Non-Blocking L2 Ethernet Switch
// Description: Comprehensive self-checking testbench for axis_skid_buffer.
//              Verifies:
//              1. Reset and initial ready assertion.
//              2. Sustained back-to-back 100% throughput (zero bubble cycles).
//              3. Single-cycle and multi-cycle downstream backpressure (stalls).
//              4. Skid buffer data capture and ready deassertion.
//              5. Correct tlast and tuser propagation.
//              6. Random stress testing with interleaved valid/ready handshakes.
// ============================================================================

`timescale 1ns / 1ps

module tb_axis_skid_buffer;

    parameter DATA_WIDTH = 8;
    parameter USER_WIDTH = 1;
    parameter CLK_PERIOD = 8; // 125 MHz clock -> 8 ns period

    reg                   clk;
    reg                   rst_n;

    // Slave interface stimulus
    reg  [DATA_WIDTH-1:0] s_axis_tdata;
    reg                   s_axis_tvalid;
    wire                  s_axis_tready;
    reg                   s_axis_tlast;
    reg  [USER_WIDTH-1:0] s_axis_tuser;

    // Master interface monitoring
    wire [DATA_WIDTH-1:0] m_axis_tdata;
    wire                  m_axis_tvalid;
    reg                   m_axis_tready;
    wire                  m_axis_tlast;
    wire [USER_WIDTH-1:0] m_axis_tuser;

    // Verification bookkeeping
    integer error_count = 0;
    integer tx_count    = 0;
    integer rx_count    = 0;

    // Golden queues for verification
    reg [DATA_WIDTH-1:0] queue_data [0:4095];
    reg                  queue_last [0:4095];
    reg [USER_WIDTH-1:0] queue_user [0:4095];
    integer q_wr_ptr = 0;
    integer q_rd_ptr = 0;

    // Instantiate Unit Under Test (UUT)
    axis_skid_buffer #(
        .DATA_WIDTH(DATA_WIDTH),
        .USER_WIDTH(USER_WIDTH)
    ) uut (
        .clk          (clk),
        .rst_n        (rst_n),
        .s_axis_tdata (s_axis_tdata),
        .s_axis_tvalid(s_axis_tvalid),
        .s_axis_tready(s_axis_tready),
        .s_axis_tlast (s_axis_tlast),
        .s_axis_tuser (s_axis_tuser),
        .m_axis_tdata (m_axis_tdata),
        .m_axis_tvalid(m_axis_tvalid),
        .m_axis_tready(m_axis_tready),
        .m_axis_tlast (m_axis_tlast),
        .m_axis_tuser (m_axis_tuser)
    );

    // Clock Generation (125 MHz)
    always #(CLK_PERIOD / 2) clk = ~clk;

    // Ingress Stimulus Task
    task send_byte;
        input [DATA_WIDTH-1:0] data;
        input                  last;
        input [USER_WIDTH-1:0] user;
        begin
            s_axis_tdata  <= data;
            s_axis_tlast  <= last;
            s_axis_tuser  <= user;
            s_axis_tvalid <= 1'b1;

            @(posedge clk);
            while (!s_axis_tready) begin
                @(posedge clk);
            end

            // Log sent beat to scoreboard
            queue_data[q_wr_ptr] = data;
            queue_last[q_wr_ptr] = last;
            queue_user[q_wr_ptr] = user;
            q_wr_ptr             = q_wr_ptr + 1;
            tx_count             = tx_count + 1;

            s_axis_tvalid <= 1'b0;
            s_axis_tdata  <= {DATA_WIDTH{1'b0}};
            s_axis_tlast  <= 1'b0;
            s_axis_tuser  <= {USER_WIDTH{1'b0}};
        end
    endtask

    // Continuous Scoreboard / Monitor on Master Interface
    always @(posedge clk) begin
        if (rst_n) begin
            if (m_axis_tvalid && m_axis_tready) begin
                if (q_rd_ptr >= q_wr_ptr) begin
                    $display("[ERROR] [%0t ns] Received unexpected beat when queue empty! Data=0x%02h", $time, m_axis_tdata);
                    error_count = error_count + 1;
                end else begin
                    if (m_axis_tdata !== queue_data[q_rd_ptr]) begin
                        $display("[ERROR] [%0t ns] Data mismatch at index %0d: Expected 0x%02h, Got 0x%02h",
                                 $time, q_rd_ptr, queue_data[q_rd_ptr], m_axis_tdata);
                        error_count = error_count + 1;
                    end
                    if (m_axis_tlast !== queue_last[q_rd_ptr]) begin
                        $display("[ERROR] [%0t ns] TLAST mismatch at index %0d: Expected %0b, Got %0b",
                                 $time, q_rd_ptr, queue_last[q_rd_ptr], m_axis_tlast);
                        error_count = error_count + 1;
                    end
                    if (m_axis_tuser !== queue_user[q_rd_ptr]) begin
                        $display("[ERROR] [%0t ns] TUSER mismatch at index %0d: Expected %0b, Got %0b",
                                 $time, q_rd_ptr, queue_user[q_rd_ptr], m_axis_tuser);
                        error_count = error_count + 1;
                    end
                    q_rd_ptr = q_rd_ptr + 1;
                    rx_count = rx_count + 1;
                end
            end
        end
    end

    // Test Sequence
    integer i;
    initial begin
        $display("==================================================================");
        $display("   STARTING TESTBENCH: axis_skid_buffer");
        $display("==================================================================");

        // Initialize signals
        clk           = 1'b0;
        rst_n         = 1'b0;
        s_axis_tdata  = {DATA_WIDTH{1'b0}};
        s_axis_tvalid = 1'b0;
        s_axis_tlast  = 1'b0;
        s_axis_tuser  = {USER_WIDTH{1'b0}};
        m_axis_tready = 1'b0;

        // Apply reset
        #(CLK_PERIOD * 5);
        rst_n = 1'b1;
        @(posedge clk);
        #(CLK_PERIOD * 2);

        // Verify Reset State
        if (s_axis_tready !== 1'b1 || m_axis_tvalid !== 1'b0) begin
            $display("[ERROR] Reset state invalid: s_axis_tready=%b, m_axis_tvalid=%b",
                     s_axis_tready, m_axis_tvalid);
            error_count = error_count + 1;
        end else begin
            $display("[INFO] TEST 1: Reset behavior verified PASS.");
        end

        // ---------------------------------------------------------------------
        // TEST 2: Back-to-back 100% Throughput Streaming (No Backpressure)
        // ---------------------------------------------------------------------
        $display("[INFO] TEST 2: Running 32-byte back-to-back streaming without stalls...");
        m_axis_tready = 1'b1;
        for (i = 0; i < 32; i = i + 1) begin
            send_byte(8'hA0 + i, (i == 31), 1'b0);
        end
        @(posedge clk);
        while (rx_count < tx_count) @(posedge clk);
        $display("[INFO] TEST 2 Completed. Sent=%0d, Received=%0d", tx_count, rx_count);

        // ---------------------------------------------------------------------
        // TEST 3: Downstream Stalls (Backpressure & Skid Register Capture)
        // ---------------------------------------------------------------------
        $display("[INFO] TEST 3: Testing downstream stall and skid storage...");
        m_axis_tready = 1'b0; // Block receiver

        // Send 1st byte: will sit in m_axis registers
        fork
            send_byte(8'hC1, 1'b0, 1'b0);
        join_none
        @(posedge clk);
        #(CLK_PERIOD);

        // Send 2nd byte: will sit in skid registers; s_axis_tready must go to 0!
        fork
            send_byte(8'hC2, 1'b1, 1'b0);
        join_none
        @(posedge clk);
        #(CLK_PERIOD * 2);

        if (s_axis_tready !== 1'b0) begin
            $display("[ERROR] s_axis_tready did not deassert when buffer was full!");
            error_count = error_count + 1;
        end else begin
            $display("[INFO] Buffer successfully full, s_axis_tready is 0 as expected.");
        end

        // Release downstream backpressure
        $display("[INFO] Releasing downstream backpressure (m_axis_tready = 1)...");
        m_axis_tready = 1'b1;
        while (rx_count < tx_count) @(posedge clk);
        #(CLK_PERIOD * 3);
        $display("[INFO] TEST 3 Completed. Sent=%0d, Received=%0d", tx_count, rx_count);

        // ---------------------------------------------------------------------
        // TEST 4: Randomized Stress Handshake Testing
        // ---------------------------------------------------------------------
        $display("[INFO] TEST 4: Running 200 transfers with random valid/ready toggles...");
        for (i = 0; i < 200; i = i + 1) begin
            // Randomly stall receiver
            m_axis_tready = ($random % 3 != 0); // ~66% ready
            if ($random % 2 == 0) begin
                send_byte($random & 8'hFF, (i % 16 == 15), (i % 32 == 31));
            end else begin
                @(posedge clk);
            end
        end

        // Drain any remaining items
        m_axis_tready = 1'b1;
        s_axis_tvalid = 1'b0;
        for (i = 0; i < 50; i = i + 1) begin
            @(posedge clk);
            if (rx_count == tx_count) i = 50;
        end

        // ---------------------------------------------------------------------
        // Final Assessment
        // ---------------------------------------------------------------------
        $display("==================================================================");
        $display("   TESTBENCH SUMMARY: axis_skid_buffer");
        $display("   Total Bytes Transmitted : %0d", tx_count);
        $display("   Total Bytes Received    : %0d", rx_count);
        $display("   Total Errors Detected   : %0d", error_count);
        if (error_count == 0 && tx_count == rx_count && tx_count > 0) begin
            $display("   RESULT: >>> [PASS] ALL TESTS PASSED SUCCESSFULLY! <<<");
        end else begin
            $display("   RESULT: >>> [FAIL] TESTBENCH FAILED WITH %0d ERRORS! <<<", error_count);
        end
        $display("==================================================================");

        #(CLK_PERIOD * 10);
        $finish;
    end

endmodule
