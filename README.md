# 4-Port Non-Blocking L2 Ethernet Switch (VOQ & iSLIP Destekli)

**Verilog-2001** standardında geliştirilmiş; **Sanal Çıkış Kuyruklaması (VOQ - Virtual Output Queuing)**, iki boyutlu **iSLIP hakem algoritması**, dinamik **MAC öğrenme & yaşlandırma (aging)** tablosu ve **AXI4-Stream** arayüzlerine sahip endüstriyel standartta 4-Port Gigabit Ethernet Katman-2 (L2) Store-and-Forward Switch donanım tasarımı.

---

## 🚀 Öne Çıkan Mimari Özellikler

* **Arayüz & Hız:** Port başına 8-bit AXI4-Stream (`tdata[7:0]`, `tvalid`, `tready`, `tlast`, `tuser`). 125 MHz tekil saat bölgesi (Port başına 1 Gbps hat hızı, toplam **4 Gbps non-blocking** anahtarlama kapasitesi).
* **Head-of-Line (HoL) Bloklamasını Önleme:** Giriş başına 4 VOQ (toplam **16 bağımsız BRAM Packet FIFO**) ile klasik tek FIFO'lu switch'lerdeki %58.58 ($1 - 1/e$) throughput tavanı tamamen kırılarak **%100 hat hızı (line-rate)** elde edilir.
* **2D iSLIP Zamanlayıcı:** Nick McKeown tarafından geliştirilen 4x4 Request-Grant-Accept döngüsel öncelikli (round-robin) hakem algoritması ve desenkronizasyon (desynchronization) güvencesi.
* **Paket Düzeyinde Kilitleme (Packet-Level Locking):** Çıkış hatlarında paket baytlarının birbirine karışmaması için hakem eşleşmesi çerçevenin son baytı (`tlast`) onaylanana kadar kilitli tutulur.
* **Store-and-Forward Doğrulaması:** Paketler, IEEE 802.3 CRC32 (FCS) kontrolü ve boyut denetimi (64B min, 1518B max) başarıyla tamamlanmadan çıkışa sürülmez. Bozuk paketler yazma göstergeci geri sarılarak (**rollback**) bellekten otomatik silinir.
* **Dinamik MAC Tablosu:** Kaynak MAC öğrenme, hedef MAC arama, dinamik aging (eskime sayacı), geldiği port hariç taşırma (**non-reflection flooding**: `(~(1 << ingress_port)) & 4'b1111`) ve read-while-write çakışma yönetimi.
* **Zamanlama ve Sentez Güvencesi:** `tvalid` ve `tready` hatlarında 2-kademeli Skid Buffer (Register Slice) kullanımı ile kombinasyonel döngüler tamamen kesilir. Sıfır bubble cycle, sıfır latch ve Yosys/Vivado ile tam sentezlenebilirlik.

---

## 📁 Proje Dizin Yapısı

```
.
├── rtl/                        # Verilog-2001 Sentezlenebilir RTL Donanım Modülleri
│   ├── axis_skid_buffer.v      # Tam kayıtlı AXI4-Stream Skid Buffer (0 bubble cycle)
│   └── crc_func.vh             # 8-bit paralel IEEE 802.3 CRC32 matris fonksiyonu
├── tb/                         # Kendi Kendini Doğrulayan (Self-Checking) Testbench'ler
│   └── tb_axis_skid_buffer.v   # Skid buffer doğrulama ve rastgele fuzzing testbench'i
├── docs/                       # Mimari El Kitapları ve Teknik Dokümantasyon
│   ├── L2_Ethernet_Switch_Technical_Architecture_Spec.pdf # Kapsamlı mimari spesifikasyon PDF'i
│   └── generate_pdf.py         # ReportLab mimari doküman üretici scripti
└── README.md                   # Proje ana tanıtım ve yol haritası dokümanı
```

---

## 🗺️ Geliştirme Fazları ve Güncel Durum

| Faz | Modül Dosyası | Açıklama ve Kabul Kriteri | Durum |
|---|---|---|---|
| **Faz 1** | `axis_skid_buffer.v` | `ready`/`valid` döngülerini kıran 2 kademeli register slice | ✅ **Tamamlandı** |
| **Faz 1** | `crc32_checker.v` | 8-bit paralel Ethernet FCS & `0xDEBB20E3` kalıntı denetimi | 🔄 **Sırada** |
| **Faz 1** | `packet_parser.v` | Ethernet FSM, Runt (<64B) ve Oversize (>1518B) filtreleme | ⏳ Beklemede |
| **Faz 1** | `tb_ingress_pipeline.v`| **Kontrol Noktası 1:** Tek port uçtan uca giriş hattı doğrulaması | ⏳ Beklemede |
| **Faz 2** | `packet_fifo.v` & `voq_block.v` | BRAM tabanlı commit/rollback FIFO ve 16'lı VOQ matrisi | ⏳ Beklemede |
| **Faz 3** | `mac_table.v` | Dinamik kaynak öğrenme, non-reflection flooding ve aging | ⏳ Beklemede |
| **Faz 4** | `islip_scheduler_4x4.v` & `crossbar_4x4.v` | 2D Request-Grant-Accept hakemi, paket kilidi ve 4x4 crossbar | ⏳ Beklemede |
| **Faz 5** | `stats_collector.v` & `switch_top.v` | Donanım sayaçları ve 4 portlu Top-Level entegrasyonu | ⏳ Beklemede |
| **Faz 6** | Cocotb & Scapy Doğrulaması | Python ile trafik enjeksiyonu, `.pcap` dökümü ve Karşılaştırma Grafiği | ⏳ Beklemede |

---

## 📖 Kapsamlı Mimari Dokümanı
Projenin tüm matematiksel formülleri, sinyal dalga şekilleri, sonlu durum makineleri (FSM) ve donanım register haritalarını içeren detaylı teknik spesifikasyon PDF'ine [`docs/L2_Ethernet_Switch_Technical_Architecture_Spec.pdf`](docs/L2_Ethernet_Switch_Technical_Architecture_Spec.pdf) dosyasından ulaşabilirsiniz.
