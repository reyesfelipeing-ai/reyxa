import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import sqlite3
import json
from datetime import datetime
from ia_modelo import predecir_y_decidir

# ==========================================
# CONFIGURACIÓN DE HIWEMQ CLOUD (NUBE)
# ==========================================
MQTT_BROKER = "e14d1d760b304e20be109e4686f8d3a4.s1.eu.hivemq.cloud"  # Copia el MQTT URL de tu panel
MQTT_PUERTO = 8883
MQTT_USUARIO = "admin"                          # El usuario que creaste en HiveMQ
MQTT_PASSWORD = "reyxa2026"                      # La contraseña de tu cluster

TOPIC_SENSORES = "reyxa/finca_demo/lote1/sensores"
TOPIC_CONTROL = "reyxa/finca_demo/lote1/control"

# Inicializar Base de Datos (Local o en la nube según prefieras)
def inicializar_bd():
    conexion = sqlite3.connect("base_datos_reyxa.db")
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_sensores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            temperatura REAL,
            humedad_suelo REAL,
            ph REAL,
            tds REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT,
            tipo_evento TEXT,
            descripcion TEXT
        )
    ''')
    conexion.commit()
    conexion.close()

def registrar_evento(tipo, descripcion):
    conexion = sqlite3.connect("base_datos_reyxa.db")
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO registro_eventos (fecha_hora, tipo_evento, descripcion) VALUES (?, ?, ?)",
        (fecha_actual, tipo, descripcion)
    )
    conexion.commit()
    conexion.close()

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"\n[CLOUD BACKEND] Dato recibido: {payload}")
    
    try:
        datos = json.loads(payload)
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar telemetría
        conexion = sqlite3.connect("base_datos_reyxa.db")
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO registro_sensores (fecha_hora, temperatura, humedad_suelo, ph, tds) VALUES (?, ?, ?, ?, ?)",
            (fecha_actual, datos['temperatura_ambiente'], datos['humedad_suelo'], datos['ph'], datos['tds_ppm'])
        )
        conexion.commit()
        conexion.close()

        # Ejecución de la IA
        decision_ia = predecir_y_decidir()
        
        if decision_ia['estado'] == 'error':
            print("🚨 [ALERTA IA] Sequía detectada. Publicando orden en la nube...")
            orden = json.dumps({"valvula": 1, "estado": "ENCENDIDO", "origen": "IA_AUTONOMA"})
            
            # Publicar usando TLS y credenciales en la nube
            publish.single(TOPIC_CONTROL, payload=orden, hostname=MQTT_BROKER, port=MQTT_PUERTO, 
                           auth={'username': MQTT_USUARIO, 'password': MQTT_PASSWORD}, tls={})
            
            registrar_evento("RIEGO_AUTOMATICO", decision_ia['mensaje'])
            
        elif decision_ia['estado'] == 'warning' or decision_ia['estado'] == 'success':
            print("🌱 [CLOUD BACKEND] Condiciones estables.")

    except Exception as e:
        print(f"Error procesando el dato: {e}")

# Configurar cliente MQTT con seguridad TLS para HiveMQ Cloud
print("Conectando Backend REYXA al Broker en la Nube...")
inicializar_bd()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USUARIO, MQTT_PASSWORD)  # Autenticación
client.tls_set()                                    # Habilitar seguridad TLS (Puerto 8883)
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PUERTO, 60)
client.subscribe(TOPIC_SENSORES)

print(f"Backend escuchando en la nube (Tópico: {TOPIC_SENSORES})")
client.loop_forever()