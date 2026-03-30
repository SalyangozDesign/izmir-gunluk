import streamlit as st
import pandas as pd
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İzmir Günlük Paylaşım", page_icon="📋", layout="wide")

# GÖRSEL TEMİZLİK VE TABLO STİLİ (Streamlit kalıntılarını gizle)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stBottom"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    button[title="View fullscreen"] {display: none !important;}
    
    /* Tablo kenarlıklarını yumuşatıp şıklaştırıyoruz */
    [data-testid="stDataFrame"] { border: 1px solid #e6e9ef; border-radius: 8px; overflow: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK (Tarihi her gün otomatik günceller) ---
bugun = datetime.date.today().strftime("%d.%m.%Y")

st.markdown(f"""
    <div style="background-color: #00569c; padding: 10px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style='color: white; text-align: center; margin: 0px;'>📋 İzmir Şube Ofisi Üretim Listesi</h2>
        <p style='color: #e0e0e0; text-align: center; margin: 0px;'>{bugun}</p>
    </div>
""", unsafe_allow_html=True)

# --- AKILLI VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=300) # 5 dakikada bir güncellenir
def veri_getir_ve_isle():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=90150185&single=true&output=csv"
    try:
        # skiprows=2 diyerek ilk iki oyalayıcı başlık satırını atlıyor ve asıl tabloyu buluyoruz!
        df_raw = pd.read_csv(url, skiprows=2) 
        
        panes = []
        # "SIRA" kelimesini içeren tüm kolonların indekslerini bul (40'ı geçince yan yana eklenen listeleri yakalar)
        sira_indices = [i for i, col in enumerate(df_raw.columns) if 'SIRA' in str(col).upper()]
        
        for idx in sira_indices:
            # Sıra sütunu ve yanındaki 2 sütunu al (Toplam 3 sütunluk set)
            if idx + 2 < len(df_raw.columns):
                pane = df_raw.iloc[:, idx : idx + 3].copy()
                pane.columns = ['SIRA', 'OLUKLU MUKAVVA', 'ESNEK AMBALAJ']
                
                # Sadece Sıra kısmında gerçekten rakam olan satırları filtrele (Boşlukları yok et)
                pane['SIRA'] = pd.to_numeric(pane['SIRA'], errors='coerce')
                pane = pane.dropna(subset=['SIRA'])
                pane['SIRA'] = pane['SIRA'].astype(int)
                
                # NaN yazan boş hücreleri temizle
                pane = pane.fillna('')
                
                if not pane.empty:
                    panes.append(pane)
                    
        return panes
    except Exception as e:
        return []

panes_list = veri_getir_ve_isle()

# --- GÖSTERİM (E-TABLO GİBİ SÜTUN GENİŞLİKLERİ AYARLANMIŞ) ---
if panes_list:
    num_panes = len(panes_list)
    # Kaç liste varsa o kadar yan yana kolon açar
    st_cols = st.columns(num_panes)
    
    for idx, pane_df in enumerate(panes_list):
        with st_cols[idx]:
            st.dataframe(
                pane_df, 
                hide_index=True, 
                use_container_width=True,
                # SIRA sütununu tam rakama göre (50 piksel) kesin olarak sabitliyoruz
                column_config={
                    "SIRA": st.column_config.NumberColumn("Sıra", format="%d", width=50),
                    "OLUKLU MUKAVVA": st.column_config.TextColumn("OLUKLU MUKAVVA"),
                    "ESNEK AMBALAJ": st.column_config.TextColumn("ESNEK AMBALAJ"),
                }
            )
else:
    st.warning("Veriler şu an yüklenemedi veya liste boş. Lütfen E-tablo bağlantısını kontrol ediniz.")

# --- ALT BİLGİ ---
st.markdown("<br><hr><p style='text-align: center; color: #a9a9a9; font-size: 13px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
