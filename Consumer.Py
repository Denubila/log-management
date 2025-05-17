import pika
import psycopg2
import json
from datetime import datetime

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'weather_data',
    'user': 'postgres',
    'password': '5928'  
}

# Validaciones de datos meteorológicos
def validate_data(data):
    errors = []

    if not (-100 <= data['temperature'] <= 80):
        errors.append("Temperatura fuera de rango.")
    if not (0 <= data['humidity'] <= 100):
        errors.append("Humedad fuera de rango.")
    if not (0 <= data['wind_speed'] <= 150):
        errors.append("Velocidad del viento fuera de rango.")
    if data['weather_condition'] not in ['soleado', 'nublado', 'lluvioso', 'tormenta', 'nevando']:
        errors.append("Condición climática inválida.")

    return errors

# Inserta en PostgreSQL
def insert_into_db(conn, data, status, error_msg=None):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO weather_logs (station_id, temperature, humidity, wind_speed, weather_condition, timestamp, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['station_id'],
            data['temperature'],
            data['humidity'],
            data['wind_speed'],
            data['weather_condition'],
            data['timestamp'],
            status,
            error_msg
        ))
        conn.commit()

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        errors = validate_data(data)

        status = 'valid' if not errors else 'invalid'
        error_msg = '; '.join(errors) if errors else None

        insert_into_db(pg_conn, data, status, error_msg)
        print(f"[✓] Mensaje procesado. Estado: {status}")

    except Exception as e:
        print(f"[✗] Error procesando mensaje: {e}")
    
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

# Conexión a PostgreSQL
print("[...] Conectando a PostgreSQL...")
pg_conn = psycopg2.connect(**DB_CONFIG)
print("[✓] Conectado a PostgreSQL.")

# Conexión a RabbitMQ
print("[...] Conectando a RabbitMQ...")
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Asegurar que la cola y exchange existan
channel.exchange_declare(exchange='weather_exchange', exchange_type='direct', durable=True)
channel.queue_declare(queue='weather_queue', durable=True)
channel.queue_bind(exchange='weather_exchange', queue='weather_queue', routing_key='weather.log')

# Prefetch = 1 para procesamiento ordenado
channel.basic_qos(prefetch_count=1)

# Iniciar consumo
channel.basic_consume(queue='weather_queue', on_message_callback=callback)
print("[✓] Esperando mensajes. Para salir presiona CTRL+C.")
channel.start_consuming()
