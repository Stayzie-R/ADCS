import config

class Photoresistor:
    def __init__(self, name, color, vector):
        """
            Initialize a Photoresistor object.

            Args:
                name (str): The code of the pin (e.g., 'AIN0').
                color (str): The color associated with the pin.
                vector (tuple): Tuple representing the direction vector.

            Attributes:
                self.name (str): The code of the pin (e.g., 'AIN0').
                self.channel (int): The numerical representation of the channel (extracted from the pin name).
                self.color (str): The color associated with the pin.
                self.vector (tuple): Tuple representing the direction vector.
                self.value_raw (int): The value_raw read from the sensor (default -1).
        """
        # Validate the pin name and vector
        PhotoresistorValidator.validate(name, vector)

        self.name = name
        self.color = color
        self.vector = vector
        self.value_raw = -1
        # Extract numerical channel from the pin name (e.g., 'AIN0' -> 0)
        self.channel = int(name[3:])

    def read_sensor_value(self):
        """
       Reads the sensor value_raw from the corresponding IIO file.

       Returns:
           float: The normalized sensor value_raw (0.0 to 1.0), or None if an error occurred.
        """
        adc_file = config.photoresistor["BBB_IIO_DEVICE_PATH"].format(channel=self.channel)
        try:
            with open(adc_file, "r") as f:
                adc_value = int(f.read().strip())
            self.value_raw = adc_value
            normalized_value = adc_value / 4095.0  # Normalize to a 0-1 range
            return normalized_value

        except FileNotFoundError:
            print(f"Error: ADC value_raw file for channel {self.channel} not found at {adc_file}.")
            return None
        except ValueError:
            print(f"Error: Invalid value_raw read from ADC file for channel {self.channel} at {adc_file}.")
            return None
        except Exception as e:
            print(f"Error: Unexpected error while reading ADC value_raw from channel {self.channel}: {e}")
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
                adc_value = int(f.read().strip())
            self.value_raw = adc_value
            return adc_value

        except FileNotFoundError:
            print(f"Error: ADC value_raw file for channel {self.channel} not found at {adc_file}.")
            return None
        except ValueError:
            print(f"Error: Invalid value_raw read from ADC file for channel {self.channel} at {adc_file}.")
            return None
        except Exception as e:
            print(f"Error: Unexpected error while reading ADC value_raw from channel {self.channel}: {e}")
            return None

    def get_norm_value(self):
        """
        Normalize the raw sensor value_raw to a range between 0 and 1.

        This method takes the raw value_raw from the sensor, which is assumed to
        be an integer between 0 and 4095 (inclusive), and normalizes it to
        a floating-point value_raw between 0.0 and 1.0.

        Returns:
            float: The normalized sensor value_raw, where 0 corresponds to the
            minimum reading (0) and 1 corresponds to the maximum reading (4095).
        """
        normalized_value = self.value_raw / 4095.0  # Normalize to a 0-1 range
        return normalized_value

class PhotoresistorValidator:
    """
    A utility class for validating Photoresistor channel names and vectors.

    This class ensures that the photoresistor channels and vectors are unique and valid
    before instantiation of Photoresistor objects.
    """

    _used_channels = set()
    _used_vectors = set()
    _allowed_names = config.photoresistor["ALLOWED_NAMES"]

    @classmethod
    def validate(cls, name, vector):
        """
            Validates the channel name and vector for uniqueness and correctness.

            Args:
                name (str): The channel name (e.g., 'AIN0').
                vector (tuple): The direction vector associated with the photoresistor.

            Raises:
                ValueError: If the channel name is invalid or already in use, or if the vector is already in use.
        """
        if name not in cls._allowed_names:
            raise ValueError(f"Invalid channel name: {name}")
        if name in cls._used_channels:
            raise ValueError(f"Channel {name} is already in use.")
        if vector in cls._used_vectors:
            raise ValueError(f"Vector {vector} is already in use.")

        cls._used_channels.add(name)
        cls._used_vectors.add(vector)


    @classmethod
    def unregister(cls, name, vector):
        """
            Unregister a photoresistor's channel and vector when it is no longer in use.

            Args:
                name (str): The channel name to unregister.
                vector (tuple): The vector to unregister.
        """
        cls._used_channels.discard(name)
        cls._used_vectors.discard(vector)