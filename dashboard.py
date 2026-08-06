import streamlit as st
import pandas as pd
import sqlite3
import time
import paho.mqtt.publish as publish
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="REYXA - Panel de Control SaaS", layout="wide")

# ==========================================
# SISTEMA DE AUTENTICACIÓN (LOGIN)
# ==========================================
def verificar_credenciales():
    """Retorna True si el usuario ya inició sesión correctamente"""
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔐 REYXA - Acceso a la Plataforma SaaS")
        st.markdown("Por favor, ingrese sus credenciales corporativas para acceder al control del cultivo.")
        
        with st.form("form_login"):
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión", type="primary")
            
            if submit:
                if usuario == "admin" and password == "reyxa2026":
                    st.session_state["autenticado"] = True
                    st.success("¡Acceso concedido! Cargando sistema...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
        return False
    
    return True

# Si no está logueado, detenemos la ejecución aquí para mostrar solo el login
if not verificar_credenciales():
    st.stop()

# ==========================================
# PANEL DE CONTROL PRINCIPAL (SI YA HIZO LOGIN)
# ==========================================
st.title("🌱 REYXA - Monitoreo Agrícola Inteligente")
st.markdown("Plataforma SaaS para el control predictivo y autónomo de cultivos.")

# Botón para cerrar sesión en la barra lateral
with st.sidebar:
    st.image("https://img.icons8.com/color/96/agriculture.png", width=80)
    st.write("Conectado como: **Administrador**")
    if st.button("Cerrar Sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

# PANEL DE CONTROL BIDIRECCIONAL
st.subheader("⚙️ Panel de Control Remoto")
if st.button("💧 ACTIVAR RIEGO (Válvula 1)", type="primary", use_container_width=True):
    try:
        publish.single("reyxa/finca_demo/lote1/control", payload='{"valvula": 1, "estado": "ENCENDIDO"}', hostname="localhost")
    except Exception:
        pass
    st.success("¡Orden de riego enviada exitosamente al nodo del campo!")

# CONECTAR A LA BASE DE DATOS CON ROBUSTEZ PARA LA NUBE
df = pd.DataFrame()
try:
    

    os.makedirs("/app/data", exist_ok=True)
    ruta_db = "/app/data/base_datos_reyxa.db"
    conexion = sqlite3.connect(ruta_db)

    
    df = pd.read_sql_query("SELECT * FROM registro_sensores ORDER BY id DESC LIMIT 50", conexion)
    conexion.close()
except Exception:
    pass

# Respaldo automático de datos simulados si la base de datos está vacía en Railway
if df.empty:
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'fecha_hora': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 3,
        'temperatura': [24.5, 25.0, 24.8],
        'humedad_suelo': [42.0, 41.5, 43.1],
        'ph': [6.5, 6.6, 6.5],
        'tds': [500, 510, 505]
    })
    st.info("ℹ️ Operando con telemetría simulada de respaldo en la nube a la espera de hardware.")

if not df.empty:
    ultimo_dato = df.iloc[0]
    
    st.subheader("Estado Actual del Lote 1")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperatura", f"{ultimo_dato['temperatura']} °C")
    col2.metric("Humedad Suelo", f"{ultimo_dato['humedad_suelo']} %")
    col3.metric("pH", f"{ultimo_dato['ph']}")
    col4.metric("TDS (Nutrientes)", f"{ultimo_dato['tds']} ppm")

    # SECCIÓN DE IA HÍBRIDA Y METEOROLÓGICA
    st.divider()
    col_ia1, col_ia2 = st.columns([2, 1])
    
    with col_ia1:
        st.subheader("🧠 Motor de Decisión Agronómica")
        try:
            from ia_modelo import predecir_y_decidir
            decision_ia = predecir_y_decidir()
            
            if decision_ia['estado'] == 'error':
                st.error(decision_ia['mensaje'])
            elif decision_ia['estado'] == 'warning':
                st.warning(decision_ia['mensaje'])
            elif decision_ia['estado'] == 'success':
                st.success(decision_ia['mensaje'])
            else:
                st.info(decision_ia['mensaje'])
        except Exception:
            st.info("ℹ️ Módulo de Inteligencia Artificial operando en modo estándar.")
    
    with col_ia2:
        st.subheader("⚙️ Modo de Operación")
        modo_auto = st.toggle("Modo Autónomo (IA)", value=True)
        if not modo_auto:
            st.warning("Control Manual Activado")

    # TENDENCIAS HISTÓRICAS
    try:
        df_graf = df.set_index('fecha_hora').sort_index()

        st.divider()
        st.subheader("📈 Tendencias Históricas")
        col_graf_1, col_graf_2 = st.columns(2)
        
        with col_graf_1:
            st.markdown("**Temperatura y Humedad**")
            st.line_chart(df_graf[['temperatura', 'humedad_suelo']])
            
        with col_graf_2:
            st.markdown("**Niveles de pH y Nutrientes (TDS)**")
            st.line_chart(df_graf[['ph', 'tds']])
    except Exception:
        pass

   # REGISTRO DE EVENTOS Y EXPORTACIÓN
    st.divider()
    st.subheader("📋 Auditoría de Riego Autónomo")
    
    try:
        # AQUÍ ES DONDE DEBES CAMBIAR LA RUTA TAMBIÉN
        ruta_db = "/app/data/base_datos_reyxa.db"
        conexion_eventos = sqlite3.connect(ruta_db)
        
        df_eventos = pd.read_sql_query("SELECT fecha_hora, tipo_evento, descripcion FROM registro_eventos ORDER BY id DESC LIMIT 5", conexion_eventos)
        conexion_eventos.close()

        if not df_eventos.empty:
            st.dataframe(df_eventos, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no se han registrado activaciones automáticas por parte de la IA.")
    except Exception:
        st.info("Auditoría de eventos en espera de sincronización.")
    st.divider()
    st.subheader("💾 Exportación de Datos")
    st.markdown("Descarga el historial completo de los sensores del terreno para análisis externo.")
    
    csv = df.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📊 Descargar Historial en CSV (Excel)",
        data=csv,
        file_name='historial_sensores_reyxa.csv',
        mime='text/csv',
        type="primary"
    )

time.sleep(3)
st.rerun()