import numpy as np
import time
import logging
import argparse
import csv
import os

from sun_sensor import SunSensor  # Make sure this module is available

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_reference_vectors(step_deg: int = 5) -> dict:
    """
    Generate a dictionary of expected unit vectors for each angle step.

    Args:
        step_deg: Step size in degrees between measurements.

    Returns:
        Dictionary with structure:
            angle_deg -> {
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


def read_existing_csv(path: str) -> dict:
    """
    Read existing measurement results from a CSV file.

    Args:
        path: Path to the CSV file.

    Returns:
        Dictionary with existing data, same format as generate_reference_vectors.
    """
    if not os.path.exists(path):
        return {}

    logger.info("Loading existing results from %s", path)
    existing_data = {}
    with open(path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            angle = int(row['angle_deg'])
            expected = (float(row['x_expected']), float(row['y_expected']))
            measured = (
                float(row['x_measured']) if row['x_measured'] else None,
                float(row['y_measured']) if row['y_measured'] else None
            )
            error = float(row['error_deg']) if row['error_deg'] else None
            existing_data[angle] = {
                'expected': expected,
                'measured': measured if None not in measured else None,
                'error_deg': error
            }
    return existing_data


def measure_average_vector(sensor: SunSensor, count: int = 10, delay: float = 1.0) -> tuple:
    """
    Collect multiple sensor readings and return a normalized average vector.

    Args:
        sensor: Instance of SunSensor.
        count: Number of samples to average.
        delay: Delay between samples in seconds.

    Returns:
        Tuple (x, y) of normalized average vector.
    """
    samples = []
    for _ in range(count):
        try:
            sensor.read_sensors_value()
            sensor.calc_light_vector()
            sensor.print_sensors_value()

            #sensor.transmit_vec_to_plot_app(False)
            samples.append(sensor.light_vector)
            time.sleep(delay)
        except Exception:

            logger.exception("Error while reading light vector")

    if len(samples) < count:
        logger.warning("Expected %d samples, got %d", count, len(samples))
        return (float('nan'), float('nan'))

    arr = np.vstack(samples)
    avg = arr.mean(axis=0)
    norm = np.linalg.norm(avg)
    return tuple(avg / norm) if norm > 0 else tuple(avg)


def compute_angular_error(expected: tuple, measured: tuple) -> float:
    """
    Compute angular error in degrees between expected and measured vectors.

    Args:
        expected: Expected unit vector (x, y).
        measured: Measured unit vector (x, y).

    Returns:
        Angular difference in degrees.
    """

    measured = measured[:2]
    dot = np.dot(expected, measured)
    mag_exp = np.hypot(*expected)
    mag_meas = np.hypot(*measured)
    cos_theta = np.clip(dot / (mag_exp * mag_meas), -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_theta)))


def append_result_to_csv(path: str, angle: int, expected: tuple, measured: tuple, error: float) -> None:
    """
    Append a single measurement result to the CSV file.

    Args:
        path: Path to CSV.
        angle: Angle in degrees.
        expected: Expected vector.
        measured: Measured vector.
        error: Angular error.
    """
    file_exists = os.path.exists(path)
    with open(path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['angle_deg', 'x_expected', 'y_expected', 'x_measured', 'y_measured', 'error_deg'])
        writer.writerow([
            angle,
            round(expected[0], 3), round(expected[1], 3),
            round(measured[0], 3), round(measured[1], 3),
            round(error, 2)
        ])

    logger.info("Saved result for angle %d° to CSV", angle)


def perform_vector_measurement(data: dict, sensor: SunSensor, output_path: str) -> dict:
    """
    Loop through unmeasured angles, perform measurements, compute errors, and save results.

    Args:
        data: Dictionary containing expected vectors and any previously loaded data.
        sensor: Instance of SunSensor.
        output_path: Path to CSV output.

    Returns:
        Updated data dictionary with new measurements.
    """
    for angle in sorted(data.keys()):
        if data[angle]['measured'] is not None:
            logger.info("Angle %d° already measured. Skipping.", angle)
            continue

        logger.info("Prepare to measure angle %d°", angle)

        user_continue = input("Press ENTER when ready...")
        print(user_continue)
        measured_vec = measure_average_vector(sensor)
        error = compute_angular_error(data[angle]['expected'], measured_vec)

        logger.info(
            "Measured angle: " + str(angle) + "°, Error: " + str(round(error, 2)) + "°, \n"
            "Measured: (" + str(round(measured_vec[0], 3)) + ", " + str(round(measured_vec[1], 3)) + ")\n"
            "Expected: (" + str(round(data[angle]['expected'][0], 3)) + ", " + str(round(data[angle]['expected'][1], 3)) + ")\n"
        )

        data[angle]['measured'] = measured_vec
        data[angle]['error_deg'] = error
        append_result_to_csv(output_path, angle, data[angle]['expected'], measured_vec, error)




def main(step: int, output: str) -> None:
    """
    Main function to measure and log light vectors from a sun sensor.

    Args:
        step: Angle step in degrees for measurement (e.g., 30 means 0°, 30°, ..., 330°).
        output: Path to CSV file where results will be saved.
    """
    logger.info("Starting measurement routine with step %d°", step)
    reference_data = generate_reference_vectors(step)
    existing_data = read_existing_csv(output)
    reference_data.update(existing_data)  # Overwrite only previously recorded angles

    sensor = SunSensor()
    updated_data = perform_vector_measurement(reference_data, sensor, output)

    logger.info("All measurements complete. Results saved to %s", output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Measure light vectors using a sun sensor and compute angular errors.'
    )
    parser.add_argument('--step', type=int, default=10,
                        help='Angle step in degrees (e.g., 30 for 0°, 30°, ..., 330°)')
    parser.add_argument('--output', type=str, default='sun_sensor_results_3m.csv',
                        help='CSV file path for storing results')

    args = parser.parse_args()
    main(step=args.step, output=args.output)