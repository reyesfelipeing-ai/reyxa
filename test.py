import streamlit as st
from supabase import create_client

st.title("🔥 PRUEBA DE CONEXIÓN REYXA")

SUPABASE_URL = "https://runoqujcdjywxasfhdkl.supabase.co"
SUPABASE_KEY = "sb_publishable_hWnWSVgB__vI56X0X4-UwA_KNOhBEMT"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    res = supabase.table("lecturas_sensores").select("*").order("created_at", desc=True).limit(1).execute()
    st.write("📋 **Último registro encontrado en Supabase:**")
    st.json(res.data)
except Exception as e:
    st.error(f"❌ Error conectando a Supabase: {e}")