import streamlit as st
import pandas as pd
import datetime
import re
import time 

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İzmir Günlük Paylaşım", page_icon="📋", layout="wide")

# GÖRSEL TEMİZLİK VE KURUMSAL TEMA (NAVY & RED HIGHLIGHT)
st.markdown("""
    <style>
    /* Zorunlu Light Mode */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    /* Streamlit Gereksiz Öğeleri Gizleme */
    [data-testid="stBottom"], [data-testid="stToolbar"] {display: none !important;}
    .viewerBadge_container__1QSob, .stAppDeployButton {display: none !important;}
    button[title="View fullscreen"] {display: none !important;}
    
    /* Sekme Başlıklarını Özelleştirme */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px !important;
        font-weight: bold !important;
    }
    /* Acil Sekmesini Kırmızı Yapma */
    .stTabs [data-baseweb="tab-list"] button:nth-child(2) [data-testid="stMarkdownContainer"] p {
        color: #ff0000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- TARİH VE GÜN AYARI ---
gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
bugun = datetime.date.today()
tarih_str = bugun.strftime("%d.%m.%Y") + " " + gunler[bugun.weekday()]

# --- ANA BAŞLIK ---
st.markdown(f"""
<div style="background-color: #004d99; padding: 15px; margin-bottom: 0px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
<h2 style='color: white; text-align: center; margin: 0px; font-size: 24px;'>📋 İZMİR ŞUBE OFİSİ ÜRETİM LİSTELERİ</h2>
</div>
<div style="background-color: #e6f0ff; padding: 8px; margin-bottom: 20px; border-bottom: 2px solid #004d99; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
<h4 style='color: #004d99; text-align: center; margin: 0px; font-size: 16px;'>{tarih_str}</h4>
</div>
""", unsafe_allow_html=True)

# --- AKILLI VERİ MOTORU (SEVK VE SAAT DESTEKLİ) ---
@st.cache_data(ttl=60) 
def veri_getir_ve_isle(url):
    zaman_damgasi = int(time.time())
    safe_url = f"{url}&_={zaman_damgasi}" if "?" in url else f"{url}?_={zaman_damgasi}"
    
    try:
        df_raw = pd.read_csv(safe_url, header=None, on_bad_lines='skip') 
        
        header_idx = -1
        for i in range(min(15, len(df_raw))):
            row_str = str(df_raw.iloc[i, 0]).upper()
            if "SIRA" in row_str:
                header_idx = i
                break
                
        if header_idx != -1:
            # G ve H sütunlarını (Sevk ve Saat) kapsamak için tarama sınırını 10 sütuna çıkardık
            max_cols = min(10, len(df_raw.columns))
            df_subset = df_raw.iloc[header_idx : header_idx+45, 0:max_cols].copy()
            
            raw_headers = df_subset.iloc[0].tolist()
            
            clean_headers = []
            last_val = "SUTUN"
            for h in raw_headers:
                h_clean = str(h).strip().upper()
                if h_clean in ["NAN", "NONE", "", "UNNAMED"]:
                    clean_headers.append(last_val)
                else:
                    clean_headers.append(h_clean)
                    last_val = h_clean
                    
            unique_headers = []
            counts = {}
            for h in clean_headers:
                if h in counts:
                    counts[h] += 1
                    unique_headers.append(f"{h}_{counts[h]}")
                else:
                    counts[h] = 0
                    unique_headers.append(h)
            
            df_subset.columns = unique_headers
            df_data = df_subset.iloc[1:].copy()
            
            sira_col = df_data.columns[0]
            df_data[sira_col] = pd.to_numeric(df_data[sira_col], errors='coerce')
            df_data = df_data.dropna(subset=[sira_col])
            df_data[sira_col] = df_data[sira_col].astype(int)
            
            # Sütunları temizleme ve filtreleme
            cols_to_keep = []
            for col in df_data.columns:
                if 'SIRA' in col.upper():
                    cols_to_keep.append(col)
                else:
                    # Hücrede gerçekten veri var mı kontrolü (Float zırhlı)
                    is_valid = df_data[col].apply(lambda x: str(x).strip() if pd.notna(x) else "").replace(['nan', 'NaN', 'None', ''], pd.NA).notna().any()
                    if is_valid:
                        cols_to_keep.append(col)
            
            df_final = df_data[cols_to_keep].fillna('')
            return df_final, None
        else:
            return pd.DataFrame(), "Tabloda 'SIRA' başlığı bulunamadı."
    except Exception as e:
        return pd.DataFrame(), f"Bağlantı Hatası: {str(e)}"

# --- HTML TABLO OLUŞTURUCU ---
def ozel_tablo_ciz(df, acil_mod=False):
    # Kurumsal Renkler (Dijital Klişe Mavi/Navy)
    renk_tema = "#002266"
    kenar_renk = "#004d99"
    
    html = "<style>"
    html += ".tablo-sarmalayici { overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; margin-bottom: 20px; }"
    html += ".ozel-tablo { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; background-color: #ffffff !important; min-width: 800px; }"
    html += f".ozel-tablo th {{ background-color: {renk_tema} !important; color: #ffffff !important; text-align: left; padding: 10px; font-size: 13px; border: 1px solid {kenar_renk}; }}"
    html += ".ozel-tablo td { padding: 10px; border: 1px solid #e0e0e0; font-size: 13px; color: #000000 !important; background-color: #ffffff !important; word-wrap: break-word; }"
    html += ".ozel-tablo tr:nth-child(even) td { background-color: #f9f9f9 !important; }"
    html += ".sira-sutunu { width: 40px !important; text-align: center !important; font-weight: bold; }"
    html += "</style>"
    
    html += "<div class='tablo-sarmalayici'><table class='ozel-tablo'>"
    
    html += "<thead><tr>"
    for col in df.columns:
        display_name = re.sub(r'_\d+$', '', col)
        if 'SIRA' in display_name.upper():
            html += f"<th class='sira-sutunu'>Sıra</th>"
        else:
            html += f"<th>{display_name}</th>"
    html += "</tr></thead><tbody>"
    
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = str(row[col])
            if 'SIRA' in col.upper():
                html += f"<td class='sira-sutunu'>{val}</td>"
            else:
                html += f"<td>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    return html

# --- SEKMELER ---
gunluk_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=374780490&single=true&output=csv"
acil_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=1428130476&single=true&output=csv"

t_gunluk, t_acil = st.tabs(["📋 Günlük Üretim Listesi", "🚨 Acil Üretim Listesi"])

with t_gunluk:
    df_g, err_g = veri_getir_ve_isle(gunluk_url)
    if not df_g.empty:
        st.markdown(ozel_tablo_ciz(df_g), unsafe_allow_html=True)
    else:
        st.error(err_g) if err_g else st.warning("Günlük liste boş.")

with t_acil:
    # Sadece bu sekmedeki başlığı kırmızı yapıyoruz
    st.markdown("<h3 style='color: #ff0000; text-align: center;'>🚨 ACİL ÜRETİM LİSTESİ</h3>", unsafe_allow_html=True)
    df_a, err_a = veri_getir_ve_isle(acil_url)
    if not df_a.empty:
        st.markdown(ozel_tablo_ciz(df_a, acil_mod=True), unsafe_allow_html=True)
    else:
        st.success("🎉 Şu an bekleyen acil iş bulunmuyor.")

# --- ALT BİLGİ ---
st.markdown("<br><p style='text-align: center; color: #a9a9a9; font-size: 12px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
