import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.express as px
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="REYXA - Panel de Riego",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .stApp { background-color: #e2e8e1; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #2d5a27;
    }
    .user-card {
        background-color: #273029;
        color: #a3b899;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN SUPABASE ---
SUPABASE_URL = "https://runoqujcdjywxasfhdkl.supabase.co"
SUPABASE_KEY = "sb_publishable_hWnWSVgB__vI56X0X4-UwA_KNOhBEMT"

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- CONSULTA DE DATOS ---
latest = None
try:
    res = supabase.table("lecturas_sensores").select("*").order("created_at", desc=True).limit(1).execute()
    if res.data and len(res.data) > 0:
        latest = res.data[0]
except Exception as e:
    st.error(f"Error de conexión con Supabase: {e}")

# Lecturas dinámicas o valores de respaldo
# Reemplaza los valores por defecto "24.0 °C" y "41.2 %" por esto:
# Reemplaza la asignación de variables por esto:
temp_suelo_val = f"{latest['temp_suelo']} °C" if (latest and 'temp_suelo' in latest) else "SIN NUBE 🔴"
humedad_val = f"{latest['humedad_aire']} %" if (latest and 'humedad_aire' in latest) else "SIN NUBE 🔴"
# --- SIDEBAR (BARRA LATERAL REYXA) ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #ffffff;'>R E Y X A</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='user-card'>
            <strong style='color: white;'>Wilmar Reyes</strong><br>
            <small>Rol: SuperAdmin</small>
        </div>
    """, unsafe_allow_html=True)
    
    st.caption("GESTIÓN DE CAMPO")
    st.button("🏠 Panel de Riego", use_container_width=True)
    st.button("🗺️ Mapas de Cultivo", use_container_width=True)
    
    st.caption("ANÁLISIS")
    st.button("📊 Balance Hídrico", use_container_width=True)
    st.button("📜 Auditoría de Eventos", use_container_width=True)
    
    st.divider()
    st.button("🚪 Cerrar Sesión", use_container_width=True)

# --- CUERPO PRINCIPAL ---
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title("Módulo: Panel de Riego")
    st.caption("Finca La Esperanza - Facatativá | Conectado como: Wilmar Reyes")

with header_col2:
    if st.button("⚡ ACCIÓN MANUAL: RIEGO LOTE 1", type="primary", use_container_width=True):
        st.success("Comando enviado a la nube.")
    st.success("Válvula 1 Abierta con éxito en la nube.")

st.markdown("---")

# --- BLOQUE 1: MÉTRICAS SUPERIORES ---
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(label="Temp. Suelo", value=temp_suelo_val)

with m2:
    st.metric(label="Humedad Edáfica", value=humedad_val)

with m3:
    st.metric(label="pH Actual", value="6.5")

with m4:
    st.metric(label="TDS (Nutrientes)", value="520 ppm")

st.write("")

# --- BLOQUE 2: MÉTRICAS SECUNDARIAS + PLANIMETRÍA ---
col_left, col_right = st.columns([1, 2.2])

with col_left:
    st.caption("Sensores del Lote 1")
    st.metric(label="Presión de Línea", value="2.1 bar")
    st.write("")
    st.metric(label="Conductividad (CE)", value="1.2 dS/m")

with col_right:
    st.caption("Planimetría (Sabana / Facatativá)")
    
    df_map = pd.DataFrame({
        'lat': [4.8143],
        'lon': [-74.3533],
        'lote': ['Lote 1 - Daniel Ortega']
    })
    
    fig_map = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lon",
        hover_name="lote",
        zoom=13,
        height=320
    )
    fig_map.update_traces(marker=dict(size=22, color='#e74c3c'))
    fig_map.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    st.plotly_chart(fig_map, use_container_width=True)

# Refresco de pantalla cada 10 segundos
time.sleep(10)
st.rerun()