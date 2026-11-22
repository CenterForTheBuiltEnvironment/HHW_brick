"""
Tests for the pump DP setpoint tracking app (pump_flow_spd_vfd).

The metric tests use small synthetic data; the end-to-end test runs only when the building 87
Brick model and timeseries fixtures are present.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from hhw_brick.applications.pump_flow_spd_vfd import app

FIXTURES = Path(__file__).parent / "fixtures"
TTL_87 = FIXTURES / "Brick_Model_File" / "building_87_district_steam_k.ttl"
CSV_87 = FIXTURES / "TimeSeriesData" / "87hhw_system_and_ancilliary_data.csv"


def _frame(dp, dp_stpt, **extra):
    idx = pd.date_range("2020-01-01", periods=len(dp), freq="15min")
    return pd.DataFrame(
        {"dp": dp, "dp_stpt": dp_stpt, "flow": np.linspace(1, 10, len(dp)), **extra}, index=idx
    )


class TestTrackingMetrics:
    def test_two_sided_classes(self):
        df = app.classify_tracking(_frame([80, 89, 91, 100, 109, 111], [100] * 6), threshold=0.10)
        assert df["cls"].tolist() == ["under", "under", "within", "within", "within", "over"]
        assert df["meet_flag"].sum() == 3
        assert df["err_rel"].iloc[0] == pytest.approx(-0.2)

    def test_operating_modes_two_pumps(self):
        df = _frame([100] * 4, [100] * 4, pmp1_spd=[0.5, 0, 0.6, 0], pmp2_spd=[0, 0.5, 0.6, np.nan])
        assert app.add_operating_mode(df)["mode"].tolist() == ["P1 only", "P2 only", "both", "none"]

    def test_operating_modes_without_speed(self):
        assert (app.add_operating_mode(_frame([100] * 3, [100] * 3))["mode"] == "all").all()

    def test_summary_shares(self):
        df = _frame(
            [80, 100, 120, 100], [100] * 4, pmp1_spd=[0.5, 0.5, 0.6, 0.6], pmp2_spd=[0, 0, 0.6, 0.6]
        )
        summary = app.tracking_summary(app.add_operating_mode(app.classify_tracking(df, 0.10)))
        overall = summary.set_index("scope").loc["all points"]
        assert overall["point_count"] == 4
        assert overall["within_ratio"] == pytest.approx(0.5)
        assert overall["under_ratio"] == pytest.approx(0.25)
        assert overall["over_ratio"] == pytest.approx(0.25)
        assert set(summary["scope"]) == {"all points", "P1 only", "both"}

    def test_flow_bins_cover_all_points(self):
        df = app.classify_tracking(
            _frame(np.full(50, 100.0), np.full(50, 100.0), pmp1_spd=np.full(50, 0.97))
        )
        bins = app.meet_setpoint_percentage_flow(df, flow_bins=5)
        assert len(bins) == 5
        assert bins["point_count"].sum() == 50
        assert bins["pmp1_spd_95ratio"].dropna().eq(1.0).all()


class TestSetpointCharacteristics:
    def test_single_setpoint(self):
        metric = app.cal_stpt_relationship(_frame([100] * 40, [100] * 40))
        assert metric["setpoint_class"] == "single"
        assert metric["stable_setpoints_ratio"] == pytest.approx(1.0)
        assert np.isnan(metric["spearman_oat"])

    def test_dynamic_setpoint(self):
        stpt = [100] * 50 + list(range(101, 151))  # half the points on non-stable values
        metric = app.cal_stpt_relationship(_frame([100] * 100, stpt, oat=np.arange(100.0)))
        assert metric["setpoint_class"] == "dynamic"
        assert metric["stable_setpoints_list"] == [100]
        assert metric["spearman_oat"] == pytest.approx(1.0)

    def test_stepwise_setpoint(self):
        metric = app.cal_stpt_relationship(_frame([100] * 40, [100] * 20 + [120] * 20))
        assert metric["setpoint_class"] == "multiple stable (step)"


def test_preprocessing_keeps_rows_without_optional_values():
    df = _frame(np.full(40, 100.0), np.full(40, 100.0), oper=np.ones(40), pmp1_spd=np.nan)
    df.loc[df.index[0], "oper"] = 0
    cleaned = app._data_preprocessing(df, app.load_config())
    assert len(cleaned) == 39
    assert "pmp1_spd" in cleaned.columns


@pytest.mark.skipif(
    not (TTL_87.exists() and CSV_87.exists()), reason="Building 87 fixtures not available"
)
def test_analyze_building_87(tmp_path):
    qualified, result = app.qualify(str(TTL_87))
    assert qualified
    assert {"dp", "dp_stpt", "flow", "pmp1_spd", "pmp2_spd", "oper"}.issubset(result)

    config = app.load_config()
    config["output"]["output_dir"] = str(tmp_path)
    config["output"]["generate_plots"] = False
    results = app.analyze(str(TTL_87), str(CSV_87), config)
    summary = results["summary"].set_index("scope")
    assert summary.loc["all points", "point_count"] == 18600
    assert summary.loc["all points", "within_ratio"] == pytest.approx(0.707, abs=0.001)
    assert summary.loc["both", "point_count"] == 8237
    assert results["setpoint_class"] == "dynamic"
    assert (tmp_path / "pump_dp_tracking_summary.csv").exists()
