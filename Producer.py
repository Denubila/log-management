import pika
import json
import random
from datetime import datetime
import time

# Condiciones meteorológicas posibles
WEATHER_CONDITIONS = ["soleado", "nublado", "lluvioso", "tormenta", "nevando"]

def generate_weather_data():
    return {
        "station_id": "STN001",
        "temperature": round(random.uniform(-10, 45), 2),
        "humidity": round(random.uniform(20, 100), 2),
        "wind_speed": round(random.uniform(0, 100), 2),  # nueva variable
        "weather_condition": random.choice(WEATHER_CONDITIONS),  # nueva variable
        "timestamp": datetime.utcnow().isoformat()
    }

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange='weather_exchange', exchange_type='direct', durable=True)

    while True:
        data = generate_weather_data()
        message = json.dumps(data)

        channel.basic_publish(
            exchange='weather_exchange',
            routing_key='weather.log',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2  # persistente
            )
        )

        print(f"[x] Enviado: {message}")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Productor detenido.")
