from sun_sensor import SunSensor


class ADCS:
    """
    Attitude Determination and Control System (ADCS) class.

    This class represents the system responsible for determining and controlling
    the attitude (orientation) of a satellite using sensors and control mechanisms.
    """

    def __init__(self):
        """
        Initialize the ADCS.

        This method initializes the ADCS by setting up the sensors.
        """
        self.sensors = {
            "sun_sensor": SunSensor()
        }
        self.acutators = {
         #   "autators"
        }

    def run(self):
        self.sensors["sun_sensor"].run()

if __name__ == "__main__":
    app = ADCS()
    app.run()