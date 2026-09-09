import pytest

from irrigation_scheduler.et import calculate_etc


def test_calculate_etc():
    assert calculate_etc(eto=5.0, kc=0.40) == pytest.approx(2.0)


def test_calculate_etc_at_mid_season():
    assert calculate_etc(eto=6.0, kc=1.15) == pytest.approx(6.9)


def test_calculate_etc_with_zero_eto():
    assert calculate_etc(eto=0.0, kc=1.15) == pytest.approx(0.0)


def test_calculate_etc_rejects_negative_eto():
    with pytest.raises(ValueError):
        calculate_etc(eto=-1.0, kc=1.0)


def test_calculate_etc_rejects_negative_kc():
    with pytest.raises(ValueError):
        calculate_etc(eto=5.0, kc=-0.1)