import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İzmir Günlük Paylaşım", page_icon="📋", layout="wide")

# GÖRSEL TEMİZLİK (Streamlit reklamlarını ve butonları gizle)
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stBottom"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    button[title="View fullscreen"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 8])
with col1:
    st.markdown("<h1 style='text-align: right;'>📋</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("<h2 style='color: #1f77b4; margin-bottom: 0px;'>İzmir Bölge Günlük Liste</h2>", unsafe_allow_html=True)
    st.caption("Dijital Klişecilik San. ve Tic. Ltd. Şti.")

st.divider()

# --- VERİ ÇEKME VE GÖSTERME ---
# Veriyi her 5 dakikada bir günceller (ttl=300 saniye)
@st.cache_data(ttl=300)
def veri_getir():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=90150185&single=true&output=csv"
    try:
        df = pd.read_csv(url)
        # Tamamen boş olan satır ve sütunları temizle
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0).fillna('')
        return df
    except:
        return pd.DataFrame()

df_liste = veri_getir()

if not df_liste.empty:
    # Tabloyu tam ekran genişliğinde ve index numaraları olmadan göster
    st.dataframe(df_liste, use_container_width=True, hide_index=True)
else:
    st.error("Veriler şu an yüklenemiyor, lütfen tablo bağlantısını kontrol ediniz.")

st.markdown("<br><hr><p style='text-align: center; color: #a9a9a9; font-size: 13px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Merkezi © 2026</p>", unsafe_allow_html=True)
