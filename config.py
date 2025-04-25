photoresistor = dict(
    ALLOWED_NAMES = ["AIN0", "AIN1", "AIN2", "AIN3", "AIN4", "AIN5", "AIN6"],
    BBB_IIO_DEVICE_PATH =  "/sys/bus/iio/devices/iio:device0/in_voltage{channel}_raw",
)

sun_sensor = dict(
    READ_INTERVAL = 1,
    PRINT_RESULT = True,
    SENSORS = [

        dict(pin_key="AIN0", color="orange", vector=(0, 0, 1)),
        dict(pin_key="AIN1", color="white", vector=(1, 0, 0)),
        dict(pin_key="AIN2", color="green", vector=(0, -1, 0)),
        dict(pin_key="AIN3", color="yellow", vector=(0, 1, 0)),
        dict(pin_key="AIN5", color="brown", vector=(-1, 0, 0)),
    ]
)

