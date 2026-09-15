from typing import Sequence
import math
from app.models.solve import Solve, PenaltyType


def format_time(time_ms: int | None, penalty: str = "none") -> str:
    """
    Format milliseconds into WCA string representation.
    E.g.:
    - 8420 ms -> '8.42'
    - 68420 ms -> '1:08.42'
    - penalty == 'dnf' -> 'DNF'
    - penalty == '+2' -> '10.42+' (where time_ms already includes the +2000)
    """
    if penalty == PenaltyType.DNF.value or time_ms is None:
        return "DNF"

    total_seconds = time_ms / 1000.0
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60

    if minutes > 0:
        formatted = f"{minutes}:{seconds:05.2f}"
    else:
        formatted = f"{seconds:.2f}"

    if penalty == PenaltyType.PLUS_TWO.value:
        formatted += "+"

    return formatted


def calculate_average_trimmed(times_or_dnf: list[int | None]) -> int | None:
    """
    WCA Trimmed Average calculation (e.g., ao5, ao12, ao100).
    Rules:
    - Sort values. DNF is treated as positive infinity (greater than any number).
    - Trim top 5% and bottom 5% (rounded to nearest integer).
      * For N=5: trim 1 fastest, 1 slowest (sample size 3).
      * For N=12: trim 1 fastest, 1 slowest (sample size 10).
      * For N=100: trim 5 fastest, 5 slowest (sample size 90).
    - If there are more than `trim_count` DNFs in the sample, the average is DNF (returns None).
    - Returns the arithmetic mean of the remaining times rounded to the nearest integer ms.
    """
    n = len(times_or_dnf)
    if n < 3:
        return None

    # Official WCA trim count: ceil(n * 0.05)
    trim_count = math.ceil(n * 0.05)

    # Sort values: None (DNF) goes to the end
    valid_times = [t for t in times_or_dnf if t is not None]
    dnf_count = len(times_or_dnf) - len(valid_times)

    valid_times.sort()

    # If DNFs exceed the allowed trim count, the average is DNF
    if dnf_count > trim_count:
        return None

    # We discard `trim_count` fastest (from the front of valid_times)
    # And `trim_count` slowest (from the end: first taking DNFs, then slowest valid times)
    remaining_dnf_to_trim = min(dnf_count, trim_count)
    remaining_slow_to_trim = trim_count - remaining_dnf_to_trim

    # Discard fastest
    trimmed = valid_times[trim_count:]

    # Discard slowest valid times (if not enough DNFs swallowed the trim)
    if remaining_slow_to_trim > 0:
        trimmed = trimmed[:-remaining_slow_to_trim]

    if not trimmed:
        return None

    avg_ms = round(sum(trimmed) / len(trimmed))
    return avg_ms


def compute_wca_stats(solves: Sequence[Solve]) -> dict:
    """
    Computes all standard WCA statistics from a sequence of user's solves.
    Expected order: chronological (oldest to newest).
    """
    if not solves:
        return {
            "total_solves": 0,
            "pb": None,
            "pb_raw_ms": None,
            "ao5": None,
            "ao12": None,
            "ao100": None,
            "best_ao5": None,
            "best_ao12": None,
        }

    # Extract final times (None represents DNF)
    times = [s.final_time_ms for s in solves]

    # 1. PB Single
    valid_times = [t for t in times if t is not None]
    pb_ms = min(valid_times) if valid_times else None

    # 2. Current Averages (from the most recent N solves)
    current_ao5_ms = calculate_average_trimmed(times[-5:]) if len(times) >= 5 else None
    current_ao12_ms = calculate_average_trimmed(times[-12:]) if len(times) >= 12 else None
    current_ao100_ms = calculate_average_trimmed(times[-100:]) if len(times) >= 100 else None

    # 3. Best Averages across entire history
    best_ao5_ms = None
    if len(times) >= 5:
        for i in range(len(times) - 4):
            val = calculate_average_trimmed(times[i:i+5])
            if val is not None:
                if best_ao5_ms is None or val < best_ao5_ms:
                    best_ao5_ms = val

    best_ao12_ms = None
    if len(times) >= 12:
        for i in range(len(times) - 11):
            val = calculate_average_trimmed(times[i:i+12])
            if val is not None:
                if best_ao12_ms is None or val < best_ao12_ms:
                    best_ao12_ms = val

    return {
        "total_solves": len(solves),
        "pb": format_time(pb_ms) if pb_ms is not None else None,
        "pb_raw_ms": pb_ms,
        "ao5": "DNF" if (len(times) >= 5 and current_ao5_ms is None) else (format_time(current_ao5_ms) if current_ao5_ms else None),
        "ao12": "DNF" if (len(times) >= 12 and current_ao12_ms is None) else (format_time(current_ao12_ms) if current_ao12_ms else None),
        "ao100": "DNF" if (len(times) >= 100 and current_ao100_ms is None) else (format_time(current_ao100_ms) if current_ao100_ms else None),
        "best_ao5": format_time(best_ao5_ms) if best_ao5_ms is not None else None,
        "best_ao12": format_time(best_ao12_ms) if best_ao12_ms is not None else None,
    }
