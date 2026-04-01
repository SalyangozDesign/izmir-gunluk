import streamlit as st
import pandas as pd
import datetime
import re

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

# --- AKILLI VE DİNAMİK VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=120) 
def veri_getir_ve_isle():
    # Doğru ve Güncel GID Numaralı Linkiniz
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=374780490&single=true&output=csv"
    try:
        df_raw = pd.read_csv(url, header=None, on_bad_lines='skip') 
        
        # SIRA kelimesinin hangi satırda olduğunu otomatik bul (Akıllı Radar)
        header_idx = -1
        for i in range(min(15, len(df_raw))):
            row_str = " ".join(df_raw.iloc[i].astype(str)).upper()
            if "SIRA" in row_str:
                header_idx = i
                break
                
        if header_idx != -1:
            raw_headers = df_raw.iloc[header_idx].astype(str).tolist()
            
            # Excel'deki birleştirilmiş (merged) hücreleri CSV'de tespit edip sağa doğru dolduruyoruz (Forward-Fill)
            # Bu sayede D sütununa "ESNEK AMBALAJ" başlığı otomatik kopyalanır.
            clean_headers = []
            last_val = ""
            for h in raw_headers:
                h_clean = h.strip()
                if h_clean.upper() in ["NAN", "NONE", ""]:
                    clean_headers.append(last_val)
                else:
                    clean_headers.append(h_clean)
                    last_val = h_clean
            
            # Pandas aynı isimde sütunları sevmediği için geçici olarak numaralandırıyoruz (Örn: ESNEK AMBALAJ_1)
            unique_headers = []
            counts = {}
            for h in clean_headers:
                if h == "":
                    unique_headers.append("GIZLI")
                    continue
                if h in counts:
                    counts[h] += 1
                    unique_headers.append(f"{h}_{counts[h]}")
                else:
                    counts[h] = 0
                    unique_headers.append(h)
                    
            df_raw.columns = unique_headers
            df = df_raw.iloc[header_idx+1:].reset_index(drop=True)
            
            # Sadece başlığı SIRA, OLUKLU veya ESNEK olan tüm sütunları (sınır olmaksızın) tut
            cols_to_keep = [c for c in df.columns if any(k in c.upper() for k in ['SIRA', 'OLUKLU', 'ESNEK'])]
            df = df[cols_to_keep]
            
            # Sıra sütununu bul ve boş satırları temizle
            sira_col = [c for c in df.columns if 'SIRA' in c.upper()][0]
            df[sira_col] = pd.to_numeric(df[sira_col], errors='coerce')
            df = df.dropna(subset=[sira_col])
            df[sira_col] = df[sira_col].astype(int)
            df = df.fillna('')
            
            return df, None
        else:
            return pd.DataFrame(), "Tabloda 'SIRA' başlığı bulunamadı. Lütfen E-Tabloyu kontrol edin."
    except Exception as e:
        return pd.DataFrame(), f"Sistem Hatası: Bağlantı kurulamadı veya dosya bulunamadı. Detay: {str(e)}"

df_liste, hata_mesaji = veri_getir_ve_isle()

# --- ÖZEL HTML TABLO OLUŞTURUCU (Tam Dinamik) ---
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
    
    html += "<thead><tr>"
    for col in df.columns:
        # Geçici olarak eklediğimiz "ESNEK AMBALAJ_1" gibi takıları silerek orijinal başlığı (Örn: ESNEK AMBALAJ) göster
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

# --- GÖSTERİM ---
if not df_liste.empty:
    st.markdown(ozel_tablo_ciz(df_liste), unsafe_allow_html=True)
else:
    if hata_mesaji:
        st.error(hata_mesaji)
    else:
        st.warning("Veriler şu an yüklenemedi veya liste boş. Lütfen E-tablo bağlantısını kontrol ediniz.")

# --- ALT BİLGİ ---
st.markdown("<br><p style='text-align: center; color: #a9a9a9; font-size: 12px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
