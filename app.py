import streamlit as st
import pandas as pd
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İzmir Günlük Paylaşım", page_icon="📋", layout="wide")

# GÖRSEL TEMİZLİK (Streamlit kalıntılarını gizle)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stBottom"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
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

# --- AKILLI VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=300)
def veri_getir_ve_isle():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=90150185&single=true&output=csv"
    try:
        df_raw = pd.read_csv(url, skiprows=2) 
        
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
                    
        return panes
    except Exception as e:
        return []

panes_list = veri_getir_ve_isle()

# --- ÖZEL HTML TABLO OLUŞTURUCU (Tam Excel Görünümü - Hatasız) ---
def ozel_tablo_ciz(df):
    # Boşluklar yüzünden koda dönüşmemesi için her şeyi tek satır mantığıyla birleştiriyoruz
    html = "<style>"
    html += ".ozel-tablo { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; margin-bottom: 20px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }"
    html += ".ozel-tablo th { background-color: #002266; color: white; text-align: left; padding: 8px; font-size: 13px; border: 1px solid #004d99; }"
    html += ".ozel-tablo td { padding: 8px; border: 1px solid #cce0ff; font-size: 13px; color: #002266; }"
    html += ".ozel-tablo tr:nth-child(even) { background-color: #f8fbff; }"
    html += ".sira-sutunu { width: 40px !important; text-align: center !important; font-weight: bold; }"
    html += "</style>"
    html += "<table class='ozel-tablo'>"
    html += "<thead><tr><th class='sira-sutunu'>Sıra</th><th>OLUKLU MUKAVVA</th><th>ESNEK AMBALAJ</th></tr></thead><tbody>"
    
    for index, row in df.iterrows():
        html += f"<tr><td class='sira-sutunu'>{row['SIRA']}</td><td>{row['OLUKLU MUKAVVA']}</td><td>{row['ESNEK AMBALAJ']}</td></tr>"
        
    html += "</tbody></table>"
    return html

# --- GÖSTERİM ---
if panes_list:
    num_panes = len(panes_list)
    st_cols = st.columns(num_panes)
    
    for idx, pane_df in enumerate(panes_list):
        with st_cols[idx]:
            st.markdown(ozel_tablo_ciz(pane_df), unsafe_allow_html=True)
else:
    st.warning("Veriler şu an yüklenemedi veya liste boş. Lütfen E-tablo bağlantısını kontrol ediniz.")

# --- ALT BİLGİ ---
st.markdown("<br><p style='text-align: center; color: #a9a9a9; font-size: 12px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
