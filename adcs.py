import threading
from sun_sensor import SunSensor

import logging

logger = logging.getLogger(__name__)

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
        self.stop_event = threading.Event()

        self.sensors = {
            "sun_sensor": SunSensor(stop_event=self.stop_event)
        }
        self.actuators = {
            # TODO: Add actuators (e.g., reaction wheels, magnetorquers)
        }

    def run(self):
        """
        Start the ADCS operation.

        This method starts the Attitude Determination System (ADS) and the Attitude
        Control System (ACS) in separate threads.
        """
        try:
            ads_thread = threading.Thread(target=self.attitude_determination_system)
            ads_thread.start()

            # acs_thread = threading.Thread(target=self.attitude_control_system)
            # acs_thread.start()

            ads_thread.join()
            #acs_thread.join()
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt – ending...")
            self.stop_event.set()

    def attitude_determination_system(self):
        """
        Attitude Determination System (ADS).

        This method runs the Attitude Determination System (ADS) which collects data
        from sensors to determine the orientation of the satellite.
        """

        def safe_run(sensor_name, sensor):
            try:
                sensor.run()
            except Exception as e:
                print(f"[ERROR] Sensor '{sensor_name}' failed: {e}")

        sensor_threads = {}
        for name, sensor in self.sensors.items():
            sensor_threads[name] = threading.Thread(target=safe_run, args=(name, sensor))
            sensor_threads[name].start()

        for t in sensor_threads.values():
            t.join()

    def attitude_control_system(self):
        """
        Attitude Control System (ACS).

        This method runs the Attitude Control System (ACS) which is responsible for
        controlling the orientation of the satellite based on the data obtained from
        the Attitude Determination System (ADS).
        """
        pass

if __name__ == "__main__":
    try:
        app = ADCS()
        app.run()
    except Exception as e:
        print(f"[FATAL ERROR] ADCS failed: {e}")