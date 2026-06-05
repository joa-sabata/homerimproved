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

# ================= SECCIÓN DE ENCABEZADO =================
st.title("Homero 🍩")
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

# LÓGICA DEL BOTÓN BORRAR TOTAL
if btn_borrar:
    st.session_state.contador_reset += 1
    st.session_state.texto_salida = ""
    st.rerun()

# ================= LÓGICA DE PROCESAMIENTO REESTRUCTURADA =================
if btn_procesar:
    if entrada.strip():
        lineas = [l.strip() for l in entrada.split('\n') if l.strip()]
        resultados_principal, resultados_jap, resultados_error = [], [], []
        
        patron_url = r'(https?://[^\s]+(?:youtu\.be|youtube\.com|tiktok\.com|instagram\.com|facebook\.com|fb\.watch|fb\.com|x\.com|twitter\.com|snapchat\.com)[^\s]*)'
        
        for i, linea in enumerate(lineas):
            url_match = re.search(patron_url, linea, re.IGNORECASE)
            
            if url_match:
                url = url_match.group(1)
                url_low = url.lower()
                
                # Contexto general del bloque de la orden
                inicio_contexto = max(0, i - 4)
                fin_contexto = min(len(lineas), i + 5)
                contexto_texto = " ".join(lineas[inicio_contexto:fin_contexto])
                contexto_texto_low = contexto_texto.lower()
                
                # === DETECTAR CAMPANITA DE ALERTA 🔔 ===
                if "🔔" in contexto_texto or "bell" in contexto_texto_low:
                    resultados_error.append(f"🔔 ORDEN CON ALERTA (Revisar en Gestor) -> {url}")
                    continue
                    
                # === DETECTAR DISPONIBLE NEGATIVO ❌ ===
                if re.search(r'-\s*\$|\$\s*-', contexto_texto):
                    resultados_error.append(f"❌ SALDO NEGATIVO (Revisar Disponible) -> {url}")
                    continue
                
                # Texto anterior a la URL (para detectar producto/servicio)
                idx_http = linea.lower().find("http")
                texto_anterior = linea.lower()[:idx_http].strip()
                if not texto_anterior:
                    texto_anterior = " ".join(lineas[inicio_contexto:i]).lower()
                
                # --- 1. EXTRACCIÓN EXTRA-ESTRICTA DEL CÓDIGO MANUAL ---
                codigo_manual = ""
                # Buscamos números de 2 a 6 dígitos en la parte del producto/servicio
                numeros_en_producto = re.findall(r'\b\d{2,6}\b', texto_anterior)
                if numeros_en_producto:
                    for num in reversed(numeros_en_producto):
                        # Ignoramos IDs de venta de 5 dígitos que empiezan con 3 e IDs de orden que empiezan con 249
                        if not (len(num) == 5 and num.startswith('3')) and not num.startswith('249'):
                            codigo_manual = num
                            break

                # --- 2. EXTRACCIÓN DE CANTIDAD AILANDO EL CÓDIGO MANUAL ---
                # Creamos un texto posterior de búsqueda y removemos la URL
                texto_posterior = " ".join(lineas[i:fin_contexto])
                texto_posterior = texto_posterior.replace(url, "")
                
                # ¡Clave! Si detectamos un código manual, también lo borramos del análisis de cantidad
                # para que no se confunda si están en la misma línea o bloque
                texto_analisis_cantidad = contexto_texto.replace(url, "")
                if codigo_manual:
                    # Lo removemos con un límite de palabra para no romper otros números parciales
                    texto_analisis_cantidad = re.sub(r'\b' + re.escape(codigo_manual) + r'\b', '', texto_analisis_cantidad)
                    texto_posterior = re.sub(r'\b' + re.escape(codigo_manual) + r'\b', '', texto_posterior)

                # Buscamos la cantidad primero en la parte posterior (lo más natural)
                numeros_candidatos = re.findall(r'\b\d+(?!\.\d)\b', texto_posterior)
                cantidad = ""
                for num in numeros_candidatos:
                    if num and not (len(num) == 5 and num.startswith('3')) and not num.startswith('249'):
                        cantidad = num
                        break
                
                # Si no se halló atrás, buscamos en todo el bloque limpio restante
                if not cantidad:
                    todos_los_numeros = re.findall(r'\b\d+(?!\.\d)\b', texto_analisis_cantidad)
                    for num in todos_los_numeros:
                        if num and not (len(num) == 5 and num.startswith('3')) and not num.startswith('249'):
                            cantidad = num
                            break

                if not cantidad:
                    resultados_error.append(f"Falta cantidad para el link -> {url}")
                    continue

                # --- IDENTIFICAR RED SOCIAL ---
                red_social = "instagram"
                if "tiktok.com" in url_low: red_social = "tiktok"
                elif any(x in url_low for x in ["facebook.com", "fb.watch", "fb.com"]): red_social = "facebook"
                elif any(x in url_low for x in ["youtube.com", "youtu.be"]): red_social = "youtube"
                elif any(x in url_low for x in ["twitter.com", "x.com"]): red_social = "twitter"
                elif "snapchat.com" in url_low: red_social = "snapchat"

                # --- PALABRAS CLAVE ---
                es_views = any(x in texto_anterior for x in ["view", "vistas", "reproducciones", "views_yt"])
                es_likes = any(x in texto_anterior for x in ["like", "me gusta"])
                es_followers = any(x in texto_anterior for x in ["follower", "seguidor", "seguidores"])
                es_post = "post" in texto_anterior
                re_shares = any(x in texto_anterior for x in ["share", "compartir", "shares", "compartidos"])
                es_repost = "repost" in texto_anterior
                es_jap_keyword = "jap" in texto_anterior

                codigo = ""
                panel_destino = ""

                # ================= MOTOR DE CLASIFICACIÓN HARDCODEADO =================
                if red_social == "snapchat":
                    panel_destino = "jap"
                    codigo = codigo_manual if codigo_manual else "4165"
                
                elif red_social == "twitter":
                    panel_destino = "jap"
                    if es_likes: codigo = "8243"
                    elif es_views: codigo = "2100"
                    elif es_followers: codigo = "7666"
                    elif "retweet" in texto_anterior: codigo = "7155"
                    elif "guardado" in texto_anterior or "save" in texto_anterior: codigo = "1017"
                    else: codigo = codigo_manual if codigo_manual else ""

                elif red_social == "youtube":
                    panel_destino = "principal"
                    if es_likes: codigo = "2606"
                    elif es_views: codigo = "2603"

                elif red_social == "tiktok":
                    if es_followers:
                        panel_destino = "jap"; codigo = "912"
                    elif es_views:
                        panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "10020"
                    elif es_likes:
                        if es_jap_keyword or codigo_manual:
                            panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "7991"
                        else:
                            panel_destino = "principal"; codigo = "1023"

                elif red_social == "facebook":
                    if "page" in texto_anterior or "pagina" in texto_anterior:
                        panel_destino = "jap"; codigo = "7663"
                    elif es_views:
                        panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "20"
                    elif es_post:
                        panel_destino = "principal"; codigo = "1248"
                    elif es_likes:
                        if es_jap_keyword or codigo_manual:
                            panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "4350"
                        else:
                            panel_destino = "principal"; codigo = "1248"
                    else:
                        panel_destino = "jap"; codigo = "20"

                elif red_social == "instagram":
                    if "empresa" in texto_anterior and "2788" in texto_anterior:
                        panel_destino = "principal"; codigo = "2788"
                    elif "empresa" in texto_anterior:
                        panel_destino = "principal"; codigo = "2754"
                    elif "cch" in texto_anterior:
                        panel_destino = "principal"; codigo = "2744"
                    elif "ccm" in texto_anterior:
                        panel_destino = "principal"; codigo = "2745"
                    elif "story" in texto_anterior or "historia" in texto_anterior:
                        panel_destino = "principal"; codigo = "700"
                    elif "reach" in texto_anterior or "alcance" in texto_anterior:
                        panel_destino = "principal"; codigo = "1755"
                    elif "save" in texto_anterior or "guardado" in texto_anterior:
                        panel_destino = "principal"; codigo = "705"
                    elif es_repost:
                        panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "2257"
                    elif re_shares:
                        if es_jap_keyword or codigo_manual:
                            panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "9590"
                        else:
                            panel_destino = "principal"; codigo = "1044"
                    elif es_views:
                        if es_jap_keyword or codigo_manual:
                            panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "6454"
                        else:
                            panel_destino = "principal"; codigo = "1266"
                    elif es_followers:
                        if es_jap_keyword or codigo_manual:
                            panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "2763"
                        else:
                            panel_destino = "principal"; codigo = "2763"
                    elif es_likes:
                        if es_jap_keyword or codigo_manual:
                            panel_destino = "jap"; codigo = codigo_manual if codigo_manual else "1736"
                        else:
                            panel_destino = "principal"; codigo = "2450"

                # Forzado manual a panel JAP
                if codigo_manual and not (red_social == "instagram" and panel_destino == "principal" and codigo_manual in ["2744","2745","2754","2788"]):
                    codigo = codigo_manual
                    panel_destino = "jap"

                # Agrupación final en listas
                if codigo and panel_destino == "principal":
                    resultados_principal.append(f"{codigo}|{url}|{cantidad}")
                elif codigo and panel_destino == "jap":
                    resultados_jap.append(f"{codigo}|{url}|{cantidad}")
                else:
                    resultados_error.append(f"No se pudo clasificar: {url}")
        
        # Formatear la salida final en pantalla
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
            texto_final.append("⚠️ DETALLES / ELEMENTOS NO PROCESADOS:")
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
