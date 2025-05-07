
import config
import logging

logger = logging.getLogger(__name__)


class Photoresistor:
    def __init__(self, name, color, vector):
        """
            Initialize a Photoresistor object.

            Args:
                name (str): The code of the pin (e.g., 'AIN0').
                color (str): The color associated with the pin.
                vector (tuple): Tuple representing the direction vector.

            Attributes:
                self.channel (int): The numerical representation of the channel (extracted from the pin name).
                self.color (str): The color associated with the pin.
                self.vector (tuple): Tuple representing the direction vector.
                self.voltage (float): Analog voltage converted from the raw ADC value, in volts (V).
                self.value (float): The normalized value read from the sensor (default -1).
        """
        # Validate the pin name and vector
        PhotoresistorValidator.validate(name, vector, color)

        self.color = color
        self.vector = vector
        self.value = -1
        self.value_voltage = -1
        # Extract numerical channel from the pin name (e.g., 'AIN0' -> 0)
        self.channel = int(name[3:])

    def read_sensor_value(self):
        """
        Reads the sensor value from the corresponding IIO file.

        Normalize the raw sensor value_raw to a range between 0 and 1.

        This method takes the raw value_raw from the sensor, which is assumed to
        be an integer between 0 and 4095 (inclusive), and normalizes it to
        a floating-point value_raw between 0.0 and 1.0.

        Returns:
           float: The normalized sensor value_raw (0.0 to 1.0), or None if an error occurred.
        """
        adc_file = config.photoresistor["BBB_IIO_DEVICE_PATH"].format(channel=self.channel)
        try:
            with open(adc_file, "r") as f:
                value_raw = int(f.read().strip())
            self.value = value_raw / 4095.0  # Normalize to a 0-1 range
            self.value_voltage = self.value * 1.8
            return self.value


        except FileNotFoundError:
            logger.error("ADC value file not found for channel %s at %s", self.channel, adc_file)
            return None
        except ValueError:
            logger.error("Invalid value read from ADC file for channel %s at %s", self.channel, adc_file)
            return None
        except Exception as e:
            logger.error("Unexpected error while reading ADC value from channel %s: %s", self.channel, e)
            return None

    def read_sensor_value_raw(self):
        """
        Reads the raw sensor value_raw from the corresponding IIO file.

        Returns:
            int: The raw sensor value_raw (0-4095), or None if an error occurred.
        """
        adc_file = config.photoresistor["adc_file_path"].format(channel=self.channel)
        try:
            with open(adc_file, "r") as f:
                value_raw = int(f.read().strip())
            return value_raw

        except FileNotFoundError:
            logger.error("ADC value file not found for channel %s at %s", self.channel, adc_file)
            return None
        except ValueError:
            logger.error("Invalid value read from ADC file for channel %s at %s", self.channel, adc_file)
            return None
        except Exception as e:
            logger.error("Unexpected error while reading ADC value from channel %s: %s", self.channel, e)
            return None

    def get_norm_value(self):
        """
        Returns:
            float: The normalized sensor value, where 0 corresponds to the
            minimum reading (0) and 1 corresponds to the maximum reading (4095).
        """

        return self.value

    def get_value_voltage(self):
        """
        Returns the analog voltage converted from the raw ADC value.

        Returns:
            float: Voltage in volts (V), typically in the range 0–1.8 V for BeagleBone Black ADC.
        """
        return self.value_voltage

class PhotoresistorValidator:
    """
    A utility class for validating Photoresistor channel names and vectors.

    This class ensures that the photoresistor channels and vectors are unique and valid
    before instantiation of Photoresistor objects.
    """

    _used_channels = set()
    _used_vectors = set()
    _used_collors = set()
    _allowed_names = config.photoresistor["ALLOWED_NAMES"]

    @classmethod
    def validate(cls, name, vector, color):
        """
            Validates the channel name and vector for uniqueness and correctness.

            Args:
                name (str): The channel name (e.g., 'AIN0').
                vector (tuple): The direction vector associated with the photoresistor.
                color (string): Color of the photoresitor side
            Raises:
                ValueError: If the channel name is invalid or already in use, or if the vector is already in use.
        """
        if name not in cls._allowed_names:
            raise ValueError("Invalid channel name: ,",name)
        if name in cls._used_channels:
            raise ValueError("Channel ",vector," is already in use.")
        if vector in cls._used_vectors:
            raise ValueError("Vector ",vector," is already in use.")
        if color in cls._used_collors:
            raise ValueError("Color ",vector," is already in use.")

        cls._used_channels.add(name)
        cls._used_vectors.add(vector)
        if color:
            cls._used_collors.add(color)


    @classmethod
    def unregister(cls, name, vector, color):
        """
            Unregister a photoresistor's channel and vector when it is no longer in use.

            Args:
                name (str): The channel name to unregister.
                vector (tuple): The vector to unregister.
                color (string): The color to unregister.
        """
        cls._used_channels.discard(name)
        cls._used_vectors.discard(vector)
        cls._used_collors.discard(color)
