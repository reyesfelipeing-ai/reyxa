import base64
from datetime import datetime
import os
import time

from auth import iniciar_sesion
from config_nube import supabase
import pandas as pd
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="REYXA | Inteligencia Agropecuaria",
    page_icon="logo_symbol_only.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILOS CSS ---
st.markdown(
    """<style>
    .stApp { background-color: #E8F0E8 !important; }
    
    /* BANNER IZQUIERDO INDUSTRIAL */
    [data-testid="stSidebar"] { background-color: #262924 !important; color: white !important; }
    
    /* BOTONES DEL SIDEBAR PLANOS */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: transparent !important;
        color: #9CA3AF !important;
        width: 100% !important;
        text-align: left !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 4px !important;
        padding: 8px 10px !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #374151 !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stMetric"] { background: white; border-left: 5px solid #6C8D71; padding: 15px; border-radius: 8px; }
    
    /* BOTONES VERDES CORPORATIVOS */
    .main div.stButton > button, div.stFormSubmitButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }
    .main div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #1b5e20 !important;
        color: white !important;
    }
    
    div[data-testid="stForm"] { background-color: #FFFFFF !important; border-radius: 12px; padding: 30px; border: none !important; }
</style>""",
    unsafe_allow_html=True,
)


# --- BASE DE DATOS HELPER ---
def get_db_supabase(tabla, limite=50):
    try:
        response = (
            supabase.table(tabla)
            .select("*")
            .order("created_at", desc=True)
            .limit(limite)
            .execute()
        )
        if response.data:
            return pd.DataFrame(response.data)
    except Exception:
        pass

    try:
        response = (
            supabase.table(tabla)
            .select("*")
            .order("id", desc=True)
            .limit(limite)
            .execute()
        )
        if response.data:
            return pd.DataFrame(response.data)
    except Exception:
        pass

    try:
        response = supabase.table(tabla).select("*").limit(limite).execute()
        return pd.DataFrame(response.data)
    except Exception:
        return pd.DataFrame()


# --- AUTENTICACIÓN (LOGIN) ---
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.usuario_actual = None

login_container = st.empty()

if not st.session_state.auth:
    with login_container.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.write("<br><br>", unsafe_allow_html=True)
            if os.path.exists("logo_white_bg.png"):
                with open("logo_white_bg.png", "rb") as f:
                    encoded_logo = base64.b64encode(f.read()).decode()
                st.markdown(
                    '<div style="text-align: center; margin-bottom: 15px;">'
                    f'<img src="data:image/png;base64,{encoded_logo}" width="140"'
                    ' style="display: block; margin: 0 auto; border-radius: 10px;">'
                    "</div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                "<h3 style='text-align: center; color: #2C4230;'>Gestión Agropecuaria"
                " Inteligente</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align: center; color: #64748B;'>Control, precisión y"
                " eficiencia para el agro colombiano.</p>",
                unsafe_allow_html=True,
            )

            with st.form("form_login"):
                usuario = st.text_input(
                    "Correo electrónico corporativo", value="admin@reyxacol.com"
                )
                password = st.text_input(
                    "Código de Acceso", type="password", value="reyxa2026"
                )
                submit = st.form_submit_button(
                    "Ingresar al Sistema", use_container_width=True
                )

                if submit:
                    user_data = iniciar_sesion(usuario, password)
                    if user_data:
                        st.session_state.auth = True
                        st.session_state.usuario_actual = user_data

                        if user_data.get("tipo_cliente") == "GOBERNACION_B2G":
                            st.session_state["modo_operacion"] = (
                                "🏛️ Reservorio Comunitario (B2G)"
                            )
                        else:
                            st.session_state["modo_operacion"] = "🏢 Finca Privada (B2B)"

                        st.success("¡Acceso concedido! Cargando sistema...")
                        st.rerun()
                    else:
                        st.error(
                            "Credenciales incorrectas. Verifique con el administrador."
                        )
    st.stop()
else:
    login_container.empty()

# --- ESTADO DE NAVEGACIÓN Y USUARIO ---
if "menu_activo" not in st.session_state:
    st.session_state.menu_activo = "Panel de Riego"

usuario_actual = st.session_state.get("usuario_actual") or {}
if isinstance(usuario_actual, dict):
    nombre_mostrar = usuario_actual.get("nombre_completo") or usuario_actual.get("email", "Usuario REYXA")
    rol_mostrar = usuario_actual.get("rol", "OPERADOR")
else:
    nombre_mostrar = "Usuario REYXA"
    rol_mostrar = "OPERADOR"

# --- BANNER IZQUIERDO INDUSTRIAL (SIDEBAR ÚNICO) ---
with st.sidebar:
    if os.path.exists("logo_white_bg.png"):
        st.image("logo_white_bg.png", width=130)

    st.markdown(
        f"<p style='text-align: center; color: #6C8D71; font-size:"
        f" 0.85rem;'><b>{nombre_mostrar}</b><br>Rol: {rol_mostrar}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown(
        "<p style='color: #A3C4A0; font-size: 0.75rem; text-transform:"
        " uppercase;'>Modelo de Operación</p>",
        unsafe_allow_html=True,
    )

    modo_defecto = (
        1
        if st.session_state.get("modo_operacion") == "🏛️ Reservorio Comunitario (B2G)"
        else 0
    )
    modo_sel = st.radio(
        "Modo de Vista:",
        ["🏢 Finca Privada (B2B)", "🏛️ Reservorio Comunitario (B2G)"],
        index=modo_defecto,
        key="modo_operacion",
        label_visibility="collapsed",
    )
    st.markdown("---")

    st.markdown(
        "<p style='color: #A3C4A0; font-size: 0.75rem; text-transform:"
        " uppercase;'>Gestión de Campo</p>",
        unsafe_allow_html=True,
    )
    if st.button("🏠 Panel Principal", use_container_width=True):
        st.session_state.menu_activo = "Panel de Riego"
        st.rerun()
    if st.button("🗺️ Mapas de Cultivo", use_container_width=True):
        st.session_state.menu_activo = "Mapas de Cultivo"
        st.rerun()

    st.markdown(
        "<p style='color: #A3C4A0; font-size: 0.75rem; text-transform:"
        " uppercase;'>Análisis</p>",
        unsafe_allow_html=True,
    )
    if st.button("📊 Balance Hídrico", use_container_width=True):
        st.session_state.menu_activo = "Balance Hídrico"
        st.rerun()
    if st.button("📋 Auditoría de Eventos", use_container_width=True):
        st.session_state.menu_activo = "Auditoría de Eventos"
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.session_state.usuario_actual = None
        st.rerun()


# --- CONSULTA DE ESTADO DE VÁLVULA ---
def obtener_estado_valvula():
    try:
        res = (
            supabase.table("comandos_riego")
            .select("*")
            .order("id", desc=True)
            .limit(1)
            .execute()
        )
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass
    return None


cmd_ultimo = obtener_estado_valvula()
estado_valvula = "CERRADA"
if (
    cmd_ultimo
    and cmd_ultimo.get("accion") == "ABRIR_RIEGO"
    and cmd_ultimo.get("estado") == "EJECUTADO"
):
    estado_valvula = "ABIERTA"

# --- ENCABEZADO Y CONTROL REMOTO ---
es_b2g = st.session_state.get("modo_operacion") == "🏛️ Reservorio Comunitario (B2G)"
col_head1, col_head2 = st.columns([2.5, 1.5])

with col_head1:
    titulo_modulo = "Gestión Comunitario (B2G)" if es_b2g and st.session_state.menu_activo == "Panel de Riego" else st.session_state.menu_activo
    st.markdown(
        f"<h2 style='color: #2C4230; margin-bottom: 0px;'>Módulo: {titulo_modulo}</h2>",
        unsafe_allow_html=True,
    )
    if estado_valvula == "ABIERTA":
        st.markdown(
            "<b>Estado Válvula Principal:</b> <span style='color: #2e7d32; font-weight: bold;'>🟢 RIEGO ACTIVO (VÁLVULA ABIERTA)</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<b>Estado Válvula Principal:</b> <span style='color: #757575; font-weight: bold;'>🔴 RIEGO INACTIVO (VÁLVULA CERRADA)</span>",
            unsafe_allow_html=True,
        )

with col_head2:
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("⚡ ABRIR", use_container_width=True):
            try:
                comando_data = {
                    "dispositivo": "RESERVORIO_CENTRAL" if es_b2g else "LOTE_1",
                    "accion": "ABRIR_RIEGO",
                    "duracion_min": 30,
                    "estado": "PENDIENTE",
                    "usuario_solicitante": (
                        usuario_actual.get("email", "admin@reyxacol.com")
                        if isinstance(usuario_actual, dict)
                        else "admin@reyxacol.com"
                    ),
                }
                supabase.table("comandos_riego").insert(comando_data).execute()
                st.success("Orden ABRIR enviada.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with col_b2:
        if st.button("🔒 CERRAR", use_container_width=True):
            try:
                comando_data = {
                    "dispositivo": "RESERVORIO_CENTRAL" if es_b2g else "LOTE_1",
                    "accion": "CERRAR_RIEGO",
                    "duracion_min": 0,
                    "estado": "PENDIENTE",
                    "usuario_solicitante": (
                        usuario_actual.get("email", "admin@reyxacol.com")
                        if isinstance(usuario_actual, dict)
                        else "admin@reyxacol.com"
                    ),
                }
                supabase.table("comandos_riego").insert(comando_data).execute()
                st.warning("Orden CERRAR enviada.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# --- RENDERIZADO DINÁMICO SEGÚN EL MODO Y MENÚ ---
if st.session_state.menu_activo == "Panel de Riego":
    if es_b2g:
        # === VISTA B2G: RESERVORIO COMUNITARIO ===
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("💧 Vol. Reservorio", "4,250 m³", delta="85% Capacidad")
        kpi2.metric("👨‍🌾 Turnos Hoy", "12 Familias", delta="Vereda El Hato")
        kpi3.metric("☀️ Diésel Evitado", "320 Galones", delta="-$4.8M COP/mes")
        kpi4.metric("⚡ Bombeo Solar", "18.5 kWh/día", delta="100% Fotovoltaico")

        st.write("<br>", unsafe_allow_html=True)
        col_turnos, col_mapa_b2g = st.columns([1.5, 1])
        
        with col_turnos:
            st.markdown("### 📋 Programación de Turnos Veredales")

            # Formulario interactivo para registrar turnos en Supabase
            with st.expander("➕ Asignar Nuevo Turno Hídrico", expanded=False):
                with st.form("form_nuevo_turno"):
                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        familia_predio = st.text_input("Predio / Familia", placeholder="Ej: Parcela San Pedro")
                        vereda = st.selectbox("Vereda", ["El Hato", "Moyano", "Pueblo Viejo", "Corito"])
                    with col_f2:
                        volumen_m3 = st.number_input("Cuota Asignada (m³)", min_value=5, max_value=200, value=35)
                        estado_inicial = st.selectbox("Estado del Turno", ["PROGRAMADO", "EN_CURSO", "FINALIZADO"])
                    
                    btn_guardar_turno = st.form_submit_button("💾 Guardar Turno en Supabase", use_container_width=True)

                    if btn_guardar_turno:
                        if familia_predio.strip():
                            try:
                                nuevo_turno = {
                                    "familia_predio": familia_predio.strip(),
                                    "vereda": vereda,
                                    "volumen_m3_asignado": volumen_m3,
                                    "volumen_m3_usado": 0.0,
                                    "estado": estado_inicial,
                                    "finca_id": "RESERVORIO_FACATATIVA"
                                }
                                supabase.table("turnos_riego").insert(nuevo_turno).execute()
                                st.success(f"¡Turno guardado para {familia_predio}!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error guardando turno: {e}")
                        else:
                            st.warning("Por favor ingresa el nombre de la familia o predio.")

            # Consulta directa a la tabla turnos_riego en Supabase
            df_turnos = get_db_supabase("turnos_riego", 50)

            if not df_turnos.empty and "familia_predio" in df_turnos.columns:
                cols_turnos = [c for c in ["familia_predio", "vereda", "volumen_m3_asignado", "volumen_m3_usado", "estado"] if c in df_turnos.columns]
                df_mostrar = df_turnos[cols_turnos].rename(columns={
                    "familia_predio": "Predio / Familia",
                    "vereda": "Vereda",
                    "volumen_m3_asignado": "Cuota (m³)",
                    "volumen_m3_usado": "Usado (m³)",
                    "estado": "Estado"
                })
                st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            else:
                # Datos de demostración en caso de que la tabla en Supabase esté vacía
                df_demo = pd.DataFrame([
                    {"Predio / Familia": "Familia Rodríguez", "Vereda": "El Hato", "Cuota (m³)": 45, "Usado (m³)": 12.0, "Estado": "EN_CURSO"},
                    {"Predio / Familia": "Parcela San Luis", "Vereda": "El Hato", "Cuota (m³)": 30, "Usado (m³)": 0.0, "Estado": "PROGRAMADO"},
                    {"Predio / Familia": "Familia Gómez", "Vereda": "Moyano", "Cuota (m³)": 60, "Usado (m³)": 0.0, "Estado": "PROGRAMADO"},
                ])
                st.dataframe(df_demo, use_container_width=True, hide_index=True)
                st.caption("💡 *Usa el botón de arriba para registrar los primeros turnos en Supabase.*")

        with col_mapa_b2g:
            st.markdown("### 🗺️ Red de Distribución Comunitario")
            df_mapa = pd.DataFrame({"lat": [4.815, 4.818], "lon": [-74.354, -74.350]})
            st.map(df_mapa, zoom=13, use_container_width=True)

    else:
        # === VISTA B2B: FINCA PRIVADA ===
        df = get_db_supabase("lecturas_sensores", 50)
        if df.empty:
            df = get_db_supabase("registro_sensores", 50)

        humedad_actual = 50.0

        if df.empty:
            temp_val, hum_val, ph_val, tds_val = ("Sin datos", "Sin datos", "6.5", "520 ppm")
        else:
            ultimo = df.iloc[0]
            val_t = ultimo.get("temp_suelo", ultimo.get("temperatura", "N/A"))
            val_h = ultimo.get("humedad_aire", ultimo.get("humedad_suelo", "N/A"))
            val_p = ultimo.get("ph", 6.5)
            val_tds = ultimo.get("tds", 520)

            temp_val = f"{val_t} °C" if val_t != "N/A" else "N/A"
            hum_val = f"{val_h} %" if val_h != "N/A" else "N/A"
            ph_val = f"{val_p}"
            tds_val = f"{val_tds} ppm"

            try:
                humedad_actual = float(val_h)
            except (ValueError, TypeError):
                humedad_actual = 50.0

        if humedad_actual < 35.0:
            st.error(f"⚠️ **ESTRÉS HÍDRICO DETECTADO:** La humedad edáfica cayó al {humedad_actual:.1f}%. El cultivo requiere riego.")
            col_aut1, col_aut2 = st.columns([2, 1])
            with col_aut1:
                if st.button("🤖 EJECUTAR RIEGO AUTÓNOMO (30 MIN)", use_container_width=True):
                    try:
                        comando_autonomo = {
                            "dispositivo": "LOTE_1",
                            "accion": "ABRIR_RIEGO",
                            "duracion_min": 30,
                            "estado": "PENDIENTE",
                            "usuario_solicitante": "SISTEMA_AUTONOMO_REYXA",
                        }
                        supabase.table("comandos_riego").insert(comando_autonomo).execute()
                        st.success("🤖 Orden de riego autónomo enviada a la nube.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al enviar orden autónoma: {e}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temp. Suelo", temp_val)
        c2.metric("Humedad Edáfica", hum_val)
        c3.metric("pH Actual", ph_val)
        c4.metric("TDS (Nutrientes)", tds_val)

        st.write("<br>", unsafe_allow_html=True)
        col_s, col_m = st.columns([1, 2.5])
        with col_s:
            st.markdown("**Sensores del Lote 1**")
            st.metric("Presión de Línea", "2.1 bar")
            st.metric("Conductividad (CE)", "1.2 dS/m")
        with col_m:
            st.markdown("**Planimetría (Sabana / Facatativá)**")
            df_mapa = pd.DataFrame({"lat": [4.815], "lon": [-74.354]})
            st.map(df_mapa, zoom=14, use_container_width=True)

elif st.session_state.menu_activo == "Mapas de Cultivo":
    st.markdown("### Vista Satelital y Sectores de la Finca / Reservorio")
    df_mapa = pd.DataFrame(
        {"lat": [4.815, 4.818, 4.812], "lon": [-74.354, -74.350, -74.360]}
    )
    st.map(df_mapa, zoom=13, use_container_width=True)
    st.info("Distribución espacial de nodos analíticos y sensores de suelo activos en los sectores.")

elif st.session_state.menu_activo == "Balance Hídrico":
    st.markdown("### Indicadores de Eficiencia e Impacto Agronómico")

    df_cmds = get_db_supabase("comandos_riego", 100)
    riegos_ejecutados = 0
    if not df_cmds.empty and "estado" in df_cmds.columns:
        riegos_ejecutados = len(df_cmds[df_cmds["estado"] == "EJECUTADO"])

    litros_ahorrados = riegos_ejecutados * 450
    gasolina_ahorrada_gal = riegos_ejecutados * 0.4
    pesos_ahorrados = gasolina_ahorrada_gal * 15500

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Agua Optimizada", f"{litros_ahorrados:,} L", delta="Goteo de Precisión")
    kpi2.metric("Gasolina Evitada", f"{gasolina_ahorrada_gal:.1f} Gal", delta="100% Solar")
    kpi3.metric("Ahorro Estimado ($)", f"${pesos_ahorrados:,.0f} COP", delta="Reducción de Costos")

    st.write("<br>", unsafe_allow_html=True)

    st.markdown("### Evolución Histórica de Telemetría")
    df_hist = get_db_supabase("lecturas_sensores", 100)
    if df_hist.empty:
        df_hist = get_db_supabase("registro_sensores", 100)

    if not df_hist.empty:
        if "id" in df_hist.columns:
            df_hist = df_hist.sort_values(by="id", ascending=True).reset_index(drop=True)
        elif "created_at" in df_hist.columns:
            df_hist = df_hist.sort_values(by="created_at", ascending=True).reset_index(drop=True)

        if "created_at" in df_hist.columns:
            df_hist["Hora"] = pd.to_datetime(df_hist["created_at"]).dt.strftime("%H:%M:%S")
        else:
            df_hist["Hora"] = df_hist.index.astype(str)

        col_t = "temp_suelo" if "temp_suelo" in df_hist.columns else "temperatura"
        col_h = "humedad_aire" if "humedad_aire" in df_hist.columns else "humedad_suelo"

        if col_t in df_hist.columns and col_h in df_hist.columns:
            df_chart = df_hist[["Hora", col_t, col_h]].copy()
            df_chart.columns = ["Hora", "Temperatura (°C)", "Humedad (%)"]
            df_chart = df_chart.set_index("Hora")

            st.line_chart(df_chart, color=["#E74C3C", "#2E7D32"])
            st.markdown("#### Registro de Muestreos Recientes")
            st.dataframe(df_chart.tail(10), use_container_width=True, hide_index=False)
        else:
            st.warning("Estructura de columnas no reconocida para generar la gráfica.")
    else:
        st.info("No hay datos históricos registrados en la nube aún.")

elif st.session_state.menu_activo == "Auditoría de Eventos":
    st.markdown("### Bitácora de Comandos y Activaciones de Riego")
    df_ev = get_db_supabase("comandos_riego", 20)

    if not df_ev.empty:
        cols_mostrar = [
            c for c in [
                "created_at",
                "dispositivo",
                "accion",
                "duracion_min",
                "estado",
                "usuario_solicitante",
            ] if c in df_ev.columns
        ]
        df_vista = df_ev[cols_mostrar].copy()

        if "created_at" in df_vista.columns:
            df_vista["created_at"] = pd.to_datetime(df_vista["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            df_vista.rename(columns={"created_at": "Fecha / Hora"}, inplace=True)

        st.dataframe(df_vista, use_container_width=True, hide_index=True)
    else:
        st.info("No hay eventos ni órdenes registradas en la nube todavía.")

time.sleep(5)
st.rerun()