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
        # Separamos el texto crudo en líneas limpias
        lineas = [l.strip() for l in entrada.split('\n') if l.strip()]
        resultados_principal, resultados_jap, resultados_error = [], [], []
        
        # Patrón estricto para cazar las URLs válidas
        patron_url = r'(https?://[^\s]+(?:youtu\.be|youtube\.com|tiktok\.com|instagram\.com|facebook\.com|fb\.watch|fb\.com|x\.com|twitter\.com|snapchat\.com)[^\s]*)'
        
        # Procesamos línea por línea buscando URLs (Elimina de raíz los encabezados o basura suelta)
        for i, linea in enumerate(lineas):
            url_match = re.search(patron_url, linea, re.IGNORECASE)
            
            if url_match:
                url = url_match.group(1)
                url_low = url.lower()
                
                # Contexto dinámico de la orden: analizamos entorno para evitar falsos positivos
                inicio_contexto = max(0, i - 4)
                fin_contexto = min(len(lineas), i + 5)
                contexto_lineas = lineas[inicio_contexto:fin_contexto]
                contexto_texto = " ".join(contexto_lineas)
                contexto_texto_low = contexto_texto.lower()
                
                # === DETECTAR CAMPANITA DE ALERTA 🔔 ===
                if "🔔" in contexto_texto or "bell" in contexto_texto_low:
                    resultados_error.append(f"🔔 ORDEN CON ALERTA (Revisar en Gestor) -> {url}")
                    continue
                    
                # === DETECTAR DISPONIBLE NEGATIVO ❌ ===
                if re.search(r'-\s*\$|\$\s*-', contexto_texto):
                    resultados_error.append(f"❌ SALDO NEGATIVO (Revisar Disponible) -> {url}")
                    continue
                
                # Extraer el TEXTO del servicio (mirando la misma línea a la izquierda de la URL)
                idx_http = linea.lower().find("http")
                texto_anterior = linea.lower()[:idx_http].strip()
                if not texto_anterior:
                    # Rescate de contexto si la URL quedó sola en su renglón
                    texto_anterior = " ".join(lineas[inicio_contexto:i]).lower()
                
                # Extraer la CANTIDAD analizando la parte posterior
                texto_posterior = " ".join(lineas[i:fin_contexto])
                texto_posterior = texto_posterior.replace(url, "")
                
                numeros_candidatos = re.findall(r'\b\d+(?!\.\d)\b', texto_posterior)
                
                cantidad = ""
                for num in numeros_candidatos:
                    # Ignoramos IDs de venta (5 dígitos que inician con 3) e IDs de orden (249XXXX)
                    if num and not (len(num) == 5 and num.startswith('3')) and not num.startswith('249'):
                        cantidad = num
                        break
                
                # Rescate total de cantidad en todo el bloque si faltaba
                if not cantidad:
                    todos_los_numeros = re.findall(r'\b\d+(?!\.\d)\b', contexto_texto)
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

                # Extraer códigos manuales (ej: "9590")
                codigo_manual = ""
                numeros_en_producto = re.findall(r'\b\d{2,6}\b', texto_anterior)
                if numeros_en_producto:
                    for num in reversed(numeros_en_producto):
                        if not (len(num) == 5 and num.startswith('3')) and not num.startswith('249'):
                            codigo_manual = num
                            break

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
                        panel_destino = "jap"; codigo = codigo_manual if codigo_
