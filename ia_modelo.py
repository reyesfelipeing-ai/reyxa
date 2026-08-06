import sqlite3
import pandas as pd
import requests
import numpy as np

def consultar_clima_local():
    # Coordenadas configuradas para análisis meteorológico local (Lat: 4.70, Lon: -74.23)
    url = "https://api.open-meteo.com/v1/forecast?latitude=4.70&longitude=-74.23&hourly=precipitation&timezone=auto&forecast_days=1"
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        # Analizamos si hay probabilidad de lluvia (> 1mm) en las próximas 6 horas
        precipitacion_proximas_horas = datos['hourly']['precipitation'][:6]
        lluvia_total = sum(precipitacion_proximas_horas)
        return lluvia_total
    except Exception as e:
        print(f"Error consultando el clima: {e}")
        return 0.0

def predecir_y_decidir():
    # 1. Leer los datos locales del lote agrícola
    conexion = sqlite3.connect("base_datos_reyxa.db")
    df = pd.read_sql_query("SELECT id, temperatura, humedad_suelo FROM registro_sensores ORDER BY id ASC", conexion)
    conexion.close()

    if len(df) < 5:
        return {"estado": "info", "mensaje": "Recopilando datos del lote para calibrar el modelo..."}

    humedad_actual = df['humedad_suelo'].iloc[-1]
    
    # 2. Consultar el pronóstico externo
    lluvia_esperada_mm = consultar_clima_local()
    
    print("\n" + "="*40)
    print("🧠 MOTOR DE DECISIÓN REYXA")
    print(f"Humedad actual del suelo: {humedad_actual:.2f}%")
    print(f"Lluvia proyectada (6h): {lluvia_esperada_mm:.2f} mm")
    print("="*40)

    # 3. Lógica Difusa para toma de decisiones
    if humedad_actual < 40.0:
        if lluvia_esperada_mm > 2.0:
            return {
                "estado": "warning", 
                "mensaje": f"⚠️ Suelo seco ({humedad_actual:.1f}%), pero se aproxima lluvia ({lluvia_esperada_mm}mm). DECISIÓN: Bloquear riego preventivo para evitar exceso de agua."
            }
        else:
            return {
                "estado": "error", 
                "mensaje": f"🚨 Suelo en estrés hídrico ({humedad_actual:.1f}%) y sin lluvia en el radar. DECISIÓN: Activar válvulas de riego inmediatamente."
            }
    elif humedad_actual >= 40.0 and humedad_actual <= 65.0:
        return {
            "estado": "success", 
            "mensaje": f"🌱 Humedad óptima ({humedad_actual:.1f}%). DECISIÓN: Mantener válvulas cerradas."
        }
    else:
        return {
            "estado": "info", 
            "mensaje": f"💧 Suelo saturado ({humedad_actual:.1f}%). DECISIÓN: Monitorear el drenaje del terreno."
        }

if __name__ == "__main__":
    resultado = predecir_y_decidir()
    print(resultado['mensaje'])