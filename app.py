import streamlit as st
import re

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(
    page_title="Homero - Procesador Multi-Panel",
    page_icon="🍩",
    layout="centered"
)

# Estilo personalizado Modo Oscuro y colores fijos de botones
st.markdown("""
    <style>
    /* Cajas de texto generales */
    .stTextArea textarea { 
        background-color: #282c34 !important; 
        color: #61afef !important; 
        font-family: 'Segoe UI', monospace; 
    }
    
    /* Forzar que la caja de salida sea SIEMPRE verde */
    div[data-testid="stTextAreaRootElement"] + div textarea, 
    .stTextArea [data-testid="stWidgetLabel"] + div textarea {
        color: #2bb063 !important;
        font-weight: bold;
    }
    
    .stCodeBlock code { color: #2bb063 !important; }
    
    /* Botón Procesar Todo */
    div.col-verde button {
        background-color: #239a54 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 5px !important;
    }
    div.col-verde button:hover {
        background-color: #2bb063 !important;
        color: white !important;
    }

    /* Botón Borrar Todo (Rojo) */
    div.col-rojo button {
        background-color: #e06c75 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 5px !important;
    }
    div.col-rojo button:hover {
        background-color: #ef596f !important;
    }
    </style>
""", unsafe_allow_html=True)

# ================= SECCIÓN DE ENCABEZADO LIMPIO =================
st.title("Homero 2 🍩")
st.write("El procesador automático que hace el trabajo pesado por vos.")
st.write("---")
st.write("Pegá tus órdenes acá abajo para separarlas por panel automáticamente.")

# Inicializamos las variables de estado correctamente
if "contador_reset" not in st.session_state:
    st.session_state.contador_reset = 0
if "texto_salida" not in st.session_state:
    st.session_state.texto_salida = ""

# ================= SECCIÓN ENTRADA =================
entrada = st.text_area(
    "Pega aquí tus órdenes :", 
    height=250, 
    placeholder="Escribe o pega las líneas aquí...",
    key=f"entrada_dinamica_{st.session_state.contador_reset}"
)

# Columnas de botones
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="col-verde">', unsafe_allow_html=True)
    btn_procesar = st.button("✨ PROCESAR TODO", use_container_width=True, key="btn_proc")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="col-rojo">', unsafe_allow_html=True)
    btn_borrar = st.button("❌ BORRAR TODO", use_container_width=True, key="btn_borr")
    st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DEL BOTÓN BORRAR TOTAL (CORREGIDO PARA LIMPIAR LA MEMORIA INTERNA)
if btn_borrar:
    st.session_state.contador_reset += 1
    st.session_state.texto_salida = ""  # <- CORRECCIÓN: Borra los resultados guardados anteriores
    st.rerun()

# ================= LÓGICA DE PROCESAMIENTO =================
if btn_procesar:
    if entrada.strip():
        lineas = entrada.strip().split('\n')
        resultados_principal, resultados_jap, resultados_error = [], [], []
        
        for linea in lineas:
            if not linea.strip(): continue
            linea_low = linea.lower()
            
            # 1. Identificar la Red Social por el Link
            red_social = "instagram"
            if "tiktok.com" in linea_low: red_social = "tiktok"
            elif any(x in linea_low for x in ["facebook.com", "fb.watch", "fb.com"]): red_social = "facebook"
            elif any(x in linea_low for x in ["youtube.com", "youtu.be"]): red_social = "youtube"
            elif any(x in linea_low for x in ["twitter.com", "x.com"]): red_social = "twitter"
            elif "snapchat.com" in linea_low: red_social = "snapchat"

            partes = linea.split()
            if len(partes) < 2: continue
            
            url, cantidad = "", ""
            partes_texto_puro = []

            # Separar la URL, la cantidad y el resto del texto de forma estricta
            for parte in partes:
                parte_low = parte.lower()
                if any(x in parte_low for x in ["http", "youtu.be", "tiktok.com", "instagram.com", "facebook.com", "fb.watch", "fb.com", "x.com", "twitter.com", "snapchat.com"]):
                    url = parte
                elif re.match(r'^\d+[\d.,]*$', parte):
                    cantidad = parte
                    partes_texto_puro.append(parte) # Mantener números para analizar posibles códigos manuales
                else:
                    partes_texto_puro.append(parte)
            
            if not url or not cantidad: continue
            
            # CREACIÓN DEL TEXTO LIMPIO: Excluyendo la URL por completo pieza por pieza
            texto_limpio_linea = " ".join(partes_texto_puro)
            texto_limpio_linea_low = texto_limpio_linea.lower()

            # Extraer código manual numérico presente únicamente en las partes de texto (descartando la cantidad)
            todos_los_numeros = re.findall(r'\b\d{2,6}\b', texto_limpio_linea)
            codigo_manual = ""
            for num in todos_los_numeros:
                if num != cantidad:
                    codigo_manual = num
                    break

            # Auxiliares de búsqueda de palabras clave basados en el texto que NO tiene la URL
            es_views = any(x in texto_limpio_linea_low for x in ["view", "vistas", "reproducciones", "views_yt"])
            es_likes = any(x in texto_limpio_linea_low for x in ["like", "me gusta"])
            es_followers = any(x in texto_limpio_linea_low for x in ["follower", "seguidor", "seguidores"])
            es_post = any(x in texto_limpio_linea_low for x in ["post", "publicacion"])
            es_shares = any(x in texto_limpio_linea_low for x in ["share", "compartir", "shares", "compartidos"])
            es_repost = "repost" in texto_limpio_linea_low
            es_jap_keyword = "jap" in texto_limpio_linea_low

            codigo = ""
            panel_destino = ""

            # ================= MOTOR DE CLASIFICACIÓN DURA =================
            
            # --- SNAPCHAT ---
            if red_social == "snapchat":
                panel_destino = "jap"
                codigo = codigo_manual if codigo_manual else "4165"
            
            # --- TWITTER ---
            elif red_social == "twitter":
                panel_destino = "jap"
                if es_likes: codigo = "8243"
                elif es_views: codigo = "2100"
                elif es_followers: codigo = "7666"
                elif "retweet" in texto_limpio_linea_low: codigo = "7155"
                elif "guardado" in texto_limpio_linea_low or "save" in texto_limpio_linea_low: codigo = "1017"
                else: codigo = codigo_manual if codigo_manual else ""

            # --- YOUTUBE ---
            elif red_social == "youtube":
                panel_destino = "principal"
                if es_likes: codigo = "2606"
                elif es_views: codigo = "2603"

            # --- TIKTOK ---
            elif red_social == "tiktok":
                if es_followers:
                    panel_destino = "jap"
                    codigo = "912"
                elif es_views:
                    panel_destino = "jap"
                    codigo = codigo_manual if codigo_manual else "10020"
                elif es_likes:
                    if es_jap_keyword or codigo_manual:
                        panel_destino = "jap"
                        codigo = codigo_manual if codigo_manual else "7991"
                    else:
                        panel_destino = "principal"
                        codigo = "1023"

            # --- FACEBOOK ---
            elif red_social == "facebook":
                if "page" in texto_limpio_linea_low or "pagina" in texto_limpio_linea_low:
                    panel_destino = "jap"
                    codigo = "7663"
                elif es_views:
                    panel_destino = "jap"
                    codigo = codigo_manual if codigo_manual else "20"
                elif es_post:
                    panel_destino = "principal"
                    codigo = "1248"
                elif es_likes:
                    if es_jap_keyword or codigo_manual:
                        panel_destino = "jap"
                        codigo = codigo_manual if codigo_manual else "4350"
                    else:
                        panel_destino = "principal"
                        codigo = "1248"
                else:
                    panel_destino = "jap"
                    codigo = "20"

            # --- INSTAGRAM (Y generales) ---
            elif red_social == "instagram":
                # Filtros prioritarios fijos de Panel Principal
                if "empresa" in texto_limpio_linea_low and "2788" in texto_limpio_linea_low:
                    panel_destino = "principal"; codigo = "2788"
                elif "empresa" in texto_limpio_linea_low:
                    panel_destino = "principal"; codigo = "2754"
                elif "cch" in texto_limpio_linea_low:
                    panel_destino = "principal"; codigo = "2744"
                elif "ccm" in texto_limpio_linea_low:
                    panel_destino = "principal"; codigo = "2745"
                elif "story" in texto_limpio_linea_low or "historia" in texto_limpio_linea_low:
                    panel_destino = "principal"; codigo = "700"
                elif "reach" in texto_limpio_linea_low or "alcance" in texto_limpio_linea_low:
                    panel_destino = "principal"; codigo = "1755"
                elif "save" in texto_limpio_linea_low or "guardado" in texto_limpio_linea_low:
                    panel_destino = "principal"; codigo = "705"
                
                # Casos mixtos (Principal o JAP según texto explícito desvinculado de la URL)
                elif es_repost:
                    panel_destino = "jap"
                    codigo = codigo_manual if codigo_manual else "2257"
                elif es_shares:
                    if es_jap_keyword or codigo_manual:
                        panel_destino = "jap"
                        codigo = codigo_manual if codigo_manual else "9590"
                    else:
                        panel_destino = "principal"; codigo = "1044"
                elif es_views:
                    if es_jap_keyword or codigo_manual:
                        panel_destino = "jap"
                        codigo = codigo_manual if codigo_manual else "6454"
                    else:
                        panel_destino = "principal"; codigo = "1266"
                elif es_followers:
                    if es_jap_keyword or codigo_manual:
                        panel_destino = "jap"
                        codigo = codigo_manual if codigo_manual else "2763"
                    else:
                        panel_destino = "principal"; codigo = "2763"
                elif es_likes:
                    if es_jap_keyword or codigo_manual:
                        panel_destino = "jap"
                        codigo = codigo_manual if codigo_manual else "1736"
                    else:
                        panel_destino = "principal"; codigo = "2450"

            # Si el cliente especificó un código manual de forma directa, reescribimos el código detectado
            if codigo_manual and not (red_social == "instagram" and panel_destino == "principal" and codigo_manual in ["2744","2745","2754","2788"]):
                codigo = codigo_manual
                if not panel_destino:
                    panel_destino = "jap"

            # 3. Guardar en los contenedores correspondientes
            if codigo and panel_destino == "principal":
                resultados_principal.append(f"{codigo}|{url}|{cantidad}")
            elif codigo and panel_destino == "jap":
                resultados_jap.append(f"{codigo}|{url}|{cantidad}")
            else:
                resultados_error.append(f"Código desconocido o incompleto -> {linea.strip()}")
        
        # Formatear el texto final
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
            
        st.session_state.texto_salida = "\n".join(texto_final)
        st.rerun()
    else:
        st.warning("Por favor, ingresa al menos una orden para procesar.")

# ================= SECCIÓN SALIDA =================
if st.session_state.texto_salida:
    st.subheader("Resultados separados por Panel:")
    st.text_area(
        "Resultados listos :", 
        value=st.session_state.texto_salida, 
        height=300, 
        key="caja_de_salida"
    )
