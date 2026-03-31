import streamlit as st
import pandas as pd
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İzmir Günlük Paylaşım", page_icon="📋", layout="wide")

# GÖRSEL TEMİZLİK VE ZORUNLU LIGHT MODE EKLENTİSİ
st.markdown("""
    <style>
    /* Zorunlu Light Mode (Siyah ekranı engeller) */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    /* Streamlit Reklamlarını (Watermark) ve Butonlarını Agresif Gizleme */
    [data-testid="stBottom"], [data-testid="stToolbar"] {display: none !important;}
    .viewerBadge_container__1QSob, .stAppDeployButton {display: none !important;}
    button[title="View fullscreen"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# --- TARİH VE GÜN AYARI ---
gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
bugun = datetime.date.today()
tarih_str = bugun.strftime("%d.%m.%Y") + " " + gunler[bugun.weekday()]

# --- ANA BAŞLIK ---
st.markdown(f"""
<div style="background-color: #004d99; padding: 15px; margin-bottom: 0px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
<h2 style='color: white; text-align: center; margin: 0px; font-size: 24px;'>📋 İZMİR ŞUBE OFİSİ ÜRETİM LİSTESİ</h2>
</div>
<div style="background-color: #e6f0ff; padding: 8px; margin-bottom: 20px; border-bottom: 2px solid #004d99; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
<h4 style='color: #004d99; text-align: center; margin: 0px; font-size: 16px;'>{tarih_str}</h4>
</div>
""", unsafe_allow_html=True)

# --- AKILLI VERİ ÇEKME MOTORU (Satır kaymalarına karşı korumalı) ---
@st.cache_data(ttl=120) # Güncellemeleri daha hızlı görmek için süreyi 2 dakikaya indirdim
def veri_getir_ve_isle():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=90150185&single=true&output=csv"
    try:
        # Tüm tabloyu başlık olmadan ham haliyle oku
        df_raw = pd.read_csv(url, header=None, on_bad_lines='skip') 
        
        # SIRA kelimesinin hangi satırda olduğunu otomatik bul (Akıllı Radar)
        header_idx = -1
        for i in range(min(15, len(df_raw))):
            row_str = " ".join(df_raw.iloc[i].astype(str)).upper()
            if "SIRA" in row_str:
                header_idx = i
                break
                
        # Eğer SIRA satırı bulunduysa, o satırı başlık yap
        if header_idx != -1:
            df_raw.columns = df_raw.iloc[header_idx]
            df_raw = df_raw.iloc[header_idx+1:].reset_index(drop=True)
        else:
            return [], "Tabloda 'SIRA' veya 'Sıra' başlığı bulunamadı."
        
        panes = []
        sira_indices = [i for i, col in enumerate(df_raw.columns) if 'SIRA' in str(col).upper()]
        
        for idx in sira_indices:
            if idx + 2 < len(df_raw.columns):
                pane = df_raw.iloc[:, idx : idx + 3].copy()
                pane.columns = ['SIRA', 'OLUKLU MUKAVVA', 'ESNEK AMBALAJ']
                
                pane['SIRA'] = pd.to_numeric(pane['SIRA'], errors='coerce')
                pane = pane.dropna(subset=['SIRA'])
                pane['SIRA'] = pane['SIRA'].astype(int)
                pane = pane.fillna('')
                
                if not pane.empty:
                    panes.append(pane)
                    
        return panes, None
    except Exception as e:
        return [], str(e)

panes_list, hata_mesaji = veri_getir_ve_isle()

# --- ÖZEL HTML TABLO OLUŞTURUCU (Dark Mode + Mobil Korumalı) ---
def ozel_tablo_ciz(df):
    html = "<style>"
    html += ".tablo-sarmalayici { overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; margin-bottom: 20px; }"
    html += ".ozel-tablo { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; box-shadow: 0 0 5px rgba(0,0,0,0.1); background-color: #ffffff !important; min-width: 600px; }"
    html += ".ozel-tablo th { background-color: #002266 !important; color: #ffffff !important; text-align: left; padding: 8px; font-size: 13px; border: 1px solid #004d99; }"
    html += ".ozel-tablo td { padding: 8px; border: 1px solid #cce0ff; font-size: 13px; color: #002266 !important; background-color: #ffffff !important; word-wrap: break-word; word-break: break-word; }"
    html += ".ozel-tablo tr:nth-child(even) td { background-color: #f8fbff !important; }"
    html += ".sira-sutunu { width: 40px !important; text-align: center !important; font-weight: bold; }"
    html += "</style>"
    html += "<div class='tablo-sarmalayici'><table class='ozel-tablo'>"
    html += "<thead><tr><th class='sira-sutunu'>Sıra</th><th>OLUKLU MUKAVVA</th><th>ESNEK AMBALAJ</th></tr></thead><tbody>"
    
    for index, row in df.iterrows():
        html += f"<tr><td class='sira-sutunu'>{row['SIRA']}</td><td>{row['OLUKLU MUKAVVA']}</td><td>{row['ESNEK AMBALAJ']}</td></tr>"
        
    html += "</tbody></table></div>"
    return html

# --- GÖSTERİM ---
if panes_list:
    num_panes = len(panes_list)
    st_cols = st.columns(num_panes)
    
    for idx, pane_df in enumerate(panes_list):
        with st_cols[idx]:
            st.markdown(ozel_tablo_ciz(pane_df), unsafe_allow_html=True)
else:
    # Hata varsa artık sadece "Liste Boş" demeyecek, hatanın ne olduğunu kırmızı kutuda yazacak
    if hata_mesaji:
        st.error(f"Sistem Hatası: {hata_mesaji}")
    else:
        st.warning("Veriler şu an yüklenemedi veya liste boş. Lütfen E-tablo bağlantısını kontrol ediniz.")

# --- ALT BİLGİ ---
st.markdown("<br><p style='text-align: center; color: #a9a9a9; font-size: 12px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
