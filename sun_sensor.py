import config
import numpy as np
import requests
import time

from photoresistor import Photoresistor


class SunSensor:
    """
    Class representing a sun sensor.

    This class handles reading values from photoresistors,
    calculating the light vector, and transmitting data to an app.
    """

    def __init__(self, read_interval=config.sun_sensor["READ_INTERVAL"], sensors=config.sun_sensor["SENSORS"]):
        """
        Initialize the SunSensor instance.

        Args:
            read_interval (float, optional): Time interval for reading sensors.
                                             Defaults to 1 second.
        """
        self.photoresistors = self._initialize_photoresistors(sensors)
        self.read_interval = read_interval
        self.light_vector = None

    @staticmethod
    def _initialize_photoresistors(sensors):
        photoresistors = []
        for sensor in sensors:
            pin_key,color,vector = sensor
            photoresistors.append(Photoresistor(pin_key, color,vector))
        return photoresistors

    def run(self):
        """
        Run APP: reading sensors, calculating light vector, and sending data.
        """
        try:
            while True:
                self.read_sensors_value()
                self.calc_light_vector()

                if config.sun_sensor["PRINT_RESULT"]:
                    self.print_sensors_value()
                    self.print_light_vector()

                if config.plot_app["PRINT_PLOT_APP"]:
                    self.transmit_vec_to_plot_app()

                if self.read_interval is not None:
                    time.sleep(self.read_interval)
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")

    def read_sensors_value(self):
        """
        Read the values from all sensors.
        """
        for photoresistor in self.photoresistors:
            photoresistor.read_sensor_value()

    def calc_light_vector(self):
        """
        Calculate the light vector based on sensor values.
        """
        # Transformation matrix for sensor directions
        T_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])

        # Differences between sensor pairs
        subtract_values = np.zeros(3)

        max_value = max(sensor.value_raw for sensor in self.photoresistors)
        if max_value == 0:
            raise ValueError("Cannot calculate light vector: all sensor values are 0.")

        for i, vector in enumerate(T_matrix):
            # Find values of corresponding sensors for each direction vector
            value1, value2 = 0, 0
            for sensor in self.photoresistors:
                if sensor.vector == tuple(vector):
                    value1 = sensor.value_raw
                elif sensor.vector == tuple(-1 * vector):
                    value2 = sensor.value_raw

            max_value = max(max_value, value1, value2)
            subtract_values[i] = value1 - value2

        # Calculate light vector using sensor differences and transformation matrix
        s = (1 / max_value) * T_matrix.transpose() * subtract_values
        self.light_vector = np.diagonal(s)

    def print_sensors_value(self):
        """
        Print the values of all sensors.
        """
        for sensor in self.photoresistors:
            print(f"{sensor.name}_{sensor.color}: {sensor.value_raw}")

    def print_light_vector(self):
        """
        Print the calculated light vector.
        """
        print("light_vec: ", self.light_vector, "\n")

    def get_light_vec(self):
        """
        Get the calculated light vector.

        Returns:
            numpy.ndarray: The light vector.
        """
        return self.light_vector

    def transmit_vec_to_plot_app(self):
        """
        Send sensor data to a app for printing.
        """
        data = [self.light_vector.tolist(), [sensor.get_norm_value() for sensor in self.photoresistors]]
        try:
            response = requests.post(config.plot_app['UPDATE_VECTOR'], json=data, headers=config.plot_app['API_KEY'])
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("An error occurred while sending the data:", e)