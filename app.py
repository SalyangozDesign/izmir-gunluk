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

# --- AKILLI VE SINIRLANDIRILMIŞ VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=120) 
def veri_getir_ve_isle():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=374780490&single=true&output=csv"
    try:
        df_raw = pd.read_csv(url, header=None, on_bad_lines='skip') 
        
        # SIRA kelimesinin hangi satırda olduğunu otomatik bul
        header_idx = -1
        for i in range(min(15, len(df_raw))):
            row_str = str(df_raw.iloc[i, 0]).upper() # Sadece A sütununa (indeks 0) bakıyoruz
            if "SIRA" in row_str:
                header_idx = i
                break
                
        if header_idx != -1:
            # 1. KURAL: Tabloyu sonsuzluğa uzatmamak için sadece SIRA ve yanındaki 5 sütuna (A'dan F'ye kadar) bak!
            max_cols = min(6, len(df_raw.columns))
            raw_headers = df_raw.iloc[header_idx, 0:max_cols].astype(str).tolist()
            
            # Excel'deki birleştirilmiş (merged) hücreleri tespit edip sağa kopyalıyoruz
            clean_headers = []
            last_val = ""
            for h in raw_headers:
                h_clean = h.strip()
                if h_clean.upper() in ["NAN", "NONE", ""]:
                    clean_headers.append(last_val)
                else:
                    clean_headers.append(h_clean)
                    last_val = h_clean
            
            # Aynı isimde olanlara numara veriyoruz (ESNEK AMBALAJ_2 gibi)
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
                    counts[h] = 1
                    unique_headers.append(h)
                    
            # 40 Sıra No limiti için sadece alttaki 45 satırı okuyoruz
            df = df_raw.iloc[header_idx+1 : header_idx+45, 0:max_cols].copy()
            df.columns = unique_headers
            
            # SIRA sütununu tamsayı yap ve geçersiz (boş) satırları sil (Sadece 1'den 40'a kadar olanlar kalır)
            sira_col = [c for c in df.columns if 'SIRA' in c.upper()][0]
            df[sira_col] = pd.to_numeric(df[sira_col], errors='coerce')
            df = df.dropna(subset=[sira_col])
            df[sira_col] = df[sira_col].astype(int)
            df = df.fillna('')
            
            # 2. KURAL: Yana açılan sütunların (Örn: ESNEK AMBALAJ_2) içi TOPTAN BOŞSA o sütunu sil.
            cols_to_keep = []
            for col in df.columns:
                if 'GIZLI' in col.upper():
                    continue
                if 'SIRA' in col.upper():
                    cols_to_keep.append(col)
                else:
                    # Sütunun içinde harf/sayı var mı diye kontrol et
                    if df[col].astype(str).str.strip().replace('', pd.NA).notna().any():
                        cols_to_keep.append(col)
                        
            df = df[cols_to_keep]
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
        # Geçici olarak eklediğimiz "_2" gibi sayıları gizleyerek, sütunun orijinal ismini (ESNEK AMBALAJ) yazıyoruz
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
