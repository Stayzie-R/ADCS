import numpy as np
import time
import logging
import argparse
import csv

from sun_sensor import SunSensor  # Ensure this module is available

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def prepare_reference_data(step_deg: int = 5) -> dict:
    """
    Create a reference dictionary containing expected unit vectors for each angle step.

    Args:
        step_deg: Step size in degrees between angles (default is 5).

    Returns:
        Dictionary with angle_deg as key and value as:
        {
            'expected': (x_expected, y_expected),
            'measured': None,
            'error_deg': None
        }
    """
    data = {}
    for angle in range(0, 360, step_deg):
        rad = np.radians(angle)
        expected = (np.cos(rad), np.sin(rad))
        data[angle] = {'expected': expected, 'measured': None, 'error_deg': None}
    return data


def measure_light_vector(sensor: SunSensor, count: int = 10, delay: float = 1.0) -> tuple:
    """
    Take multiple readings from the SunSensor and return normalized average vector.

    Args:
        sensor: SunSensor instance.
        count: Number of readings to average.
        delay: Seconds to wait between readings.

    Returns:
        Tuple (x, y) of normalized average measurement, or (nan, nan) on failure.
    """
    samples = []
    for _ in range(count):
        try:
            sensor.read_sensors_value()
            sensor.calc_light_vector()
            samples.append(sensor.light_vector)
            time.sleep(delay)
        except Exception:
            logger.exception("Error reading light vector from sensor")

    if len(samples) < count:
        logger.warning("Expected %d samples but got %d", count, len(samples))
        return (float('nan'), float('nan'))

    arr = np.vstack(samples)
    avg = arr.mean(axis=0)
    norm = np.linalg.norm(avg)
    return tuple(avg / norm) if norm > 0 else tuple(avg)


def calc_light_vec(data: dict, sensor: SunSensor) -> dict:
    """
    Prompt user to perform light measurements for each unmeasured angle.

    Args:
        data: Reference dictionary created by prepare_reference_data().
        sensor: SunSensor instance.

    Returns:
        Updated dictionary with measured values.
    """
    for angle, vectors in data.items():
        if vectors['measured'] is not None:
            logger.info("Angle %s° already measured; skipping.", angle)
            continue
        logger.info("Ready to measure angle %s°", angle)
        input("Press Enter when device is ready for measurement...")
        avg_vec = measure_light_vector(sensor)
        vectors['measured'] = avg_vec
    return data


def compute_error_rate(data: dict) -> dict:
    """
    Compute angular error in degrees between expected and measured unit vectors.

    Args:
        data: Dictionary with expected and measured vectors.

    Returns:
        Same dictionary with 'error_deg' added for each angle.

    Raises:
        ValueError: If any measured value is missing.
    """
    for angle, vectors in data.items():
        if vectors['measured'] is None:
            raise ValueError(f"Missing measurement for angle {angle}")

        x_exp, y_exp = vectors['expected']
        x_meas, y_meas = vectors['measured']
        dot = x_exp * x_meas + y_exp * y_meas
        mag_exp = np.hypot(x_exp, y_exp)
        mag_meas = np.hypot(x_meas, y_meas)
        cos_t = np.clip(dot / (mag_exp * mag_meas), -1.0, 1.0)
        vectors['error_deg'] = float(np.degrees(np.arccos(cos_t)))
    return data

def export_to_csv(data: dict, path: str) -> None:
    """
    Export results to a CSV file.

    Args:
        data: Dictionary with angle data.
        path: File path for the .csv output.
    """
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Header row
        writer.writerow(['angle_deg', 'x_expected', 'y_expected', 'x_measured', 'y_measured', 'error_deg'])

        for angle in sorted(data.keys()):
            expected = data[angle]['expected']
            measured = data[angle]['measured'] or (None, None)
            error = data[angle]['error_deg']
            writer.writerow([
                angle,
                expected[0], expected[1],
                measured[0], measured[1],
                error
            ])

    logger.info("Exported results to CSV: %s", path)




def main(step: int, output: str) -> None:
    """
    Main routine: prepare reference vectors, perform measurements, compute error, export results.

    Args:
        step: Angle increment in degrees.
        output: Output file path for Excel export.
    """
    data = prepare_reference_data(step)
    sensor = SunSensor()

    data = calc_light_vec(data, sensor)
    data = compute_error_rate(data)
    export_to_csv(data, output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Measure sun sensor light vectors and compute error rates.'
    )
    parser.add_argument('--step', type=int, default=30,
                        help='Angle step in degrees')
    parser.add_argument('--output', type=str, default='sun_sensor_results.xlsx',
                        help='Output Excel file path')

    args = parser.parse_args()
    main(step=args.step, output=args.output)
