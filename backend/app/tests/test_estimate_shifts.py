import pytest

from app.repositories import history, shifts_repo
from app.services import estimate_service

# Seeded: room 1 客餐厅 6x4.5, tile 1 600x600 -> raw 75
# default waste 8%; seeded 夜班 22:00-06:00 +5%, active


def test_daytime_uses_base_only():
    r = estimate_service.run_estimate(1, 1, None, False, "", work_time=12.0)
    assert r["base_waste_pct"] == 8.0
    assert r["surcharge_pct"] == 0.0
    assert r["shift_name"] is None
    assert r["waste_pct"] == 8.0
    assert r["order_count"] == 81  # ceil(75 * 1.08)


def test_night_hit_adds_surcharge():
    r = estimate_service.run_estimate(1, 1, None, False, "", work_time=23.0)
    assert r["shift_name"] == "夜班"
    assert r["surcharge_pct"] == 5.0
    assert r["waste_pct"] == 13.0  # base 8 + night 5
    assert r["order_count"] == 85  # ceil(75 * 1.13)


def test_wrapping_window_after_midnight():
    r = estimate_service.run_estimate(1, 1, None, False, "", work_time=2.0)
    assert r["surcharge_pct"] == 5.0
    # boundary: end hour 06:00 is excluded, start 22:00 included
    assert estimate_service.run_estimate(1, 1, None, False, "", 6.0)["surcharge_pct"] == 0.0
    assert estimate_service.run_estimate(1, 1, None, False, "", 22.0)["surcharge_pct"] == 5.0


def test_disabled_shift_no_surcharge():
    shift = shifts_repo.list_shifts()[0]
    shifts_repo.update_shift(shift["id"], {"active": False})
    r = estimate_service.run_estimate(1, 1, None, False, "", work_time=23.0)
    assert r["surcharge_pct"] == 0.0
    assert r["waste_pct"] == 8.0


def test_no_work_time_means_no_surcharge():
    r = estimate_service.run_estimate(1, 1, None, False, "")
    assert r["surcharge_pct"] == 0.0
    assert r["work_time"] is None


def test_run_freezes_total_waste_and_clock_time():
    r = estimate_service.run_estimate(1, 1, None, True, "夜班单", work_time=23.0)
    run_id = r["run_id"]
    assert run_id is not None

    # later rule changes must not recompute the stored run
    shift = shifts_repo.list_shifts()[0]
    shifts_repo.update_shift(shift["id"], {"surcharge_pct": 10.0})

    run = history.get_run(run_id)
    assert run["waste_pct"] == 13.0          # total actually applied
    assert run["base_waste_pct"] == 8.0
    assert run["surcharge_pct"] == 5.0
    assert run["work_time"] == 23.0
    assert run["shift_name"] == "夜班"
    assert run["result"]["order_count"] == 85


def test_disabling_shift_after_run_keeps_old_run():
    r = estimate_service.run_estimate(1, 1, None, True, "", work_time=23.0)
    run_id = r["run_id"]
    shift = shifts_repo.list_shifts()[0]
    shifts_repo.update_shift(shift["id"], {"active": False})

    run = history.get_run(run_id)
    assert run["waste_pct"] == 13.0
    assert run["result"]["order_count"] == 85
    # new estimates no longer carry the surcharge
    assert estimate_service.run_estimate(1, 1, None, False, "", 23.0)["waste_pct"] == 8.0


def test_negative_surcharge_rejected():
    with pytest.raises(ValueError):
        shifts_repo.create_shift("负加耗", 0.0, 4.0, -1.0)


def test_illegal_window_rejected():
    with pytest.raises(ValueError):
        shifts_repo.create_shift("坏窗", 22.0, 22.0, 3.0)
    shift = shifts_repo.create_shift("可改", 1.0, 5.0, 3.0)
    with pytest.raises(ValueError):
        shifts_repo.update_shift(shift["id"], {"end_hour": 1.0})
