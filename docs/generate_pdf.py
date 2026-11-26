# ==============================================================================
# Script: generate_pdf.py
# Description: Generates a comprehensive, professional hardware architecture and
#              design specification PDF for the 4-Port Non-Blocking L2 Ethernet Switch.
# ==============================================================================

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ------------------------------------------------------------------------------
# Register TrueType Fonts for Turkish and Monospace Support
# ------------------------------------------------------------------------------
FONT_DIR = "C:/Windows/Fonts"
pdfmetrics.registerFont(TTFont('Arial', os.path.join(FONT_DIR, 'arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(FONT_DIR, 'arialbd.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(FONT_DIR, 'ariali.ttf')))
pdfmetrics.registerFont(TTFont('Consolas', os.path.join(FONT_DIR, 'consola.ttf')))

# ------------------------------------------------------------------------------
# Custom Canvas for Two-Pass Page Numbering (Sayfa X / Y) & Running Headers
# ------------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page

        self.saveState()
        self.setFont('Arial', 8)
        self.setFillColor(colors.HexColor('#718096'))

        # Running Header
        self.drawString(54, 760, '4-Port Non-Blocking L2 Ethernet Switch (VOQ & iSLIP) | Donanım Tasarım Spesifikasyonu')
        self.setStrokeColor(colors.HexColor('#CBD5E0'))
        self.setLineWidth(0.6)
        self.line(54, 752, 541, 752)

        # Running Footer
        self.line(54, 45, 541, 45)
        self.drawString(54, 32, 'TEKNİK MİMARİ VE DOĞRULAMA KILAVUZU — SOLO GELİŞTİRİCİ REFERANS DOKÜMANI')
        page_str = f"Sayfa {self._pageNumber} / {page_count}"
        self.drawRightString(541, 32, page_str)

        self.restoreState()

# ------------------------------------------------------------------------------
# Color Palette
# ------------------------------------------------------------------------------
PRIMARY    = colors.HexColor('#1A365D')  # Deep Navy
SECONDARY  = colors.HexColor('#2B6CB0')  # Blue Slate
ACCENT     = colors.HexColor('#2C7A7B')  # Dark Teal
DARK_TEXT  = colors.HexColor('#2D3748')  # Charcoal Body Text
LIGHT_BG   = colors.HexColor('#F7FAFC')  # Off-white table background
BORDER_COL = colors.HexColor('#E2E8F0')  # Subtle Borders
ALERT_BG   = colors.HexColor('#FFF5F5')  # Light red callout
ALERT_BRD  = colors.HexColor('#FEB2B2')  # Red border
BOX_BG     = colors.HexColor('#EDF2F7')  # Grey box

# ------------------------------------------------------------------------------
# Styles Setup
# ------------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_title = ParagraphStyle(
    'CoverTitle',
    fontName='Arial-Bold',
    fontSize=24,
    leading=30,
    textColor=PRIMARY,
    alignment=0, # Left
    spaceAfter=10
)

style_subtitle = ParagraphStyle(
    'CoverSubtitle',
    fontName='Arial',
    fontSize=13,
    leading=18,
    textColor=SECONDARY,
    alignment=0,
    spaceAfter=25
)

style_h1 = ParagraphStyle(
    'Heading1_Custom',
    fontName='Arial-Bold',
    fontSize=15,
    leading=20,
    textColor=PRIMARY,
    spaceBefore=16,
    spaceAfter=8,
    keepWithNext=True
)

style_h2 = ParagraphStyle(
    'Heading2_Custom',
    fontName='Arial-Bold',
    fontSize=11.5,
    leading=16,
    textColor=SECONDARY,
    spaceBefore=12,
    spaceAfter=6,
    keepWithNext=True
)

style_h3 = ParagraphStyle(
    'Heading3_Custom',
    fontName='Arial-Bold',
    fontSize=10,
    leading=14,
    textColor=ACCENT,
    spaceBefore=8,
    spaceAfter=4,
    keepWithNext=True
)

style_body = ParagraphStyle(
    'Body_Custom',
    fontName='Arial',
    fontSize=9,
    leading=13.5,
    textColor=DARK_TEXT,
    spaceAfter=6
)

style_body_bold = ParagraphStyle(
    'BodyBold_Custom',
    fontName='Arial-Bold',
    fontSize=9,
    leading=13.5,
    textColor=DARK_TEXT,
    spaceAfter=6
)

style_bullet = ParagraphStyle(
    'Bullet_Custom',
    fontName='Arial',
    fontSize=9,
    leading=13.5,
    textColor=DARK_TEXT,
    leftIndent=15,
    firstLineIndent=-10,
    spaceAfter=3
)

style_code = ParagraphStyle(
    'Code_Custom',
    fontName='Consolas',
    fontSize=7.8,
    leading=11,
    textColor=colors.HexColor('#1A202C')
)

style_callout = ParagraphStyle(
    'Callout_Custom',
    fontName='Arial-Italic',
    fontSize=8.5,
    leading=12.5,
    textColor=colors.HexColor('#742A2A')
)

style_th = ParagraphStyle(
    'TH_Custom',
    fontName='Arial-Bold',
    fontSize=8.5,
    leading=11,
    textColor=colors.white,
    alignment=1 # Center
)

style_td = ParagraphStyle(
    'TD_Custom',
    fontName='Arial',
    fontSize=8,
    leading=11,
    textColor=DARK_TEXT
)

style_td_code = ParagraphStyle(
    'TD_Code_Custom',
    fontName='Consolas',
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor('#2C5282')
)

# ------------------------------------------------------------------------------
# Build Document Story
# ------------------------------------------------------------------------------
def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=18*mm,
        rightMargin=18*mm,
        topMargin=22*mm,
        bottomMargin=20*mm
    )

    story = []

    # ==========================================================================
    # COVER / HEADER BLOCK
    # ==========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("4-PORT NON-BLOCKING L2 ETHERNET SWITCH", style_title))
    story.append(Paragraph("VOQ (Virtual Output Queuing) & 2D iSLIP Hakem Destekli Donanım Mimarisi, RTL Tasarım ve Doğrulama Spesifikasyonu", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=0, spaceAfter=15))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Proje Adı:</b>", style_td), Paragraph("4-Port Gigabit L2 Non-Blocking Switch", style_td),
         Paragraph("<b>Saat Frekansı:</b>", style_td), Paragraph("125.0 MHz (8.0 ns Periyot)", style_td)],
        [Paragraph("<b>Geliştirici Rolü:</b>", style_td), Paragraph("Solo Hardware & Verification Engineer", style_td),
         Paragraph("<b>Hat Hızı / Port:</b>", style_td), Paragraph("1 Gbps (8-bit @ 125 MHz)", style_td)],
        [Paragraph("<b>RTL Standardı:</b>", style_td), Paragraph("Verilog-2001 (Yosys & Vivado Sentezlenebilir)", style_td),
         Paragraph("<b>Anahtarlama Kapasitesi:</b>", style_td), Paragraph("4 Gbps Tam Çift Yönlü (Full-Duplex)", style_td)],
        [Paragraph("<b>Mimari Türü:</b>", style_td), Paragraph("Store-and-Forward + VOQ (16 FIFO)", style_td),
         Paragraph("<b>Doğrulama Çatısı:</b>", style_td), Paragraph("Icarus Verilog, Cocotb & Scapy (.pcap)", style_td)]
    ]
    t_meta = Table(meta_data, colWidths=[90, 160, 100, 137])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BOX_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))

    # ==========================================================================
    # BÖLÜM 1: YÖNETİCİ ÖZETİ VE TEMEL MİMARİ FELSEFE
    # ==========================================================================
    story.append(Paragraph("1. GENEL BAKIŞ VE MİMARİ FELSEFE", style_h1))
    story.append(Paragraph(
        "Bu teknik spesifikasyon; 4 giriş ve 4 çıkış portuna sahip, yüksek başarımlı, endüstriyel standartta bir "
        "<b>Katman-2 (L2) Ethernet Switch</b> donanımının mimari, mantıksal ve doğrulama ayrıntılarını tanımlar. "
        "Tasarım, gigabit Ethernet hızında (125 MHz tekil saat frekansı, 8-bit veri yolu ile port başına 1 Gbps) "
        "çalışmak üzere optimize edilmiştir.", style_body
    ))
    story.append(Paragraph(
        "<b>Geleneksel Giriş Kuyruklamalı (Input-Queued) Switch Problemi:</b> Tek bir FIFO kullanılan giriş portlarında, "
        "kuyruğun en başındaki paket tıkalı bir çıkış portuna gitmek istediğinde, arkasındaki paketler boş çıkışlara gitmek istese "
        "dahi beklemek zorunda kalır. <b>Head-of-Line (HoL) Blocking</b> olarak adlandırılan bu olgu, switch başarımını teorik olarak "
        "en fazla <b>%58.58</b> (1 - 1/e) seviyesinde sınırlar.", style_body
    ))
    story.append(Paragraph(
        "<b>Çözüm — VOQ & iSLIP Mimarisi:</b> Bu projede her giriş portu, 4 çıkış portunun her biri için ayrı bir kuyruk "
        "barındırır (Giriş başına 4 VOQ, toplam <b>16 bağımsız BRAM Packet FIFO</b>). İki boyutlu 4x4 <b>iSLIP hakem algoritması</b> "
        "ile giriş ve çıkışlar arasındaki eşleşme çevrimsel olarak çözülerek HoL bloklaması tamamen ortadan kaldırılır ve "
        "<b>%100 hat hızı (line-rate throughput)</b> elde edilir.", style_body
    ))

    # Architecture Overview Callout Box
    callout_data = [[
        Paragraph("<b>Dondurulmuş Temel Tasarım Kuralları:</b><br/>"
                  "• <b>Store-and-Forward:</b> Paket FCS kontrolünden başarıyla geçip boyutu doğrulanana kadar çıkışa sürülmez.<br/>"
                  "• <b>Paket Seviyesinde Kilitleme:</b> iSLIP eşleşmesi, çıkışta baytların karışmaması için <code>tlast</code> onaylanana kadar sabit tutulur.<br/>"
                  "• <b>Kombinasyonel Döngü Güvencesi:</b> <code>tready</code>/<code>tvalid</code> el sıkışma hatlarında Skid Buffer kullanılır.<br/>"
                  "• <b>Sentez Garantisi:</b> Tamamen Verilog-2001 standardında, sıfır latch, sıfır çoklu sürücü prensibiyle tasarlanır.", style_callout)
    ]]
    t_callout = Table(callout_data, colWidths=[487])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ALERT_BG),
        ('BOX', (0,0), (-1,-1), 1, ALERT_BRD),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 10))

    # ==========================================================================
    # BÖLÜM 2: SİSTEM BLOK ŞEMASI VE VERİ YOLU
    # ==========================================================================
    story.append(Paragraph("2. SİSTEM VERİ YOLU VE BLOK HİYERARŞİSİ", style_h1))
    story.append(Paragraph(
        "Sistem 5 ana fonksiyonel blok grubundan oluşmaktadır. Giriş portlarından gelen AXI4-Stream paketleri, "
        "ayrıştırıcıdan geçerek doğru VOQ kuyruğuna yönlendirilir; iSLIP zamanlayıcı hakemliği çözer ve crossbar üzerinden "
        "çıkış portlarına iletilir:", style_body
    ))

    # Datapath Table
    block_table = [
        [Paragraph("Blok Adı", style_th), Paragraph("Modül Dosyası", style_th), Paragraph("Fonksiyonu ve Donanım Rolü", style_th)],
        [Paragraph("<b>Skid Buffer</b>", style_td), Paragraph("<code>axis_skid_buffer.v</code>", style_td_code),
         Paragraph("2-kademeli register slice. Ready/valid arasındaki kombinasyonel döngüyü sıfır gecikme kabarcığıyla keser.", style_td)],
        [Paragraph("<b>CRC32 Checker</b>", style_td), Paragraph("<code>crc32_checker.v</code>", style_td_code),
         Paragraph("8-bit paralel IEEE 802.3 FCS denetimi. 0xDEBB20E3 sihirli kalıntısını doğrular, hatalı paketleri bayraklar.", style_td)],
        [Paragraph("<b>Packet Parser</b>", style_td), Paragraph("<code>packet_parser.v</code>", style_td_code),
         Paragraph("Ethernet FSM (Dst/Src MAC, EtherType). Runt (<64B) ve oversize (>1518B) paketleri filtreler.", style_td)],
        [Paragraph("<b>Packet FIFO</b>", style_td), Paragraph("<code>packet_fifo.v</code>", style_td_code),
         Paragraph("BRAM tabanlı, store-and-forward destekli FIFO. Commit sinyali gelene kadar paketi saklar; bozuksa geri sarar (rollback).", style_td)],
        [Paragraph("<b>VOQ Block</b>", style_td), Paragraph("<code>voq_block.v</code>", style_td_code),
         Paragraph("Her giriş portu için 4 adet sanal çıkış kuyruğu (VOQ0..3) ve giriş yönlendirici mantığı.", style_td)],
        [Paragraph("<b>MAC Table</b>", style_td), Paragraph("<code>mac_table.v</code>", style_td_code),
         Paragraph("64/128 girdili dinamik CAM/RAM tablosu. Kaynak öğrenme, hedef arama, flooding maskesi ve aging sayacı.", style_td)],
        [Paragraph("<b>iSLIP Scheduler</b>", style_td), Paragraph("<code>islip_scheduler_4x4.v</code>", style_td_code),
         Paragraph("2D döngüsel öncelikli hakem. Request-Grant-Accept döngüsünü çözer ve tlast'e kadar kilitler.", style_td)],
        [Paragraph("<b>Crossbar Fabric</b>", style_td), Paragraph("<code>crossbar_4x4.v</code>", style_td_code),
         Paragraph("16 FIFO çıkışını 4 çıkış portuna bağlayan 4:1 multiplexer ağı ve çıkış skid buffer'ları.", style_td)],
        [Paragraph("<b>Stats Collector</b>", style_td), Paragraph("<code>stats_collector.v</code>", style_td_code),
         Paragraph("Port başına RX/TX paket, bayt, CRC hata, runt/oversize drop ve taşma sayaçlarını tutar.", style_td)]
    ]
    t_blocks = Table(block_table, colWidths=[90, 115, 282])
    t_blocks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_blocks)
    story.append(Spacer(1, 10))

    # ==========================================================================
    # BÖLÜM 3: ARAYÜZ VE SİNYAL SPESİFİKASYONU
    # ==========================================================================
    story.append(Paragraph("3. ARAYÜZ VE SİNYAL SPESİFİKASYONLARI", style_h1))
    story.append(Paragraph(
        "Switch, port başına endüstri standardı <b>AXI4-Stream</b> protokolünü kullanır. "
        "Saat frekansı 125.0 MHz'dir. Her bir saat çevriminde 1 bayt veri akar, bu da port başına net 1 Gbps bant genişliği sağlar.", style_body
    ))

    # AXI-Stream Signal Table
    axis_signals = [
        [Paragraph("Sinyal Adı", style_th), Paragraph("Yön", style_th), Paragraph("Genişlik", style_th), Paragraph("Açıklama ve Protokol Rolü", style_th)],
        [Paragraph("<code>clk</code>", style_td_code), Paragraph("Giriş", style_td), Paragraph("1 bit", style_td), Paragraph("125 MHz tekil global sistem saati.", style_td)],
        [Paragraph("<code>rst_n</code>", style_td_code), Paragraph("Giriş", style_td), Paragraph("1 bit", style_td), Paragraph("Aktif-alçak (active-low) global sıfırlama.", style_td)],
        [Paragraph("<code>axis_tdata[7:0]</code>", style_td_code), Paragraph("Giriş/Çıkış", style_td), Paragraph("8 bit", style_td), Paragraph("Bayt düzeyinde Ethernet çerçeve verisi (Little-endian).", style_td)],
        [Paragraph("<code>axis_tvalid</code>", style_td_code), Paragraph("Giriş/Çıkış", style_td), Paragraph("1 bit", style_td), Paragraph("Verinin geçerli olduğunu belirten kaynak bayrağı.", style_td)],
        [Paragraph("<code>axis_tready</code>", style_td_code), Paragraph("Giriş/Çıkış", style_td), Paragraph("1 bit", style_td), Paragraph("Hedefin yeni bayt kabul etmeye hazır olduğunu bildiren bayrak.", style_td)],
        [Paragraph("<code>axis_tlast</code>", style_td_code), Paragraph("Giriş/Çıkış", style_td), Paragraph("1 bit", style_td), Paragraph("Ethernet çerçevesinin son baytını (FCS son baytı) işaretler.", style_td)],
        [Paragraph("<code>axis_tuser</code>", style_td_code), Paragraph("Giriş/Çıkış", style_td), Paragraph("1 bit", style_td), Paragraph("Hata bayrağı (1: Bozuk/CRC hatalı paket, 0: Geçerli paket).", style_td)]
    ]
    t_axis = Table(axis_signals, colWidths=[100, 45, 55, 287])
    t_axis.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_axis)
    story.append(Spacer(1, 12))

    # ==========================================================================
    # BÖLÜM 4: FAZ BAZLI MODÜL DETAYLARI
    # ==========================================================================
    story.append(Paragraph("4. GELİŞTİRME FAZLARI VE DETAYLI MODÜL MİMARİSİ", style_h1))

    # 4.1 FAZ 1: Giriş Hattı
    story.append(Paragraph("4.1 Faz 1: Giriş Hattı & Ayrıştırıcı (Ingress Pipeline)", style_h2))
    story.append(Paragraph(
        "Giriş hattı, fiziksel hattan gelen bayt akışını karşılar, bütünlüğünü denetler ve paket başlıklarını çözer:", style_body
    ))
    story.append(Paragraph(
        "• <b>Skid Buffer (Register Slice):</b> Downstream tıkanıklığında giriş hazır sinyalini anında keserken, "
        "hatta bulunan son baytı yedek kayda alır. Bu sayede hiçbir döngü oluşmaz ve sıfır bubble çevrimiyle çalışır.<br/>"
        "• <b>CRC32 / FCS Denetleyicisi:</b> Standart IEEE 802.3 Ethernet polinomu <code>0x04C11DB7</code> (ters yansıtılmış: <code>0xEDB88320</code>) "
        "üzerinden 8-bit paralel LFSR matrisi işletilir. Paket FCS baytları dahil hesaplandığında, kaydedilen son değer sihirli kalıntı olan "
        "<b><code>0xDEBB20E3</code></b> (ters çevrilmiş haliyle <code>0x2144DF1C</code>) ile eşleşmelidir. Eşleşmezse <code>crc_error</code> sinyali üretilir.<br/>"
        "• <b>Packet Parser (Ethernet FSM):</b> Durum makinesi sırasıyla <i>IDLE -> DST_MAC (6B) -> SRC_MAC (6B) -> ETHERTYPE (2B) -> PAYLOAD -> FCS (4B)</i> "
        "aşamalarından geçer. Toplam bayt sayısı 64'ten küçükse (<b>Runt Frame</b>) veya 1518'den büyükse (<b>Oversize Frame</b>) "
        "paket bozuk işaretlenir ve kuyruktan düşürülür (drop).", style_body
    ))

    # 4.2 FAZ 2: VOQ ve Commit
    story.append(Paragraph("4.2 Faz 2: Sanal Çıkış Kuyruk Matrisi (VOQ) ve Paket Tabanlı Commit", style_h2))
    story.append(Paragraph(
        "• <b>16 Adet Bağımsız Paket FIFO:</b> Her giriş portu (Port 0..3) için 4 adet FIFO tahsis edilir: <code>VOQ[in][out]</code>. "
        "Port 0'dan gelip Port 2'ye gitmek isteyen bir paket <code>VOQ_0_2</code>'ye yazılırken, Port 0'dan Port 1'e gitmek isteyen paket "
        "<code>VOQ_0_1</code>'e yazılır. Böylece Port 2 meşgulken Port 1'e gidecek paket asla engellenmez (Zero HoL Blocking).<br/>"
        "• <b>Store-and-Forward Commit / Rollback:</b> Gelen baytlar anlık olarak FIFO BRAM'ine yazılır ancak okuma göstergeci (read pointer) "
        "ve <code>packet_ready</code> bayrağı paket sonuna (<code>tlast</code>) kadar kilitli tutulur. Paket sonunda CRC32 geçerli ve boyut kurallara "
        "uygunsa <b>COMMIT</b> darbesi üretilir ve paket hakeme sunulur. Eğer paket hatalıysa <b>ROLLBACK</b> yapılır; yazma göstergeci "
        "paketin başladığı adrese geri çekilerek paket bellekten tamamen silinir.<br/>"
        "• <b>Almost Full Eşiği:</b> FIFO doluluğu belirlenen eşiği (örn. MTU=1518B payı kalacak şekilde) aştığında giriş portunun <code>tready</code> "
        "sinyali düşürülerek Ethernet akış denetimi (flow control / backpressure) tetiklenir.", style_body
    ))

    # 4.3 FAZ 3: MAC Tablosu
    story.append(Paragraph("4.3 Faz 3: Dinamik MAC Öğrenme ve Yaşlandırma Tablosu (MAC Table)", style_h2))
    story.append(Paragraph(
        "• <b>Öğrenme (Source Learning):</b> Ayrıştırıcıdan gelen her geçerli paketin Kaynak MAC adresi ve geldiği Giriş Portu "
        "tabloya kaydedilir. Eğer adres zaten varsa port bilgisi ve yaşlandırma sayacı güncellenir.<br/>"
        "• <b>Arama ve Yönlendirme (Destination Lookup):</b> Hedef MAC tabloda aranır:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;1. <i>Unicast Hit:</i> MAC tabloda bulunursa paket yalnızca ilgili çıkış kuyruğuna yazılır.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;2. <i>Unicast Miss / Broadcast (FF:FF:FF:FF:FF:FF):</i> Paket, geldiği port hariç (<b>Non-Reflection</b>) "
        "diğer 3 çıkış portunun kuyruğuna birden kopyalanır (Flooding: <code>dest_mask = (~(1 << ingress_port)) & 4'b1111</code>).<br/>"
        "• <b>Dinamik Yaşlandırma (Aging Engine):</b> Her kayıt için bir geri sayım sayacı çalışır (varsayılan 300 sn). Süresi dolan kayıt "
        "tablodan otomatik olarak silinir (invalidated).<br/>"
        "• <b>Read-While-Write Güvenliği:</b> Aynı saat çevriminde aynı adrese hem öğrenme hem de arama geldiğinde verinin bayat okunmaması "
        "için forwarding (bypass) mantığı işletilir.", style_body
    ))

    # 4.4 FAZ 4: iSLIP Zamanlayıcı & Crossbar
    story.append(Paragraph("4.4 Faz 4: 2 Boyutlu 4x4 iSLIP Hakem Algoritması ve Crossbar Dokusu", style_h2))
    story.append(Paragraph(
        "iSLIP, Stanford Üniversitesi'nden Prof. Nick McKeown tarafından geliştirilen ve donanımda O(1) karmaşıklıkla çalışan "
        "yüksek başarımlı bir 2D döngüsel (round-robin) eşleştirme algoritmasıdır. Her saat çevriminde 3 adımda çalışır:", style_body
    ))

    # iSLIP 3 Steps Table
    islip_steps = [
        [Paragraph("Adım", style_th), Paragraph("Aşama Adı", style_th), Paragraph("Algoritmik Davranış ve Donanım İşleyişi", style_th)],
        [Paragraph("<b>1</b>", style_td), Paragraph("<b>Request (İstek)</b>", style_td),
         Paragraph("Her giriş portu, dolu olan ve paketi hazır bulunan VOQ'ları için ilgili çıkış portlarına eşzamanlı istek (request) gönderir.", style_td)],
        [Paragraph("<b>2</b>", style_td), Paragraph("<b>Grant (İzin)</b>", style_td),
         Paragraph("Her çıkış portu, kendisine gelen istekler arasından kendi Round-Robin hakem göstergecine göre bir girişe izin (grant) verir.", style_td)],
        [Paragraph("<b>3</b>", style_td), Paragraph("<b>Accept (Kabul)</b>", style_td),
         Paragraph("Birden fazla çıkıştan izin alan bir giriş portu, kendi Round-Robin kabul göstergecine göre bir çıkışı kabul (accept) eder.", style_td)],
        [Paragraph("<b>*</b>", style_td), Paragraph("<b>Desenkronizasyon</b>", style_td),
         Paragraph("Çıkış grant göstergeçleri <i>yalnızca istek başarıyla kabul edildiğinde (accept)</i> ilerletilir. Bu özellik hakemlerin birbiriyle çakışmasını engeller ve %100 throughput sağlar.", style_td)]
    ]
    t_islip = Table(islip_steps, colWidths=[35, 110, 342])
    t_islip.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), ACCENT),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_islip)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Paket Seviyesinde Kilitleme (Packet-Level Locking):</b> Klasik iSLIP hücre (cell) bazlı ATM/IP anahtarlarda her çevrim "
        "yeniden eşleşir. Ancak Ethernet paketleri bölünemez. Bir giriş ile çıkış eşleştiğinde, o paketin son baytı (<code>tlast</code>) "
        "çıkış Skid Buffer'ı tarafından onaylanana kadar eşleşme <b>KİLİTLİ</b> tutulur. Böylece çıkışta farklı girişlerden gelen baytların "
        "birbirine karışması kesin olarak önlenir.", style_body
    ))
    story.append(Paragraph(
        "<b>4x4 Crossbar Dokusu:</b> 16 FIFO çıkışı, iSLIP eşleşme vektörüne göre 4 adet 4:1 multiplexer üzerinden fiziksel çıkış "
        "portlarına aktarılır. Her çıkış portunun önünde birer Skid Buffer yer alarak çıkış hattı zamanlaması güvenceye alınır.", style_body
    ))

    # 4.5 FAZ 5: İstatistikler ve Top-Level
    story.append(Paragraph("4.5 Faz 5: İstatistik Sayaçları ve Top-Level Entegrasyonu", style_h2))
    story.append(Paragraph(
        "• <b>Stats Collector:</b> Donanım hata ayıklama ve RMON uyumluluğu için her portta 32-bitlik sayaçlar yer alır: "
        "<code>rx_frame_count</code>, <code>tx_frame_count</code>, <code>rx_byte_count</code>, <code>tx_byte_count</code>, "
        "<code>crc_error_drop_count</code>, <code>runt_drop_count</code>, <code>oversize_drop_count</code>, <code>fifo_overflow_drop_count</code>.<br/>"
        "• <b>Top-Level Entegrasyon (switch_top.v):</b> Tüm bloklar hiyerarşik olarak birbirine bağlanır. Tüm dahili arayüzler "
        "AXI4-Stream uyumludur ve saat bölgesi tekil 125 MHz'dir.", style_body
    ))

    # ==========================================================================
    # BÖLÜM 5: DOĞRULAMA ÇATISI VE PERFORMANS KARŞILAŞTIRMASI
    # ==========================================================================
    story.append(Spacer(1, 5))
    story.append(Paragraph("5. DOĞRULAMA METODOLOJİSİ VE ANALİZ PLANI", style_h1))
    story.append(Paragraph(
        "Projenin doğrulanması iki katmanlı bir piramit yaklaşımıyla yürütülecektir:", style_body
    ))
    story.append(Paragraph(
        "1. <b>Modüler RTL Testbench'leri (Icarus Verilog):</b> Her modülün kendine ait, assertion ve scoreboard içeren "
        "kendi kendini doğrulayan (self-checking) testbench'i bulunur. Hatalı bayt, yetersiz periyot veya kayıp el sıkışma durumunda "
        "simülasyon <code>$display(\"[FAIL]\")</code> ile hata verir.<br/>"
        "2. <b>Sistem Seviyesi Cocotb & Scapy Doğrulaması:</b> Python tabanlı test çatısında Scapy kütüphanesi kullanılarak gerçekçi "
        "Ethernet trafiği oluşturulur (Rastgele MAC, VLAN etiketleri, IPv4/TCP yükleri). Switch çıkışları yakalanarak doğrudan "
        "Wireshark uyumlu <b><code>.pcap</code></b> dosyalarına kaydedilir.<br/>"
        "3. <b>Throughput Karşılaştırma Grafiği (Raporun Kalbi):</b> "
        "Giriş trafik yükü (Offered Load: %10'dan %100'e) kademeli artırılarak iki switch konfigürasyonu simüle edilir:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <i>Konfigürasyon A (Klasik Tek FIFO):</i> HoL bloklaması nedeniyle %58.6 yükten sonra throughput düzleşir.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <i>Konfigürasyon B (VOQ + iSLIP):</i> %100 yüke kadar lineer artış göstererek tam hat hızını (%100) korur.<br/>"
        "Elde edilen metrikler Python <code>matplotlib</code> ile grafikleştirilerek kesin başarım ispatı sunulur.", style_body
    ))

    # ==========================================================================
    # BÖLÜM 6: SOLO GELİŞTİRİCİ FAZ VE ONAY MATRİSİ
    # ==========================================================================
    story.append(Spacer(1, 5))
    story.append(Paragraph("6. SOLO GELİŞTİRİCİ İCRA PLANI VE KONTROL NOKTALARI", style_h1))

    roadmap_data = [
        [Paragraph("Faz", style_th), Paragraph("Modül Dosyası", style_th), Paragraph("Hedef Doğrulama ve Kabul Kriteri", style_th), Paragraph("Durum", style_th)],
        [Paragraph("<b>Faz 1</b>", style_td), Paragraph("<code>axis_skid_buffer.v</code>", style_td_code),
         Paragraph("Sıfır bubble cycle, backpressure altında bayt kayıpsız transfer.", style_td), Paragraph("<b>TAMAMLANDI</b>", style_td)],
        [Paragraph("<b>Faz 1</b>", style_td), Paragraph("<code>crc32_checker.v</code>", style_td_code),
         Paragraph("0xDEBB20E3 kalıntısı, runt/oversize paket bayraklama.", style_td), Paragraph("<i>Sırada</i>", style_td)],
        [Paragraph("<b>Faz 1</b>", style_td), Paragraph("<code>packet_parser.v</code>", style_td_code),
         Paragraph("Ethernet başlık FSM'i, MAC yakalama, Kontrol Noktası 1 entegrasyonu.", style_td), Paragraph("Beklemede", style_td)],
        [Paragraph("<b>Faz 2</b>", style_td), Paragraph("<code>packet_fifo.v</code><br/><code>voq_block.v</code>", style_td_code),
         Paragraph("Store-and-forward commit & rollback, 4x VOQ yönlendirme testi.", style_td), Paragraph("Beklemede", style_td)],
        [Paragraph("<b>Faz 3</b>", style_td), Paragraph("<code>mac_table.v</code>", style_td_code),
         Paragraph("Kaynak öğrenme, unicast hit, non-reflection flooding ve aging sayacı.", style_td), Paragraph("Beklemede", style_td)],
        [Paragraph("<b>Faz 4</b>", style_td), Paragraph("<code>islip_scheduler_4x4.v</code><br/><code>crossbar_4x4.v</code>", style_td_code),
         Paragraph("Request-Grant-Accept döngüsü, tlast paket kilidi, 4x4 non-blocking aktarım.", style_td), Paragraph("Beklemede", style_td)],
        [Paragraph("<b>Faz 5</b>", style_td), Paragraph("<code>switch_top.v</code><br/><code>stats_collector.v</code>", style_td_code),
         Paragraph("Top-level 4 portlu donanım entegrasyonu ve istatistik sayaçları.", style_td), Paragraph("Beklemede", style_td)],
        [Paragraph("<b>Faz 6</b>", style_td), Paragraph("Cocotb & Scapy Testbench<br/>Throughput Karşılaştırması", style_td_code),
         Paragraph(".pcap dökümü ve Tek FIFO (%58.6) vs VOQ (%100) grafik çizimi.", style_td), Paragraph("Beklemede", style_td)]
    ]
    t_road = Table(roadmap_data, colWidths=[45, 120, 242, 80])
    t_road.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_road)
    story.append(Spacer(1, 15))

    # Closing Signature Block
    sign_block = [
        [Paragraph("<b>Doküman Durumu:</b> ONAYLANDI & YÜRÜRLÜKTE", style_td),
         Paragraph("<b>Mühendislik Kuralı:</b> Modül Modül Onaylı İlerleme", style_td)]
    ]
    t_sign = Table(sign_block, colWidths=[240, 247])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BOX_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sign)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated: {filename}")

if __name__ == '__main__':
    pdf_path = r"C:\Users\esila\.gemini\antigravity\scratch\l2_ethernet_switch\L2_Ethernet_Switch_Technical_Architecture_Spec.pdf"
    build_pdf(pdf_path)
