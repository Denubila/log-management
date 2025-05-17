import pika
import json
import time

# Datos de ejemplo (puedes variar los valores)
weather_data = {
    "station_id": "STN001",
    "temperature": 28.5,
    "humidity": 55.2,
    "wind_speed": 15.3,
    "weather_condition": "nublado",
    "timestamp": "2025-05-16T19:00:00"
}

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

# Declarar el exchange y la cola si es necesario
channel.exchange_declare(exchange="weather_logs", exchange_type="fanout", durable=True)
channel.queue_declare(queue="weather_queue", durable=True)
channel.queue_bind(exchange="weather_logs", queue="weather_queue")

# Publicar el mensaje
channel.basic_publish(
    exchange="weather_logs",
    routing_key="",
    body=json.dumps(weather_data),
    properties=pika.BasicProperties(
        delivery_mode=2  # mensaje persistente
    )
)

print("[x] Mensaje enviado:", weather_data)

connection.close()
