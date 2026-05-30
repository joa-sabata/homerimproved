import streamlit as st
import re

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(
    page_title="Homero Mejorado - Procesador Multi-Panel",
    page_icon="🔮",
    layout="centered"
)

# Estilo personalizado Modo Oscuro
st.markdown("""
    <style>
    .stTextArea textarea { background-color: #282c34 !important; color: #61afef !important; font-family: 'Segoe UI', monospace; }
    .stCodeBlock code { color: #2bb063 !important; }
    div.stButton > button:first-child { background-color: #239a54; color: white; font-weight: bold; width: 100%; border-radius: 5px; padding: 0.6rem; }
    div.stButton > button:first-child:hover { background-color: #2bb063; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🔮 Homero Mejorado")
st.write("Pegá tus órdenes acá abajo para separarlas por panel automáticamente.")

# ================= SECCIÓN ENTRADA =================
entrada = st.text_area("Pega aquí tus órdenes mezcladas:", height=250, placeholder="Escribe o pega las líneas aquí...")

# ================= BOTÓN PROCESAR =================
if st.button("PROCESAR TODO"):
    if entrada.strip():
        lineas = entrada.strip().split('\n')
        resultados_principal, resultados_jap, resultados_error = [], [], []
       
        for linea in lineas:
            if not linea.strip(): continue
            linea_low = linea.lower()
            partes = linea.split()
            if len(partes) < 2: continue
            
            url, cantidad = "", ""
            # 1. Extraer URL y Cantidad
            for parte in partes:
                parte_low = parte.lower()
                if any(x in parte_low for x in ["http", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "fb.watch", "fb.com"]):
                    url = parte
                elif re.match(r'^\d+[\d.,]*$', parte):
                    cantidad = parte
            
            if not url or not cantidad: continue
            url_low = url.lower()
            
            # 2. Identificar Red Social por el LINK
            es_link_fb = "facebook.com" in url_low or "fb.watch" in url_low or "fb.com" in url_low
            es_link_tt = "tiktok.com" in url_low
            es_link_yt = "youtube.com" in url_low or "youtu.be" in url_low
            
            # 3. Buscar código manual (Limpiando la URL)
            linea_limpia = linea.replace(url, "")
            codigo_manual = ""
            numeros_en_linea = re.findall(r'\b\d{2,}\b', linea_limpia)
            for num in numeros_en_linea:
                if num != cantidad:
                    codigo_manual = num
                    break
            
            # Auxiliares de palabras clave
            es_views = any(x in linea_low for x in ["view", "vistas", "reproducciones", "views_yt"])
            es_likes = any(x in linea_low for x in ["like", "me gusta"])
            es_followers = any(x in linea_low for x in ["follower", "seguidor", "seguidores"])
            es_post = "post" in linea_low
            
            # ================= DETERMINAR EL PANEL CORRECTO =================
            
            # REGLA EXCEPCIÓN: Si es un post de FB (ej: "like post"), prioridad absoluta al código 1248
            if es_link_fb and es_post:
                resultados_principal.append(f"1248|{url}|{cantidad}")
                
            # Si es de FB pero pide solo likes tradicionales (sin la palabra post), va con el 2450
            elif es_link_fb and es_likes:
                resultados_principal.append(f"2450|{url}|{cantidad}")
                
            # LÓGICA PANEL JAP
            elif "jap" in linea_low or "repost" in linea_low or es_link_fb or (es_link_tt and es_followers):
                if codigo_manual:
                    resultados_jap.append(f"{codigo_manual}|{url}|{cantidad}")
                elif "repost" in linea_low:
                    resultados_jap.append(f"2257|{url}|{cantidad}")
                elif es_link_fb:
                    resultados_jap.append(f"20|{url}|{cantidad}")  # Views FB JAP
                elif es_link_tt and es_followers:
                    resultados_jap.append(f"912|{url}|{cantidad}") # TikTok Followers JAP
                else:
                    resultados_error.append(f"Falta código JAP -> {linea.strip()}")
            
            # LÓGICA PANEL PRINCIPAL NORMAL
            else:
                codigo = ""
                if "empresa" in linea_low and "2788" in linea_low: codigo = "2788"
                elif "empresa" in linea_low: codigo = "2754"
                elif "cch" in linea_low: codigo = "2744"
                elif "ccm" in linea_low: codigo = "2745"
                elif "story" in linea_low or "historia" in linea_low: codigo = "700"
                elif es_link_yt and es_views: codigo = "2603"
                elif es_link_yt and es_likes: codigo = "2606"
                elif es_link_tt and es_likes: codigo = "1023"
                elif es_post: codigo = "1248"
                elif es_followers: codigo = "2763"
                elif es_views: codigo = "1266"
                elif es_likes: codigo = "2450"
                elif "save" in linea_low or "guardado" in linea_low: codigo = "705"
                elif "share" in linea_low or "compartir" in linea_low: codigo = "1044"
                elif "reach" in linea_low or "alcance" in linea_low: codigo = "1755"
                
                if codigo: resultados_principal.append(f"{codigo}|{url}|{cantidad}")
                else: resultados_error.append(f"Código desconocido -> {linea.strip()}")
       
        # ================= SECCIÓN SALIDA =================
        st.subheader("Resultados separados por Panel:")
        texto_final = []
        if resultados_principal:
            texto_final.append("=== PANEL PRINCIPAL ===")
            texto_final.extend(resultados_principal)
        if resultados_jap:
            if resultados_principal: texto_final.append("")
            texto_final.append("=== PANEL JAP ===")
            texto_final.extend(resultados_jap)
        if resultados_error:
            if resultados_principal or resultados_jap: texto_final.append("")
            texto_final.append("⚠️ ÓRDENES CON ERROR (REVISAR):")
            texto_final.extend(resultados_error)
            
        st.text_area("Resultados listos (Verde):", value="\n".join(texto_final), height=300)
    else:
        st.warning("Por favor, ingresa al menos una orden para procesar.")
