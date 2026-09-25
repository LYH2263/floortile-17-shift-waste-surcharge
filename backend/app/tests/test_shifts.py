from app.engines.shifts import in_window, validate_window


def test_plain_window():
    assert in_window(8.0, 8.0, 18.0)
    assert in_window(17.99, 8.0, 18.0)
    assert not in_window(18.0, 8.0, 18.0)  # end exclusive
    assert not in_window(7.5, 8.0, 18.0)


def test_wrapping_window_past_midnight():
    # 22:00 - 06:00 night shift
    assert in_window(22.0, 22.0, 6.0)
    assert in_window(2.0, 22.0, 6.0)
    assert in_window(5.99, 22.0, 6.0)
    assert not in_window(6.0, 22.0, 6.0)  # end exclusive
    assert not in_window(12.0, 22.0, 6.0)
    assert not in_window(21.59, 22.0, 6.0)


def test_validate_window():
    assert validate_window(22.0, 6.0) is None
    assert validate_window(6.0, 22.0) is None
    assert validate_window(22.0, 22.0) is not None
    assert validate_window(-1.0, 6.0) is not None
    assert validate_window(24.0, 6.0) is not None
