import config
import numpy as np
import requests
import time

from photoresistor import Photoresistor
import logging

logger = logging.getLogger(__name__)

class SunSensor:
    """
   Class representing a sun sensor.

   This class handles reading values from photoresistors,
   calculating the light vector, and transmitting data to an app.

   """
    def __init__(self, read_interval=config.sun_sensor["READ_INTERVAL"], sensors=config.sun_sensor["SENSORS"],stop_event=None):
        """
        Initialize the SunSensor instance.

        Args:
            read_interval (float, optional): Time interval for reading sensors.
                                             Defaults to 1 second.
            sensors (list, optional): A list of dictionaries representing sensor configurations.
                                      Defaults to the value from config.sun_sensor["SENSORS"].
            stop_event (threading.Event, optional): An event to signal when to stop sensor reading. Defaults to None.
        """
        self.photoresistors = self._initialize_photoresistors(sensors)
        self.read_interval = read_interval
        self.light_vector = None
        self.stop_event = stop_event

    @staticmethod
    def _initialize_photoresistors(sensors):
        """
        Initialize a list of Photoresistor objects based on the provided sensor data.

        This method takes a list of sensor dictionaries, where each dictionary contains
        the information required to create a Photoresistor object, such as pin key, color, and vector.
        It then initializes the Photoresistor objects and appends them to a list.

        Args:
            sensors (list): A list of dictionaries where each dictionary represents a sensor with keys:
                             "pin_key", "color", and "vector" (a list or tuple).

        Returns:
            list: A list of Photoresistor objects initialized with the data from the provided sensor list.
        """
        photoresistors = []
        for sensor in sensors:
            pin_key = sensor["pin_key"]
            color = sensor["color"]
            vector = tuple(sensor["vector"])
            photoresistors.append(Photoresistor(pin_key, color,vector))
        return photoresistors

    def run(self):
        """
            Run the SunSensor application: read sensor values, calculate the light vector,
            and transmit data to the plot application.

            Exception Handling:
                If an error occurs during the reading, calculation, or transmission process,
                it will be caught and logged.

            Cleanup:
                After the process ends, an attempt is made to remove the light vector
                from the plot application, if configured.

            Raises:
                Exception: Any errors encountered during the execution will be caught
                           and printed.
            """
        try:
            while self.stop_event is None or not self.stop_event.is_set():
                self.read_sensors_value()
                self.calc_light_vector()

                if config.sun_sensor["PRINT_RESULT"]:
                    self.print_sensors_value()
                    self.print_light_vector()

                if config.plot_app["PRINT_PLOT_APP"]:
                    self.transmit_vec_to_plot_app()

                if self.read_interval is not None:
                    time.sleep(self.read_interval)

        except Exception as e:
            logger.error("SunSensor runtime error: %s", e)
        finally:
            if config.plot_app["PRINT_PLOT_APP"]:
                try:
                    self.transmit_vec_to_plot_app(shutdown=True)
                except Exception as e:
                    logger.warning("Failed to remove vector from plot_app: %s", e)
            logger.info("SunSensor has ended.")

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

        max_value = max(sensor.value for sensor in self.photoresistors)
        if max_value == 0:
            logger.warning("Cannot calculate light vector: all sensor values are 0.")
            raise ValueError("Cannot calculate light vector: all sensor values are 0.")

        for i, vector in enumerate(T_matrix):
            # Find values of corresponding sensors for each direction vector
            value1, value2 = 0, 0
            for sensor in self.photoresistors:
                if sensor.vector == tuple(vector):
                    value1 = sensor.value
                elif sensor.vector == tuple(-1 * vector):
                    value2 = sensor.value

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
            print("AIN_",sensor.channel,"_", sensor.color,": ", sensor.get_norm_value())

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

    def transmit_vec_to_plot_app(self, shutdown=False):
        """
        This method formats the sensor data, including the light vector and sensor values,
        into a JSON structure and sends it via a POST request to the plot application
        specified in the configuration.

        If the request is successful, the plot app is updated with the new data. If there is
        any error during the request (e.g., connection issues, API errors), an exception is caught
        and logged.

        Raises:
            requests.exceptions.RequestException: If an error occurs during the request, the exception is caught and logged.
        """
        if shutdown:
            self.light_vector = np.array([0.0, 0.0, 0.0])
            for sensor in self.photoresistors:
                sensor.value = 0.0

            data = {
                "light_vector": [0.0,0.0,0.0],
                "sensors": [
                    {
                        "color": sensor.color,
                        "vector": sensor.vector,
                        "value": 0.0
                    }
                    for sensor in self.photoresistors
                ]
            }
        else:
            data = {
                "light_vector": self.light_vector.tolist() if self.light_vector is not None else None,
                "sensors": [
                    {
                        "color": sensor.color,
                        "vector": sensor.vector,
                        "value": sensor.get_norm_value()
                    }
                    for sensor in self.photoresistors
                ]
            }
        logger.info("Sending light vector: %s", data['light_vector'])

        try:
            response = requests.post(
                config.plot_app['UPDATE_VECTOR_URL'],
                json=data,
                headers=config.plot_app['API_KEY']
            )
            response.raise_for_status()
            logger.info("Light vector successfully sent to plot app.")
        except requests.exceptions.RequestException as e:
            logger.error("An error occurred while sending data: %s", e)
