import paho.mqtt.client as mqtt
import time
import json
import random

# CONFIGURACIÓN CLOUD (IGUAL QUE RECEPTOR)
MQTT_BROKER = "e14d1d760b304e20be109e4686f8d3a4.s1.eu.hivemq.cloud"
MQTT_PUERTO = 8883
MQTT_USUARIO = "admin"
MQTT_PASSWORD = "reyxa2026"
TOPIC_SENSORES = "reyxa/finca_demo/lote1/sensores"

# Configurar cliente con seguridad
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USUARIO, MQTT_PASSWORD) # Usuario y contraseña
client.tls_set()                                    # Cifrado TLS requerido por HiveMQ

print("Conectando simulador a la nube...")
client.connect(MQTT_BROKER, MQTT_PUERTO, 60)
client.loop_start()

try:
    while True:
        # Generar datos simulados
        datos = {
            "temperatura_ambiente": round(random.uniform(18.0, 25.0), 2),
            "humedad_suelo": round(random.uniform(30.0, 70.0), 2),
            "ph": round(random.uniform(6.0, 7.5), 2),
            "tds_ppm": round(random.uniform(800.0, 1200.0), 2)
        }
        
        # Enviar a la nube
        client.publish(TOPIC_SENSORES, json.dumps(datos))
        print(f"Dato enviado a la nube: {datos}")
        
        time.sleep(5) # Envía cada 5 segundos

except KeyboardInterrupt:
    print("Simulador detenido.")
    client.loop_stop()
    client.disconnect()