import numpy as np
import pandas as pd
import time
import logging
import argparse

from sun_sensor import SunSensor

logger = logging.getLogger(__name__)


def prepare_reference_dataframe(step_deg: int = 5) -> pd.DataFrame:
    """
    Create a reference DataFrame containing expected unit vectors for given angle steps.

    Args:
        step_deg: Step size in degrees between angles (default 5).

    Returns:
        DataFrame with columns:
          - angle_deg
          - x_expected
          - y_expected
          - x_measured (NaN placeholder)
          - y_measured (NaN placeholder)
    """
    angles = np.arange(0, 360, step_deg)
    radians = np.radians(angles)
    df = pd.DataFrame({
        'angle_deg': angles,
        'x_expected': np.cos(radians),
        'y_expected': np.sin(radians),
        'x_measured': np.nan,
        'y_measured': np.nan,
    })
    return df

def measure_light_vector(sensor: SunSensor, count: int = 10, delay: float = 1.0) -> np.ndarray:
    """
    Take multiple readings from SunSensor and return normalized average vector.

    Args:
        sensor: SunSensor instance (injected for testability).
        count: Number of readings to average.
        delay: Seconds to wait between readings.

    Returns:
        2-element array [x, y] of normalized average measurement,
        or [nan, nan] if readings failed.
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
        return np.array([np.nan, np.nan])
    arr = np.vstack(samples)
    avg = arr.mean(axis=0)
    norm = np.linalg.norm(avg)
    return avg / norm if norm > 0 else avg

def calc_light_vec(df: pd.DataFrame, sensor: SunSensor) -> pd.DataFrame:
    """
    Prompt user and perform light measurements for each unmeasured angle.

    Args:
        df: Reference DataFrame from prepare_reference_dataframe.
        sensor: SunSensor instance to read measurements.

    Returns:
        DataFrame with x_measured and y_measured filled in.
    """
    for idx, row in df.iterrows():
        if not np.isnan(row['x_measured']) and not np.isnan(row['y_measured']):
            logger.info("Angle %s° already measured; skipping.", row['angle_deg'])
            continue
        logger.info("Ready to measure angle %s°", row['angle_deg'])
        input("Press Enter when device is ready for measurement...")
        avg_vec = measure_light_vector(sensor)
        df.at[idx, 'x_measured'] = avg_vec[0]
        df.at[idx, 'y_measured'] = avg_vec[1]
    return df

def compute_error_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute angular error (degrees) between expected and measured unit vectors.

    Args:
        df: DataFrame with columns x_expected, y_expected, x_measured, y_measured.

    Returns:
        Same DataFrame with an added 'error_deg' column.

    Raises:
        ValueError: if any measured component is NaN.
    """
    if df[['x_measured', 'y_measured']].isna().any().any():
        raise ValueError("Missing measured vector components; cannot compute error.")
    dot = (df['x_expected'] * df['x_measured'] +
           df['y_expected'] * df['y_measured'])
    mag_exp = np.hypot(df['x_expected'], df['y_expected'])
    mag_meas = np.hypot(df['x_measured'], df['y_measured'])
    cos_t = np.clip(dot / (mag_exp * mag_meas), -1.0, 1.0)
    df['error_deg'] = np.degrees(np.arccos(cos_t))
    return df

def export_to_excel(df: pd.DataFrame, path: str, sheet: str = 'Measurements', include_index: bool = False) -> None:
    """
    Export DataFrame to an Excel file.

    Args:
        df: DataFrame to export.
        path: File path for .xlsx output.
        sheet: Worksheet name (default 'Measurements').
        include_index: Write row indices if True.
    """
    df.to_excel(path, sheet_name=sheet, index=include_index)
    logger.info("Exported results to Excel: %s (sheet: %s)", path, sheet)


def main(
    step: int,
    output: str,
    no_prompt: bool
) -> None:
    """
    Main entry point: generate reference table, measure, compute error, and export.

    Args:
        step: Degree increment between angles.
        output: Path to output Excel file.
        no_prompt: If True, skip all user prompts and measure immediately.
    """
    df = prepare_reference_dataframe(step)
    sensor = SunSensor()

    df = calc_light_vec(df, sensor)
    df = compute_error_rate(df)
    export_to_excel(df, output)


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