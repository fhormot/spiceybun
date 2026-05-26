import pytest

from spiceybun.measure_ngspice import Measure_ngspice

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