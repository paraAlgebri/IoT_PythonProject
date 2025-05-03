import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime


# Функція для створення випадкових даних з датчиків
def generate_random_data():
    return {
        'accelerometer_x': round(random.uniform(-2.0, 2.0), 2),
        'accelerometer_y': round(random.uniform(-2.0, 2.0), 2),
        'accelerometer_z': round(random.uniform(-2.0, 2.0), 2),
        'gps_latitude': round(random.uniform(50.4000, 50.5000), 4),
        'gps_longitude': round(random.uniform(30.5000, 30.6000), 4),
        'timestamp': int(time.time())
    }


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


def on_publish(client, userdata, mid):
    print(f"Message {mid} published. Time: {datetime.now().strftime('%H:%M:%S')}")


def run_sender(broker_host='mqtt', broker_port=1883, topic='agent_data_topic', interval=2):
    client = mqtt.Client(client_id=f"data_sender_{int(time.time())}")
    client.on_connect = on_connect
    client.on_publish = on_publish

    print(f"Connecting to {broker_host}:{broker_port}")
    client.connect(broker_host, broker_port)
    client.loop_start()

    message_count = 0
    try:
        while True:
            message_count += 1
            data = generate_random_data()
            print(f"Sending message #{message_count}: {json.dumps(data)}")

            client.publish(topic, json.dumps(data), qos=1, retain=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopping sender...")
    finally:
        client.loop_stop()
        client.disconnect()
        print("Sender stopped")


if __name__ == "__main__":
    import os

    broker_host = os.environ.get('MQTT_BROKER_HOST', 'mqtt')
    broker_port = int(os.environ.get('MQTT_BROKER_PORT', 1883))
    topic = os.environ.get('MQTT_TOPIC', 'agent_data_topic')
    interval = int(os.environ.get('SEND_INTERVAL', 2))

    print(f"Starting sender to {broker_host}:{broker_port} on topic {topic}")
    run_sender(broker_host, broker_port, topic, interval)
