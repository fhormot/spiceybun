import pytest

from pathlib import Path

from spiceybun.measure_ngspice import Measure_ngspice

@pytest.fixture
def get_file_path():
        test_dir = Path(__file__).parent

        return test_dir

@pytest.fixture
def measure_ngspice():
        return Measure_ngspice()

def test_explicit(measure_ngspice):
        measure = 'measure tran delay1 TRIG v(out) VAL=0.5 RISE=1 TARG v(out) VAL=0.5 RISE=2'
        expected_measure = {
                "name": "delay1",
                "analysis": "tran",
                "measure": measure
        }

        assert measure_ngspice.explicit(measure) == measure
        assert measure_ngspice.get_all()[-1] == expected_measure

def test_process_measure(measure_ngspice, get_file_path):
        path = get_file_path / "rawfiles" / "meas_mc_20_samples_2_columns.raw"

        output = measure_ngspice.process_measure(path)

        assert not output.empty
        assert list(output.columns) == ['v_th_l2h', 'v_th_h2l']
        assert len(output) == 20

def test_process_measure_with_errors(measure_ngspice, get_file_path):
        path = get_file_path / "rawfiles" / "meas_mc_20_samples_2_columns_fails.raw"

        output = measure_ngspice.process_measure(path)

        assert not output.empty
        assert list(output.columns) == ['v_th_l2h', 'v_th_h2l']
        assert len(output) == 20