from csv import reader
from datetime import datetime

from src.domain.accelerometer import Accelerometer
from src.domain.aggregated_data import AggregatedData
from src.domain.gps import Gps


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        """
        Ініціалізує джерело даних з файлів CSV.

        Args:
            accelerometer_filename: шлях до CSV файлу з даними акселерометра
            gps_filename: шлях до CSV файлу з даними GPS
        """
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.accelerometer_file = None
        self.gps_file = None
        self.accelerometer_reader = None
        self.gps_reader = None

    def read(self) -> AggregatedData:
        """
        Метод повертає дані отримані з датчиків.
        Якщо досягнуто кінця файлу, файл починає читатись заново з початку.

        Returns:
            AggregatedData: об'єкт з агрегованими даними з датчиків
        """
        if self.accelerometer_reader is None or self.gps_reader is None:
            raise ValueError("Спочатку викличте startReading() перед читанням даних")

        try:
            # Читаємо рядок даних з файлу акселерометра
            accel_row = next(self.accelerometer_reader)
            x, y, z = float(accel_row[0]), float(accel_row[1]), float(accel_row[2])
            accelerometer = Accelerometer(x=x, y=y, z=z)

            # Читаємо рядок даних з файлу GPS
            gps_row = next(self.gps_reader)
            latitude, longitude = float(gps_row[0]), float(gps_row[1])
            gps = Gps(latitude=latitude, longitude=longitude)

            # Створюємо та повертаємо агреговані дані
            return AggregatedData(
                accelerometer=accelerometer,
                gps=gps,
                time=datetime.now()
            )
        except StopIteration:
            # Якщо досягнуто кінця файлу, перезапускаємо читання
            self.stopReading()
            self.startReading()
            # Рекурсивно викликаємо метод знову для читання першого рядка
            return self.read()

    def startReading(self, *args, **kwargs):
        """
        Метод повинен викликатись перед початком читання даних.
        Відкриває файли та ініціалізує CSV-читачі.
        """
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')

        self.accelerometer_reader = reader(self.accelerometer_file)
        self.gps_reader = reader(self.gps_file)

        # Пропускаємо заголовки
        next(self.accelerometer_reader, None)
        next(self.gps_reader, None)

    def stopReading(self, *args, **kwargs):
        """
        Метод повинен викликатись для закінчення читання даних.
        Закриває відкриті файли та очищає ресурси.
        """
        if self.accelerometer_file:
            self.accelerometer_file.close()
            self.accelerometer_file = None

        if self.gps_file:
            self.gps_file.close()
            self.gps_file = None

        self.accelerometer_reader = None
        self.gps_reader = None