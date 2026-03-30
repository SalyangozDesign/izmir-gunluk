import streamlit as st
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İzmir Günlük Paylaşım", page_icon="📋", layout="wide")

# GÖRSEL TEMİZLİK VE EK GİZLEMELER (Mevcut yapı bozulmadan)
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    /* Tüm Streamlit watermark/menü gizleme */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stBottom"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    button[title="View fullscreen"] {display: none !important;}
    
    /* Tablonun daha derli toplu görünmesi için CSS */
    [data-testid="stDataFrame"] { border: 1px solid #e6e9ef; border-radius: 8px; overflow: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
# Tarihi dinamik olarak bugüne ayarlayalım
import datetime
bugun = datetime.date.today().strftime("%d.%m.%Y")

st.markdown(f"""
    <div style="background-color: #1f77b4; padding: 10px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style='color: white; text-align: center; margin: 0px;'>📋 İzmir Bölge Günlük Üretim Listesi</h2>
        <p style='color: #e0e0e0; text-align: center; margin: 0px;'>{bugun}</p>
    </div>
""", unsafe_allow_html=True)

# --- VERİ ÇEKME VE İŞLEME (ESKİ SİSTEMİN BOZULMAYAN KALBİ) ---
@st.cache_data(ttl=300)
def veri_getir_ve_isle():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=90150185&single=true&output=csv"
    try:
        # E-tablodaki birleştirilmiş hücreler yüzünden header=1 diyerek
        # 2. satırı (SIRA, OLUKLU, ESNEK yazan satır) başlık yapıyoruz
        # Bu, "Unnamed" sorununu kökten çözer.
        df_raw = pd.read_csv(url, header=1) 
        
        # 1. Adım: Pandas'ın "Unnamed: X" olarak okuduğu boş ayırıcı sütunları temizle
        # SADECE SIRA, OLUKLU ve ESNEK kelimelerini içeren sütunları tut
        cols_to_keep = [c for c in df_raw.columns if any(h in c for h in ['SIRA', 'OLUKLU MUKAVVA', 'ESNEK AMBALAJ'])]
        df_cleaned = df_raw[cols_to_keep]
        
        # 2. Adım: Verileri dinamik olarak yan yana parçalara (pane) böl (Haftalık liste gibi)
        panes = []
        # 'SIRA' ile başlayan her sütun yeni bir parça başlangıcıdır
        sira_indices = [i for i, col in enumerate(df_cleaned.columns) if col.startswith('SIRA')]
        
        for start_idx in sira_indices:
            # Her parça 3 sütundur: SIRA, OLUKLU, ESNEK
            pane = df_cleaned.iloc[:, start_idx : start_idx + 3].copy()
            # Sütun isimlerini standart yap
            pane.columns = ['SIRA', 'OLUKLU MUKAVVA', 'ESNEK AMBALAJ']
            
            # 3. Adım: Satır temizliği - Boş olan parçaları sil (Excel'de aşağıya sarkan boşluklar)
            pane = pane.replace('', pd.NA).dropna(how='all', subset=['OLUKLU MUKAVVA', 'ESNEK AMBALAJ']).fillna('')
            
            if not pane.empty:
                # SIRA sütununu tamsayı yap (1,2,3,4 gibi)
                pane['SIRA'] = pd.to_numeric(pane['SIRA'], errors='coerce').fillna(0).astype(int)
                # Sıra no 0'dan büyük olanları tut (Pandas başlık satırını tekrar okursa diye)
                pane = pane[pane['SIRA'] > 0]
                panes.append(pane)
                
        return panes
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
        return []

panes_list = veri_getir_ve_isle()

# --- GÖSTERİM (E-TABLO GİBİ YAN YANA PANELLER) ---
if panes_list:
    # Kaç parça veri varsa (hafta gibi) o kadar yan yana sütun oluştur
    num_panes = len(panes_list)
    st_cols = st.columns(num_panes)
    
    # Her parça için tabloyu oluştur
    for idx, pane_df in enumerate(panes_list):
        with st_cols[idx]:
            # Tablo ayarları (SIRA küçük, diğerleri geniş)
            st.dataframe(
                pane_df, 
                hide_index=True, 
                use_container_width=True,
                # Sütun genişliklerini istediğiniz gibi küçültüp büyütebiliriz
                column_config={
                    "SIRA": st.column_config.NumberColumn("SIRA", format="%d", width="small"),
                    "OLUKLU MUKAVVA": st.column_config.TextColumn("OLUKLU MUKAVVA", width="large"),
                    "ESNEK AMBALAJ": st.column_config.TextColumn("ESNEK AMBALAJ", width="large"),
                }
            )
else:
    st.warning("Veriler şu an yüklenemedi veya liste boş. Lütfen E-tabloyu kontrol ediniz.")

# --- ALT BİLGİ ---
st.markdown("<br><hr><p style='text-align: center; color: #a9a9a9; font-size: 13px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
