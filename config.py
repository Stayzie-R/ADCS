"""
config.py

This file contains configuration settings for the Sun Sensor application.
It includes the configuration for photoresistors, sun sensor read intervals,
and settings for the plot app integration.

Attributes:
    photoresistor (dict): Configuration for photoresistor names and paths.
    sun_sensor (dict): Configuration for sun sensor read intervals, result printing, and sensor list.
    plot_app (dict): Configuration for plot app settings, including API endpoint and authorization key.
"""
import logging

# Configuration for photoresistors
photoresistor = dict(
    ALLOWED_NAMES = ["AIN0", "AIN1", "AIN2", "AIN3", "AIN4", "AIN5", "AIN6"],
    BBB_IIO_DEVICE_PATH =  "/sys/bus/iio/devices/iio:device0/in_voltage{channel}_raw",
)

# Configuration for the Sun Sensor application
sun_sensor = dict(
    READ_INTERVAL = 1,
    PRINT_RESULT = True,
    SENSORS = [
        dict(pin_key="AIN2", color="orange", vector=(0, 0, 1)),
        dict(pin_key="AIN0", color="white", vector=(1, 0, 0)),
        dict(pin_key="AIN1", color="green", vector=(0, -1, 0)),
        dict(pin_key="AIN5", color="yellow", vector=(0, 1, 0)),
        dict(pin_key="AIN3", color="brown", vector=(-1, 0, 0)),
    ]
)

# Configuration for the Plot App integration
plot_app = dict(
    PRINT_PLOT_APP = True,                                         # Whether to send data to the plot app
    UPDATE_VECTOR_URL = 'https://adcs-plot-app-5522ec11eb30.herokuapp.com/update_vector',
    API_KEY = {'Authorization': "ADCS"}                             # API key for authentication
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
