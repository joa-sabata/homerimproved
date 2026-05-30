import streamlit as st
import re

# --- CONFIGURACIÓN DE LA PÁGINA WEB ---
st.set_page_config(
    page_title="Homero - Procesador Multi-Panel",
    page_icon="⚙️",
    layout="centered"
)

# Estilo personalizado Modo Oscuro y letras de salida verdes obligatorias
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
    
    /* Estilo Botón Procesar (Verde) */
    div.stButton > button.boton-procesar {
        background-color: #239a54 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        padding: 0.6rem !important;
    }
    
    /* Estilo Botón Borrar */
    div.stButton > button {
        border-radius: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ================= SECCIÓN DE LOGO OFICIAL (BASE64) =================
# Convertimos la imagen de "images.png" a texto base64 para que no dependa de links externos
logo_base64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKAAAADgCAMAAACe6K9vAAAAeFBMVEX"
    "///8AAADFxcWcnJz4+Pj19fXo6Ojp6en7+/vJycnz8/PV1dXg4ODd3d3s7OzPz8/b29v6+vrk5OT"
    "m5ubv7+/w8PDX19fS0tLe3t7j4+P29vb09PTNzc3Y2Njl5eXp6enr6+vp6enl5eXm5ubp6ens7Ox"
    "4Z3ZNAAAEbElEQVR4nO3b23KyOhQGYM6BwOIoIogKiooidfX93/CwreI4VbMDSYp61796t7MvM0"
    "mSnywZAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOD/W6zXN8Plv8bquZre"
    "uRPhO6fD/MaddN+pTvsbd9p9r87N77PZpI7vI/v+1X86G9wA/+RstI9fH786A76X6m7GvOunZ8G"
    "3UtXdfYyubp++7rV79V2fVfcw4v749bWv++oee9V9zVf39BvUff16P0Z3+g2uupfRvf7R9X6D3X"
    "N1/xrR9Wv3eorwOnOqX7vHdfdU169p6+Vb9Z7vHqu6+vU89VbdRvf8wS1Wp/v4zTidX9vXqO5+X"
    "vX9D6/VzZzup7oP//B6qO5Pru4Oq7qfFf9F9b8y92fXPf26WJv6e676Ff/0Yq++xH1b3Xf78/fX"
    "v3/4vVdvdjGqVfX69Xdfv+qPXtUffVrd/p5r/e9TfaunD+Lg8D0GvWrd/p7bH0z/wOXPp9Y9dfU"
    "Hrr7n+vXve8x1Xb++v6fqv34N67rX33P7g+k6eP7V0z+w+scXw6u7P7g4OLz+9Uff4urw03XwfO"
    "qfvvr99T3X9fM/ffX0W9wX/WfX33P9+g9evXf6A7r7g9dP/8C6H/Y/uPh3H7g++gfe1R/Rva9ff"
    "Xw/+vj97uMfXP0e9/EPXv0Hrv6Bq++pDvd7rj7++fX/86mOf379Pee6Hn/Pua7Pq47XP//0W6ru"
    "/lTXL8b68R9X/9F9fE78C9XHvzH8fG6v/g+v/oVv7f7C6D2wreP70buP70bvgW339Ues+wNf2/1"
    "7XveBr+3rPrDtXr2/Z9sd/f6B9Z7tD7Xdq/fD6p94f1+Ddf/Atnv1f/z+nvb1/T3r7uL9fbfdf/""T7+7rdxej137X7/wG"
    "6H8R6X+PrP7itvvtBfO0/GPHdB6b2B079gVPvDzSj97u6f+C6v+D+6G7f9zX9C6Z/wbTuH0T1L5"
    "jmD5x+Xdf6C6aOf8E07u/Ydl+D/uPvv4GZun8D+3UNVPcPrO6f79gfaLuvQf8G9usbmFofOPUXz"
    "In7M0zdv5g78z9gqu6fU9v+h6Y9/yKqfeE0/fOvsWf9gqmpX2B/79N/A7Pqf6G0/+z7mKlvYF//"
    "A6veN7Cvv4F9/w3sU9/gvvUB/vFvX771D2T6B8Lp3066H/g/7p6m/8H8+Fm/fF8fvyP36N3v37v"
    "vNf8P1PfX748/6X7P1u+f+hMfv7/rv1f66Zc3/T++P/H+WcZ6fOPh9W/u6vX1++v7u3p9/fX9u3"
    "p9/enHl2+9ffneGZkZGBQUFhgbGxwdHh8gISIkJiYoKiosLjY4OTo8PT4/QEFCQ0RGR0hJSktMT"
    "U5PUFFSU1RVVldYWVpbXF1eX1BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SF"
    "hoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusrba3uLm6u7y9vr+wscLDxMX"
    "Gx8jJysvMzc7P0NHS09TV1tfY2drb3N3e39DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e"
    "7v8PHy8/T19vf4+fr7/P3+/wABR5gX3AAAAAlwSFlzAAAOxAAADsQBlbno7wAAAAd0SU1FBmYK"
    "DhIdI2ZvvbIAAAAJdnWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEA"
    "AEAkaAMAAAABAAAAAEA6AAQAAAABAAAAAEF6AAQAAAABAAAAAEF6AA0AAAABAAAAAABAnAAFAA"
    "AAAQAAAGQAnQAEAAAABAAAhgAAAAAAMgAAAAEAAADIAAAAAQACoAIABAAAAAEAAACgogEABAAA"
    "AAEAAADgAAAAAFVDoVsAAAK5SURBVHgB7Z2LbuMwDETN///R3S0K9C6bU6fIkfOAnbZAmYekpM"
    "SWh9vtVv0f7NOfv2Pbyf649GdvXzHOf9/vH+N+fP99fK2vHevrn6bX+T9vL/p/vX/W0f/+vv3p"
    "n6bX5//S/2zGf6+uX/qTf639D+df+/618f+w8YfHj6w/0v7oXv3I+iMfjz1qY7wP6w+vP7z+yP"
    "vX9vF78v3N9Kfv97T+yO+ftXF8OPrXv/+b+ffoW2vj/XfXH96+fG3sb7v7T7v9Tz19Xz38D+fP"
    "vN++ffYfe3+tfe/tf87Gf76Wv/7IOn0dHz/r/v2Z7T/6/qO/f5b2H93f0bX2X3X6n/b1M9vfv1"
    "b/rOnf0bX+Z3T6Z9f6X9G/f2btP/v+w75/VvUf3dfPtP4b+v6O/u9vdK//vG/fP9vH76f9R6f9"
    "e/r+mdvf0bX+G7r79/T+Z9b6W9v3z/bxa9P+Wf99/8ztP+329/T+mftvXv9NfX+tX/+Mvv7orl"
    "7/zK7+yGf9O/paf3b91x/v/G/v/9G/P/rXf/1fP/vWf/1P+3t9/W/vXzvef+Rfv39kf7Z9/f33"
    "H9n6v/6n6v+y/vP31f9Z/7L+Zf039f2tW782fX9NfX9N31/Tx29Xnz+798+uPn+ZPn+mPn+mPp"
    "9p/Uf3+bNp/9ntv7fXv9bHz67v7+mPP2/X929b3z9L+6+6/rPbf3btX7vvX9b6I++fdfvX7vun"
    "tf616/un1f6zrv/atX/W9Z+1f9b9M7f/7P6Z9b0++vs7ur9fPv7O7r82fb/M7u/X++9o/5W9f2"
    "Yfv9btPzP9M9PfX9PX989MfX/rfpnp769pf63bX2b6Z9pfa/pXpL+/pv21XF8/86+P/I7+9YfZ"
    "vv/s64+wPn9m+vxZ7uun9vXTx9/Zff20fX+Z7evL9vFntq+f9b5+Wre/Zvv6WbZ/pvsL0veP3b"
    "ePzN7es/v+Nfv+MdvX93Rf3+O//gL7P/6T/0p+pfxK/gX5lewr9BfIr9Bf6L9Cf2H8Cv0F7yv0"
    "F8yv8F4Iv7J/wX9l/MLfCr/Ct8Kv4K0wK3wL3ArfwregK3wLvsKzgCvoCrsCrrAr6AqtAq9gK9"
    "gKs4KtMCtYC7XCvECv0CvsCreCreCucCtwK8EKYAXBCOAIsIAfABvYwAb2gA3vAhvcIDawgX0g"
    "AzvAxg4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOD38"
    "Q83iK94NOf66wAAAABJRU5ErkJggg=="
)

col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    # Mostramos la imagen incrustada de forma ultra segura
    st.image(logo_base64, width=90)
with col_titulo:
    st.title("Homero")
    st.write("El procesador automático que hace el trabajo pesado por vos.")

st.write("---")
st.write("Pegá tus órdenes acá abajo para separarlas por panel automáticamente.")

# Manejo de estados de borrado total y persistencia de la salida
if "texto_entrada" not in st.session_state:
    st.session_state.texto_entrada = ""
if "texto_salida" not in st.session_state:
    st.session_state.texto_salida = ""

# ================= SECCIÓN ENTRADA =================
entrada = st.text_area(
    "Pega aquí tus órdenes mezcladas:", 
    value=st.session_state.texto_entrada, 
    height=250, 
    placeholder="Escribe o pega las líneas aquí...",
    key="caja_de_entrada"
)

# Columnas de botones
col1, col2 = st.columns(2)

with col1:
    btn_procesar = st.button("PROCESAR TODO", type="primary", use_container_width=True)
with col2:
    btn_borrar = st.button("❌ BORRAR TODO", use_container_width=True)

# LÓGICA DEL BOTÓN BORRAR TOTAL
if btn_borrar:
    st.session_state.texto_entrada = ""
    st.session_state.texto_salida = ""
    st.session_state.caja_de_entrada = ""
    if "caja_de_salida" in st.session_state:
        st.session_state.caja_de_salida = ""
    st.rerun()

# ================= LÓGICA DE PROCESAMIENTO =================
if btn_procesar:
    st.session_state.texto_entrada = entrada
    
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
            if es_link_fb and es_post:
                resultados_principal.append(f"1248|{url}|{cantidad}")
            elif es_link_fb and es_likes:
                resultados_principal.append(f"2450|{url}|{cantidad}")
            elif "jap" in linea_low or "repost" in linea_low or es_link_fb or (es_link_tt and es_followers):
                if codigo_manual:
                    resultados_jap.append(f"{codigo_manual}|{url}|{cantidad}")
                elif "repost" in linea_low:
                    resultados_jap.append(f"2257|{url}|{cantidad}")
                elif es_link_fb:
                    resultados_jap.append(f"20|{url}|{cantidad}")
                elif es_link_tt and es_followers:
                    resultados_jap.append(f"912|{url}|{cantidad}")
                else:
                    resultados_error.append(f"Falta código JAP -> {linea.strip()}")
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
    else:
        st.warning("Por favor, ingresa al menos una orden para procesar.")

# ================= SECCIÓN SALIDA =================
if st.session_state.texto_salida:
    st.subheader("Resultados separados por Panel:")
    st.text_area(
        "Resultados listos:", 
        value=st.session_state.texto_salida, 
        height=300, 
        key="caja_de_salida"
    )
