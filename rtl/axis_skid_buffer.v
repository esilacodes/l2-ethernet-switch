// ============================================================================
// File: axis_skid_buffer.v
// Module: axis_skid_buffer
// Project: 4-Port Non-Blocking L2 Ethernet Switch
// Description: Fully registered AXI4-Stream Skid Buffer (Register Slice).
//              Decouples s_axis_tready and m_axis_tvalid with zero combinational
//              paths, eliminating combinational loops and timing critical paths.
//              Provides 100% sustained throughput (zero bubble cycles).
// Standard: Verilog-2001, Synthesizable, Zero latches.
// ============================================================================

`timescale 1ns / 1ps

module axis_skid_buffer #(
    parameter DATA_WIDTH = 8,
    parameter USER_WIDTH = 1
)(
    input  wire                  clk,
    input  wire                  rst_n,

    // Slave AXI-Stream Interface (Ingress)
    input  wire [DATA_WIDTH-1:0] s_axis_tdata,
    input  wire                  s_axis_tvalid,
    output reg                   s_axis_tready,
    input  wire                  s_axis_tlast,
    input  wire [USER_WIDTH-1:0] s_axis_tuser,

    // Master AXI-Stream Interface (Egress)
    output reg  [DATA_WIDTH-1:0] m_axis_tdata,
    output reg                   m_axis_tvalid,
    input  wire                  m_axis_tready,
    output reg                   m_axis_tlast,
    output reg  [USER_WIDTH-1:0] m_axis_tuser
);

    // =========================================================================
    // Internal Registers for Skid Storage
    // =========================================================================
    reg [DATA_WIDTH-1:0] skid_tdata;
    reg                  skid_tlast;
    reg [USER_WIDTH-1:0] skid_tuser;
    reg                  skid_valid;

    // Handshake detection wires
    wire s_handshake = s_axis_tvalid && s_axis_tready;
    wire m_handshake = m_axis_tvalid && m_axis_tready;

    // =========================================================================
    // Skid Buffer Sequential Logic
    // =========================================================================
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            // Reset Master outputs
            m_axis_tvalid <= 1'b0;
            m_axis_tdata  <= {DATA_WIDTH{1'b0}};
            m_axis_tlast  <= 1'b0;
            m_axis_tuser  <= {USER_WIDTH{1'b0}};

            // Reset Skid registers
            skid_valid    <= 1'b0;
            skid_tdata    <= {DATA_WIDTH{1'b0}};
            skid_tlast    <= 1'b0;
            skid_tuser    <= {USER_WIDTH{1'b0}};

            // Ready to accept data immediately out of reset
            s_axis_tready <= 1'b1;
        end else begin
            if (skid_valid) begin
                // A stalled byte is stored in the skid buffer.
                // Ingress is currently blocked (s_axis_tready == 0).
                if (m_handshake) begin
                    // Egress consumed current m_axis byte; drain skid buffer to m_axis
                    m_axis_tdata  <= skid_tdata;
                    m_axis_tlast  <= skid_tlast;
                    m_axis_tuser  <= skid_tuser;
                    m_axis_tvalid <= 1'b1;

                    // Skid buffer is now emptied; re-enable ingress ready
                    skid_valid    <= 1'b0;
                    s_axis_tready <= 1'b1;
                end
                // If downstream remains stalled (!m_handshake), keep holding state
            end else begin
                // Skid buffer is empty. Ingress is ready (s_axis_tready == 1).
                if (m_handshake) begin
                    if (s_handshake) begin
                        // Flow-through: Master consumes current byte, Slave supplies next byte
                        m_axis_tdata  <= s_axis_tdata;
                        m_axis_tlast  <= s_axis_tlast;
                        m_axis_tuser  <= s_axis_tuser;
                        m_axis_tvalid <= 1'b1;
                        s_axis_tready <= 1'b1;
                    end else begin
                        // Master consumed current byte, but no new byte arrived
                        m_axis_tvalid <= 1'b0;
                        s_axis_tready <= 1'b1;
                    end
                end else begin
                    // Downstream did not consume
                    if (!m_axis_tvalid) begin
                        // Output stage was idle; if new byte arrives, load it into m_axis
                        if (s_handshake) begin
                            m_axis_tdata  <= s_axis_tdata;
                            m_axis_tlast  <= s_axis_tlast;
                            m_axis_tuser  <= s_axis_tuser;
                            m_axis_tvalid <= 1'b1;
                        end
                        s_axis_tready <= 1'b1;
                    end else begin
                        // Output stage is holding valid data and downstream is stalled.
                        // If slave produces a new byte, capture it in the skid buffer.
                        if (s_handshake) begin
                            skid_tdata    <= s_axis_tdata;
                            skid_tlast    <= s_axis_tlast;
                            skid_tuser    <= s_axis_tuser;
                            skid_valid    <= 1'b1;

                            // Buffer is now completely full (m_axis + skid both occupied)
                            // Pull s_axis_tready LOW to assert backpressure
                            s_axis_tready <= 1'b0;
                        end
                    end
                end
            end
        end
    end

endmodule
