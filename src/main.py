import os
import time
import json
from src.domain.aggregated_data import AggregatedData
from src.file_datasource import FileDatasource
from src.shema.aggregated_data_schema import AggregatedDataSchema
import paho.mqtt.client as mqtt

# Конфігурація змінних середовища
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "agent_data_topic")
DELAY = float(os.getenv("DELAY", 0.1))


class DataAggregator:
    def __init__(self, broker_host, broker_port, topic):
        # Налаштування MQTT клієнта
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.schema = AggregatedDataSchema()
        self.is_connected = False

    def connect_to_broker(self):
        try:
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
            self.is_connected = True
            print(f"Підключено до MQTT брокера {self.broker_host}:{self.broker_port}")
            return True
        except Exception as e:
            print(f"Помилка підключення до MQTT брокера: {e}")
            self.is_connected = False
            return False

    def publish_data(self, data: AggregatedData):
        if not self.is_connected:
            print("MQTT клієнт не підключено, дані не опубліковано")
            return False

        # Серіалізуємо дані в JSON
        json_data = self.schema.dumps(data)

        # Виведення даних у зручному для читання форматі
        parsed_data = json.loads(json_data)
        print(f"Час: {parsed_data.get('time', 'невідомо')}")
        print("Акселерометр:")
        accel = parsed_data.get('accelerometer', {})
        print(f"  X: {accel.get('x', 'невідомо')}")
        print(f"  Y: {accel.get('y', 'невідомо')}")
        print(f"  Z: {accel.get('z', 'невідомо')}")
        print("GPS:")
        gps = parsed_data.get('gps', {})
        print(f"  Довгота: {gps.get('longitude', 'невідомо')}")
        print(f"  Широта: {gps.get('latitude', 'невідомо')}")
        print("--------------------------------------\n")

        # Публікуємо дані в MQTT топік
        result = self.mqtt_client.publish(self.topic, json_data)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Дані опубліковано в топік {self.topic}")
            return True
        else:
            print(f"Помилка публікації даних: {result}")
            return False


def main():
    # Шляхи до файлів відносно робочої директорії
    accelerometer_file = "../accelerometer.csv"
    gps_file = "../gps.csv"

    # Перевірка наявності файлів
    for file_path in [accelerometer_file, gps_file]:
        if not os.path.exists(file_path):
            print(f"Помилка: файл {file_path} не знайдено!")
            return

    # Ініціалізуємо джерело даних
    data_source = FileDatasource(accelerometer_file, gps_file)

    # Ініціалізуємо агрегатор даних
    aggregator = DataAggregator(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC)

    # Підключаємося до MQTT брокера
    aggregator.connect_to_broker()

    try:
        # Починаємо читання даних
        data_source.startReading()

        while True:
            try:
                # Читаємо дані
                data = data_source.read()

                # Публікуємо дані
                aggregator.publish_data(data)

                # Затримка між зчитуваннями
                time.sleep(DELAY)

            except StopIteration:
                print("Досягнуто кінця файлів даних")
                break
            except Exception as e:
                print(f"Помилка обробки даних: {e}")
                break

    finally:
        # Завершуємо читання даних
        data_source.stopReading()

        # Зупиняємо MQTT клієнт
        if aggregator.is_connected:
            aggregator.mqtt_client.loop_stop()
            aggregator.mqtt_client.disconnect()


if __name__ == "__main__":
    main()
