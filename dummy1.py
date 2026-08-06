import paho.mqtt.client as mqtt
import time
import random
import json

# ==========================================
# Configuración del Nodo y Servidor
# ==========================================
BROKER_ADDRESS = "127.0.0.1"  # "localhost" si pruebas todo en la misma PC
PORT = 1883
TOPIC_DATA_OUT = "Invernadero/DataOut"
ID_DISPOSITIVO = "nodo_virtual_01"

# Variables iniciales simuladas (condiciones base del cultivo)
temp_ds1 = 18.5
temp_ds2 = 18.3
tds_1 = 850.0
tds_2 = 845.0
ph_val = 6.5

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[EXITO] Nodo '{ID_DISPOSITIVO}' conectado al Broker MQTT.")
    else:
        print(f"[ERROR] Conexión fallida con código {rc}")

# Inicializar cliente MQTT
client = mqtt.Client(ID_DISPOSITIVO)
client.on_connect = on_connect

# Conectar al broker local
try:
    client.connect(BROKER_ADDRESS, PORT, 60)
except Exception as e:
    print(f"No se pudo conectar al broker. ¿Está Mosquitto corriendo? Error: {e}")
    exit()

client.loop_start()

print("Iniciando simulación de sensores agrícolas... (Presiona Ctrl+C para detener)")

try:
    while True:
        # Simular fluctuaciones naturales del cultivo (ruido en sensores)
        temp_ds1 += random.uniform(-0.2, 0.2)
        temp_ds2 += random.uniform(-0.2, 0.2)
        tds_1 += random.uniform(-5.0, 5.0)
        tds_2 += random.uniform(-5.0, 5.0)
        ph_val += random.uniform(-0.05, 0.05)

        # Empaquetar los datos en formato JSON para que sea fácil de leer después
        payload = {
            "dispositivo": ID_DISPOSITIVO,
            "sensores": {
                "temperatura_1": round(temp_ds1, 2),
                "temperatura_2": round(temp_ds2, 2),
                "tds_1": round(tds_1, 2),
                "tds_2": round(tds_2, 2),
                "ph": round(ph_val, 2)
            },
            "timestamp": int(time.time())
        }

        # Convertir a texto y publicar
        msg_str = json.dumps(payload)
        client.publish(TOPIC_DATA_OUT, msg_str)
        
        print(f"[ENVIADO] {msg_str}")
        
        # Esperar 5 segundos antes de la siguiente lectura
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulación detenida por el usuario.")
    client.loop_stop()
    client.disconnect()