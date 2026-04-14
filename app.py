import streamlit as st
import pandas as pd
import datetime
import re
import time 

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
    
    /* Sekme (Tab) Metinlerini Büyütme ve Renklendirme */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px !important;
        font-weight: bold !important;
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

# --- AKILLI, GOOGLE CACHE KIRICI VE FLOAT ZIRHLI ORTAK MOTOR ---
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
            max_cols = min(6, len(df_raw.columns))
            df_subset = df_raw.iloc[header_idx : header_idx+45, 0:max_cols].copy()
            
            raw_headers = df_subset.iloc[0].tolist()
            
            clean_headers = []
            last_val = "SUTUN"
            for h in raw_headers:
                h_clean = str(h).strip().upper()
                if h_clean in ["NAN", "NONE", ""]:
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
                    counts[h] = 1
                    unique_headers.append(h)
            
            df_subset.columns = unique_headers
            df_data = df_subset.iloc[1:].copy()
            
            sira_col = df_data.columns[0]
            df_data[sira_col] = pd.to_numeric(df_data[sira_col], errors='coerce')
            df_data = df_data.dropna(subset=[sira_col])
            df_data[sira_col] = df_data[sira_col].astype(int)
            
            cols_to_keep = []
            for col in df_data.columns:
                if 'SIRA' in col.upper():
                    cols_to_keep.append(col)
                else:
                    is_valid = df_data[col].apply(lambda x: str(x).strip() if pd.notna(x) else "").replace(['nan', 'NaN', 'None', ''], pd.NA).notna().any()
                    if is_valid:
                        cols_to_keep.append(col)
            
            df_final = df_data[cols_to_keep].fillna('')
            return df_final, None
        else:
            return pd.DataFrame(), "Tabloda 'SIRA' başlığı bulunamadı. Lütfen E-Tabloyu kontrol edin."
    except Exception as e:
        return pd.DataFrame(), f"Sistem Hatası: Bağlantı kurulamadı veya dosya bulunamadı. Detay: {str(e)}"

# --- ÖZEL HTML TABLO OLUŞTURUCU (RENK PARAMETRELİ) ---
def ozel_tablo_ciz(df, renk_tema="#002266", kenar_renk="#004d99"):
    html = "<style>"
    html += ".tablo-sarmalayici { overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch; margin-bottom: 20px; }"
    html += ".ozel-tablo { width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; box-shadow: 0 0 5px rgba(0,0,0,0.1); background-color: #ffffff !important; min-width: 600px; }"
    html += f".ozel-tablo th {{ background-color: {renk_tema} !important; color: #ffffff !important; text-align: left; padding: 8px; font-size: 14px; border: 1px solid {kenar_renk}; }}"
    html += f".ozel-tablo td {{ padding: 8px; border: 1px solid #e6e6e6; font-size: 13px; color: #000000 !important; background-color: #ffffff !important; word-wrap: break-word; word-break: break-word; }}"
    html += ".ozel-tablo tr:nth-child(even) td { background-color: #f8fbff !important; }"
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
    
    for index, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            if 'SIRA' in col.upper():
                html += f"<td class='sira-sutunu'>{row[col]}</td>"
            else:
                html += f"<td>{row[col]}</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    return html

# --- VERİ LİNKLERİ VE SEKMELER ---
gunluk_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=374780490&single=true&output=csv"
acil_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=1428130476&single=true&output=csv"

t_gunluk, t_acil = st.tabs(["📋 Günlük Üretim Listesi", "🚨 Acil Üretim Listesi"])

with t_gunluk:
    df_gunluk, hata_gunluk = veri_getir_ve_isle(gunluk_url)
    if not df_gunluk.empty:
        st.markdown(ozel_tablo_ciz(df_gunluk, renk_tema="#002266", kenar_renk="#004d99"), unsafe_allow_html=True)
    else:
        if hata_gunluk:
            st.error(hata_gunluk)
        else:
            st.warning("Veriler şu an yüklenemedi veya günlük liste boş.")

with t_acil:
    df_acil, hata_acil = veri_getir_ve_isle(acil_url)
    if not df_acil.empty:
        # Acil listesi için koyu kırmızı (bordo) başlıklar
        st.markdown(ozel_tablo_ciz(df_acil, renk_tema="#8b0000", kenar_renk="#b30000"), unsafe_allow_html=True)
    else:
        if hata_acil:
            st.error(hata_acil)
        else:
            st.success("🎉 Harika! Şu an için bekleyen hiçbir acil iş görünmüyor.")

# --- ALT BİLGİ ---
st.markdown("<br><p style='text-align: center; color: #a9a9a9; font-size: 12px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
