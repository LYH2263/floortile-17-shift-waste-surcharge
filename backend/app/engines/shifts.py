"""Night-shift surcharge: pure window math, no DB.

Times are "clock hours" on a 24h dial, stored as decimal hours (e.g. 22.5 = 22:30).
A window may wrap past midnight (start > end); such a window covers clock times
[start, 24) U [0, end]. start == end is an illegal window (zero width / ambiguous).
"""


def validate_window(start_hour: float, end_hour: float) -> str | None:
    """Return an error message if the clock window is illegal, else None."""
    for name, v in (("start_hour", start_hour), ("end_hour", end_hour)):
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            return f"{name} must be a number"
        if v < 0 or v >= 24:
            return f"{name} must be within [0, 24)"
    if float(start_hour) == float(end_hour):
        return "start_hour and end_hour must differ"
    return None


def in_window(clock_hour: float, start_hour: float, end_hour: float) -> bool:
    """Whether a clock hour falls in a possibly midnight-wrapping window.

    End is exclusive. In a wrapping window the hour 24/0 maps to 0.
    """
    t = float(clock_hour) % 24.0
    s, e = float(start_hour), float(end_hour)
    if s < e:
        return s <= t < e
    return t >= s or t < e
