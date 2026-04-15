import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import re
import time 

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İzmir Günlük Paylaşım", page_icon="📋", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; }
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    [data-testid="stBottom"], [data-testid="stToolbar"] {display: none !important;}
    .viewerBadge_container__1QSob, .stAppDeployButton {display: none !important;}
    
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px !important; font-weight: bold !important;
    }
    .stTabs [data-baseweb="tab-list"] button:nth-child(3) [data-testid="stMarkdownContainer"] p {
        color: #ff0000 !important;
    }
    </style>
""", unsafe_allow_html=True)

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
bugun = datetime.date.today()
tarih_str = bugun.strftime("%d.%m.%Y") + " " + gunler[bugun.weekday()]

st.markdown(f"""
<div style="background-color: #004d99; padding: 15px; margin-bottom: 0px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
<h2 style='color: white; text-align: center; margin: 0px; font-size: 24px;'>📋 İZMİR ŞUBE OFİSİ ÜRETİM LİSTELERİ</h2>
</div>
<div style="background-color: #e6f0ff; padding: 8px; margin-bottom: 20px; border-bottom: 2px solid #004d99; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
<h4 style='color: #004d99; text-align: center; margin: 0px; font-size: 16px;'>{tarih_str}</h4>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=1) 
def veri_getir_ve_isle(url):
    zaman_damgasi = int(time.time())
    safe_url = f"{url}&_={zaman_damgasi}" if "?" in url else f"{url}?_={zaman_damgasi}"
    
    url_map = {}
    try:
        df_raw = pd.read_csv(safe_url, header=None, names=range(50), on_bad_lines='skip', engine='python') 
        
        for r in range(3, len(df_raw)):
            url_val = str(df_raw.iloc[r, 30]).strip()
            if "http" in url_val:
                clean_url = url_val[url_val.find("http"):].split()[0].replace("/view?usp=drivesdk", "/preview").replace("/view", "/preview")
                oid = str(df_raw.iloc[r, 25]).strip().replace('.0', '')
                if oid and oid not in ["MANUEL", "-", "nan", "None", ""]: url_map[oid] = clean_url
                is_val = str(df_raw.iloc[r, 27]).strip()
                if is_val and is_val not in ["nan", "None", ""]:
                    found_numbers = re.findall(r'(?<!\d)(\d{5,6})(?!\d)', is_val)
                    for num in found_numbers: url_map[num] = clean_url

        for r in range(3, len(df_raw)):
            url_val = str(df_raw.iloc[r, 36]).strip()
            if "http" in url_val:
                clean_url = url_val[url_val.find("http"):].split()[0].replace("/view?usp=drivesdk", "/preview").replace("/view", "/preview")
                oid = str(df_raw.iloc[r, 31]).strip().replace('.0', '')
                if oid and oid not in ["MANUEL", "-", "nan", "None", ""]: url_map[oid] = clean_url
                is_val = str(df_raw.iloc[r, 33]).strip()
                if is_val and is_val not in ["nan", "None", ""]:
                    found_numbers = re.findall(r'(?<!\d)(\d{5,6})(?!\d)', is_val)
                    for num in found_numbers: url_map[num] = clean_url
                
        header_idx = -1
        for i in range(min(15, len(df_raw))):
            if "SIRA" in str(df_raw.iloc[i, 0]).upper():
                header_idx = i; break
                
        if header_idx != -1:
            max_cols = min(15, len(df_raw.columns))
            df_subset = df_raw.iloc[header_idx : header_idx+45, 0:max_cols].copy()
            df_subset.dropna(axis=1, how='all', inplace=True)
            
            raw_headers = df_subset.iloc[0].tolist()
            clean_headers = []
            last_val = "SUTUN"
            for h in raw_headers:
                h_clean = str(h).strip().upper()
                if h_clean in ["NAN", "NONE", "", "UNNAMED"]: clean_headers.append(last_val)
                else: clean_headers.append(h_clean); last_val = h_clean
                    
            unique_headers = []
            counts = {}
            for h in clean_headers:
                if h in counts: counts[h] += 1; unique_headers.append(f"{h}_{counts[h]}")
                else: counts[h] = 0; unique_headers.append(h)
            
            df_subset.columns = unique_headers
            df_data = df_subset.iloc[1:].copy()
            
            gorsel_col = next((c for c in df_data.columns if "GÖRSEL" in str(c).upper()), None)
            oid_col = next((c for c in df_data.columns if "ORDER ID" in str(c).upper()), None)
            is_col_visible = next((c for c in df_data.columns if "İŞİN İSMİ" in str(c).upper() or "ISIN ISMI" in str(c).upper()), None)
            
            if gorsel_col:
                for r in range(len(df_data)):
                    gorsel_url = str(df_data.iloc[r][gorsel_col]).strip()
                    if "http" in gorsel_url:
                        clean_url = gorsel_url[gorsel_url.find("http"):].split()[0].replace("/view?usp=drivesdk", "/preview").replace("/view", "/preview")
                        if oid_col:
                            oid_raw = str(df_data.iloc[r][oid_col]).strip().replace('.0', '')
                            if oid_raw and oid_raw not in ["MANUEL", "-", "nan", "None", ""]: url_map[oid_raw] = clean_url
                        if is_col_visible:
                            is_raw = str(df_data.iloc[r][is_col_visible]).strip()
                            if is_raw and is_raw not in ["nan", "None", ""]:
                                found_numbers = re.findall(r'(?<!\d)(\d{5,6})(?!\d)', is_raw)
                                for num in found_numbers: url_map[num] = clean_url
            
            sira_col = df_data.columns[0]
            df_data[sira_col] = pd.to_numeric(df_data[sira_col], errors='coerce')
            df_data = df_data.dropna(subset=[sira_col])
            df_data[sira_col] = df_data[sira_col].astype(int)
            
            cols_to_keep = []
            for col in df_data.columns:
                if 'GÖRSEL' in col.upper(): continue 
                if 'SIRA' in col.upper(): cols_to_keep.append(col)
                else:
                    is_valid = df_data[col].apply(lambda x: str(x).strip() if pd.notna(x) else "").replace(['nan', 'NaN', 'None', ''], pd.NA).notna().any()
                    if is_valid: cols_to_keep.append(col)
            
            df_final = df_data[cols_to_keep].fillna('')
            return df_final, url_map, None
        else:
            return pd.DataFrame(), {}, "Tabloda 'SIRA' başlığı bulunamadı."
    except Exception as e:
        return pd.DataFrame(), {}, f"Bağlantı Hatası: {str(e)}"

def ozel_tablo_html_olustur_gunluk(df, url_map):
    renk_tema = "#004d99"
    kenar_renk = "#003366"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #ffffff; }}
    .gorsel-buton {{ float: right; cursor: pointer; text-decoration: none; font-size: 12px; padding: 6px 12px; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white !important; border-radius: 20px; border: none; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: all 0.3s ease; animation: pulse 2s infinite; display: inline-flex; align-items: center; gap: 5px; }}
    .gorsel-buton:hover {{ transform: scale(1.1); box-shadow: 0 6px 12px rgba(0,0,0,0.3); background: linear-gradient(135deg, #c0392b, #a93226); }}
    @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }} }}
    .modal-overlay {{ display: none; position: fixed; z-index: 999999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.85); backdrop-filter: blur(5px); align-items: center; justify-content: center; cursor: pointer; }}
    .modal-content {{ position: relative; width: 95%; height: 90%; max-width: 1200px; background: #fff; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); padding: 10px; cursor: default; animation: zoomIn 0.3s ease; }}
    @keyframes zoomIn {{ from {{ transform: scale(0.9); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
    .close-btn {{ position: absolute; top: -10px; right: -10px; background: #e74c3c; color: white; border-radius: 50%; width: 36px; height: 36px; text-align: center; line-height: 34px; cursor: pointer; font-weight: bold; font-size: 24px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); border: 2px solid white; transition: 0.2s; z-index: 1000000; }}
    .close-btn:hover {{ background: #c0392b; transform: scale(1.1); }}
    .desktop-view {{ display: block; }} .mobile-view {{ display: none; padding: 5px; }} .tablo-sarmalayici {{ overflow-x: auto; width: 100%; padding-bottom: 20px; }} .ozel-tablo {{ width: 100%; border-collapse: collapse; min-width: 800px; }} .ozel-tablo th {{ background-color: {renk_tema}; color: #ffffff; text-align: left; padding: 12px; font-size: 14px; border: 1px solid {kenar_renk}; position: sticky; top: 0; z-index: 10; }} .ozel-tablo td {{ padding: 12px; border: 1px solid #e0e0e0; font-size: 13px; color: #000000; word-wrap: break-word; vertical-align: middle; }} .ozel-tablo tr:nth-child(even) td {{ background-color: #f9f9f9; }} .ozel-tablo tr:hover td {{ background-color: #f1f7ff; }} .sira-sutunu {{ width: 40px; text-align: center; font-weight: bold; }}
    @media screen and (max-width: 768px) {{ .desktop-view {{ display: none; }} .mobile-view {{ display: block; }} .mobile-category {{ background: {renk_tema}; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; text-align: center; font-size: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }} .mobile-card {{ background: #fff; border: 1px solid #d1d9e6; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); position: relative; }} .mc-sira {{ background: {renk_tema}; color: #fff; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; position: absolute; top: -10px; left: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }} .mc-body {{ padding-top: 5px; font-size: 13px; color: #333; line-height: 1.5; }} .gorsel-buton {{ float: none; width: 100%; justify-content: center; padding: 12px; font-size: 14px; margin-top: 12px; border-radius: 6px; }} }}
    </style>
    </head>
    <body>
    <div id="imgModal" class="modal-overlay" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation();"><span class="close-btn" onclick="closeModal()">&times;</span><iframe id="modalIframe" src="" style="width:100%; height:100%; border:none; border-radius:4px;"></iframe></div>
    </div>
    <div class='desktop-view'><div class='tablo-sarmalayici'><table class='ozel-tablo'><thead><tr>
    """
    
    for col in df.columns:
        display_name = re.sub(r'_\d+$', '', col)
        if 'SIRA' in display_name.upper(): html += "<th class='sira-sutunu'>Sıra</th>"
        else: html += f"<th>{display_name}</th>"
    html += "</tr></thead><tbody>"
    
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = str(row[col]).strip()
            if 'SIRA' in col.upper(): html += f"<td class='sira-sutunu'>{val}</td>"
            else:
                btn_html = ""
                all_numbers = re.findall(r'(?<!\d)(\d{5,6})(?!\d)', val)
                for num in all_numbers:
                    if num in url_map:
                        btn_html = f" <button onclick=\"openModal('{url_map[num]}')\" class='gorsel-buton'>🔍 İNCELE</button>"
                        break 
                html += f"<td>{val}{btn_html}</td>"
        html += "</tr>"
    html += "</tbody></table></div></div><div class='mobile-view'>"
    
    oluklu_cols = [c for c in df.columns if "OLUKLU" in str(c).upper()]
    esnek_cols = [c for c in df.columns if "ESNEK" in str(c).upper()]
    oluklu_jobs = [str(val).strip() for col in oluklu_cols for val in df[col] if str(val).strip() not in ["", "nan", "None"]]
    esnek_jobs = [str(val).strip() for col in esnek_cols for val in df[col] if str(val).strip() not in ["", "nan", "None"]]
                
    if oluklu_jobs:
        html += f"<div class='mobile-category'>📦 OLUKLU MUKAVVA</div>"
        for i, job in enumerate(oluklu_jobs, 1):
            btn_html = ""
            for num in re.findall(r'(?<!\d)(\d{5,6})(?!\d)', job):
                if num in url_map:
                    btn_html = f" <div style='margin-top:10px; border-top:1px solid #eee; padding-top:8px;'><button onclick=\"openModal('{url_map[num]}')\" class='gorsel-buton'>🔍 GÖRSELİ İNCELE</button></div>"
                    break
            html += f"<div class='mobile-card'><div class='mc-sira'>Sıra {i}</div><div class='mc-body'>{job}{btn_html}</div></div>"
            
    if esnek_jobs:
        html += f"<div class='mobile-category'>🍬 ESNEK AMBALAJ</div>"
        for i, job in enumerate(esnek_jobs, 1):
            btn_html = ""
            for num in re.findall(r'(?<!\d)(\d{5,6})(?!\d)', job):
                if num in url_map:
                    btn_html = f" <div style='margin-top:10px; border-top:1px solid #eee; padding-top:8px;'><button onclick=\"openModal('{url_map[num]}')\" class='gorsel-buton'>🔍 GÖRSELİ İNCELE</button></div>"
                    break
            html += f"<div class='mobile-card'><div class='mc-sira'>Sıra {i}</div><div class='mc-body'>{job}{btn_html}</div></div>"
            
    html += "</div><script>function openModal(url) { document.getElementById('modalIframe').src = url; document.getElementById('imgModal').style.display = 'flex'; } function closeModal() { document.getElementById('imgModal').style.display = 'none'; document.getElementById('modalIframe').src = ''; }</script></body></html>"
    return html

def ozel_tablo_html_olustur_acil(df, url_map):
    renk_tema = "#cc0000"
    kenar_renk = "#a93226"
    html = f"""
    <!DOCTYPE html> <html> <head> <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style> body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #ffffff; }} .tablo-sarmalayici {{ overflow-x: auto; width: 100%; padding-bottom: 20px; }} .ozel-tablo {{ width: 100%; border-collapse: collapse; min-width: 800px; }} .ozel-tablo th {{ background-color: {renk_tema}; color: #ffffff; text-align: left; padding: 12px; font-size: 14px; border: 1px solid {kenar_renk}; position: sticky; top: 0; z-index: 10; }} .ozel-tablo td {{ padding: 12px; border: 1px solid #e0e0e0; font-size: 13px; color: #000000; word-wrap: break-word; vertical-align: middle; }} .ozel-tablo tr:nth-child(even) td {{ background-color: #f9f9f9; }} .ozel-tablo tr:hover td {{ background-color: #fceceb; }} .sira-sutunu {{ width: 40px; text-align: center; font-weight: bold; }} .gorsel-buton {{ float: right; cursor: pointer; text-decoration: none; font-size: 12px; padding: 6px 12px; background: linear-gradient(135deg, #e74c3c, #c0392b); color: white !important; border-radius: 20px; border: none; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: all 0.3s ease; animation: pulse 2s infinite; display: inline-flex; align-items: center; gap: 5px; }} .gorsel-buton:hover {{ transform: scale(1.1); box-shadow: 0 6px 12px rgba(0,0,0,0.3); background: linear-gradient(135deg, #c0392b, #a93226); }} @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }} }} @media screen and (max-width: 768px) {{ .ozel-tablo {{ min-width: 100%; border: none; }} .ozel-tablo thead {{ display: none; }} .ozel-tablo tr {{ display: block; margin-bottom: 20px; border: 1px solid #e0e0e0; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); background-color: #ffffff; overflow: hidden; }} .ozel-tablo tr:nth-child(even) td {{ background-color: #ffffff; }} .ozel-tablo td {{ display: block; padding: 10px 15px; border: none; border-bottom: 1px solid #f0f0f0; font-size: 14px; position: relative; text-align: right; padding-left: 45%; }} .ozel-tablo td:last-child {{ border-bottom: none; }} .ozel-tablo td::before {{ content: attr(data-label); position: absolute; left: 15px; width: 40%; text-align: left; font-weight: bold; color: {renk_tema}; font-size: 13px; }} .sira-sutunu {{ width: auto; text-align: right; background-color: {renk_tema} !important; color: #fff !important; font-size: 16px; padding: 12px 15px !important; }} .sira-sutunu::before {{ color: #ffffff !important; opacity: 0.9; }} .gorsel-buton {{ float: none; width: 100%; display: flex; justify-content: center; padding: 12px; font-size: 14px; margin-top: 10px; border-radius: 6px; }} }} .modal-overlay {{ display: none; position: fixed; z-index: 999999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.85); backdrop-filter: blur(5px); align-items: center; justify-content: center; cursor: pointer; }} .modal-content {{ position: relative; width: 95%; height: 90%; max-width: 1200px; background: #fff; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); padding: 10px; cursor: default; animation: zoomIn 0.3s ease; }} @keyframes zoomIn {{ from {{ transform: scale(0.9); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }} .close-btn {{ position: absolute; top: -10px; right: -10px; background: #e74c3c; color: white; border-radius: 50%; width: 36px; height: 36px; text-align: center; line-height: 34px; cursor: pointer; font-weight: bold; font-size: 24px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); border: 2px solid white; transition: 0.2s; z-index: 1000000; }} .close-btn:hover {{ background: #c0392b; transform: scale(1.1); }} </style> </head> <body>
    <div id="imgModal" class="modal-overlay" onclick="closeModal()">
        <div class="modal-content" onclick="event.stopPropagation();"><span class="close-btn" onclick="closeModal()">&times;</span><iframe id="modalIframe" src="" style="width:100%; height:100%; border:none; border-radius:4px;"></iframe></div>
    </div>
    <div class='tablo-sarmalayici'><table class='ozel-tablo'><thead><tr>
    """
    for col in df.columns:
        display_name = re.sub(r'_\d+$', '', col)
        if 'SIRA' in display_name.upper(): html += "<th class='sira-sutunu'>Sıra</th>"
        else: html += f"<th>{display_name}</th>"
    html += "</tr></thead><tbody>"
    for _, row in df.iterrows():
        html += "<tr>"
        for col in df.columns:
            val = str(row[col]).strip()
            display_name = re.sub(r'_\d+$', '', col)
            if 'SIRA' in col.upper(): html += f"<td class='sira-sutunu' data-label='Sıra No'>{val}</td>"
            else:
                btn_html = ""
                for num in re.findall(r'(?<!\d)(\d{5,6})(?!\d)', val):
                    if num in url_map:
                        btn_html = f" <div style='margin-top:8px;'><button onclick=\"openModal('{url_map[num]}')\" class='gorsel-buton'>🔍 İNCELE</button></div>"
                        break
                html += f"<td data-label='{display_name}'>{val}{btn_html}</td>"
        html += "</tr>"
    html += "</tbody></table></div><script>function openModal(url) { document.getElementById('modalIframe').src = url; document.getElementById('imgModal').style.display = 'flex'; } function closeModal() { document.getElementById('imgModal').style.display = 'none'; document.getElementById('modalIframe').src = ''; }</script></body></html>"
    return html

# ----------------- URL AYARLARI -----------------
gunluk_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=374780490&single=true&output=csv"
acil_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=1428130476&single=true&output=csv"

# ⚠️ DİKKAT: BURAYA KOPYALADIĞINIZ YENİ GID NUMARASINI YAZIN! ⚠️
dunku_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSFjG4nZyzHg_OmUc4IgiZpKpxLyC2lO-0-TuvCq1PGOboEDD3N5Au6qcz0WJRFB7tZwTSrEQlfStv_/pub?gid=1976168354&single=true&output=csv"

t_gunluk, t_dunku, t_acil = st.tabs(["📋 Günlük Üretim", "⏪ Dünkü Liste", "🚨 Acil Üretim"])

with t_gunluk:
    df_g, url_g, err_g = veri_getir_ve_isle(gunluk_url)
    if not df_g.empty: components.html(ozel_tablo_html_olustur_gunluk(df_g, url_g), height=850, scrolling=True)
    else: st.error(err_g) if err_g else st.warning("Günlük liste boş.")

with t_dunku:
    st.markdown("<h3 style='color: #27ae60; text-align: center;'>⏪ DÜNKÜ ÜRETİM LİSTESİ</h3>", unsafe_allow_html=True)
    df_d, url_d, err_d = veri_getir_ve_isle(dunku_url)
    if not df_d.empty: components.html(ozel_tablo_html_olustur_gunluk(df_d, url_d), height=850, scrolling=True)
    else: st.error(err_d) if err_d else st.warning("Dünkü liste boş veya henüz oluşturulmadı.")

with t_acil:
    st.markdown("<h3 style='color: #ff0000; text-align: center;'>🚨 ACİL ÜRETİM LİSTESİ</h3>", unsafe_allow_html=True)
    df_a, url_a, err_a = veri_getir_ve_isle(acil_url)
    if not df_a.empty: components.html(ozel_tablo_html_olustur_acil(df_a, url_a), height=850, scrolling=True)
    else: st.error(err_a) if err_a else st.success("🎉 Harika! Şu an için bekleyen hiçbir acil iş görünmüyor.")

st.markdown("<br><p style='text-align: center; color: #a9a9a9; font-size: 12px;'><b>Mehmet YANGÖZ</b> - İzmir Bölge Performans Merkezi © 2026</p>", unsafe_allow_html=True)
