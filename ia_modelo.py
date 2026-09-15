import pandas as pd
import requests
from config_nube import supabase

def consultar_clima_local():
    """Consulta el pronóstico del tiempo en tiempo real usando Open-Meteo"""
    # Coordenadas configuradas para Cundinamarca / Sabana
    url = "https://api.open-meteo.com/v1/forecast?latitude=4.70&longitude=-74.23&hourly=precipitation&timezone=auto&forecast_days=1"
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        # Analizamos si hay probabilidad de lluvia en las próximas 6 horas
        precipitacion_proximas_horas = datos['hourly']['precipitation'][:6]
        lluvia_total = sum(precipitacion_proximas_horas)
        return lluvia_total
    except Exception as e:
        print(f"Error consultando el clima: {e}")
        return 0.0

def predecir_y_decidir():
    """
    Motor de IA Agronómica de REYXA.
    Combina variables edafoclimáticas de Supabase con pronóstico meteorológico externo.
    """
    try:
        # 1. Leer los datos más recientes del lote desde Supabase
        response = supabase.table("registro_sensores").select("*").order("id", desc=True).limit(50).execute()
        df = pd.DataFrame(response.data)

        if df.empty or len(df) < 2:
            return {
                "estado": "info", 
                "mensaje": "⚠️ Recopilando datos del lote en la nube para calibrar el modelo..."
            }

        humedad_actual = float(df['humedad_suelo'].iloc[0])
        temp_actual = float(df['temperatura'].iloc[0])
        ph_actual = float(df['ph'].iloc[0]) if 'ph' in df.columns else 6.5
        
        # 2. Consultar el pronóstico externo (Open-Meteo)
        lluvia_esperada_mm = consultar_clima_local()
        
        # 3. Lógica experta de toma de decisiones
        if humedad_actual < 40.0:
            if lluvia_esperada_mm > 2.0:
                return {
                    "estado": "warning", 
                    "mensaje": f"⚠️ Suelo seco ({humedad_actual:.1f}%), pero se aproxima lluvia ({lluvia_esperada_mm:.1f}mm). DECISIÓN: Bloquear riego preventivo para evitar encharcamiento."
                }
            else:
                return {
                    "estado": "error", 
                    "mensaje": f"🚨 Suelo en estrés hídrico ({humedad_actual:.1f}%) y sin lluvia en el radar. DECISIÓN: Activar válvulas de riego inmediatamente."
                }
        elif 40.0 <= humedad_actual <= 65.0:
            return {
                "estado": "success", 
                "mensaje": f"🌱 Humedad óptima ({humedad_actual:.1f}%). pH: {ph_actual}. DECISIÓN: Mantener válvulas cerradas. Sistema estable."
            }
        else:
            return {
                "estado": "info", 
                "mensaje": f"💧 Suelo saturado ({humedad_actual:.1f}%). DECISIÓN: Monitorear el drenaje del terreno y canales."
            }

    except Exception as e:
        return {
            "estado": "error",
            "mensaje": f"❌ Error en el motor analítico de la nube: {e}"
        }

if __name__ == "__main__":
    resultado = predecir_y_decidir()
    print(resultado['mensaje'])