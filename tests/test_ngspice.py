import pytest
from pathlib import Path

from sppy.ngspice import Ngspice
from pprint import pprint

@pytest.fixture
def ngspice_basic():
    test_dir = Path(__file__).parent

    path_netlist = test_dir / "netlists" / "input_flat_no_variables.spice"

    return Ngspice(path_netlist)

@pytest.fixture
def ngspice():
    test_dir = Path(__file__).parent

    path_netlist = test_dir / "netlists" / "input_flat_no_variables.spice"

    path = Path(__file__).parent
    path_output = path / "outputs" / "output_flat_no_variables"

    ngspice = Ngspice(path_netlist)
    ngspice.set_output_path(path_output)

    ngspice.save_signal_all(False)

    return ngspice

def test_include(ngspice_basic):
    path = 'foo.sp'
    expected_include = f'.include {path}'

    assert ngspice_basic._include(path) == expected_include
    assert ngspice_basic._netlist[-1] == expected_include

def test_read_dut_netlist(ngspice_basic):
    ngspice_basic._read_dut_nelist()

    assert len(ngspice_basic._netlist_dut) > 0

def test_set_output_path(ngspice_basic):
    path_new = Path(__file__).parent

    path_old = ngspice_basic._output_path

    ngspice_basic.set_output_path(path_new)

    assert ngspice_basic._output_path == path_new
    assert ngspice_basic._output_path != path_old

@pytest.mark.skip
def test_write_netlist(ngspice):
    t_stop = '10e-12'
    t_step =' 30e-9'
    t_start = '0'
    t_max = '100e-12'
    statement = ngspice.add_transient(30e-9, t_step=10e-12)

    assert statement == f'tran {t_step} {t_stop} {t_start} {t_max}'

    ngspice._write_netlist()

def test_run(ngspice):
    ngspice.add_transient(30e-9, t_step=10e-12)

    #TODO: Refactor test_write_netlist test here

    ngspice.save_signal('V(v_out)')
    ngspice.save_signal('V(v_in)')

    ngspice.measure.explicit('meas tran t_delay_l2h TRIG V(v_in) VAL=0.75 RISE=1 TARG V(v_out) VAL=0.75 RISE=1')
    ngspice.measure.explicit('meas tran t_delay_h2l TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=0.75 FALL=1')
    ngspice.measure.explicit('meas tran t_fail TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=1.75 FALL=1')

    output = ngspice.run()
    assert output.stderr == ''

def test_run_mc(ngspice):
    ngspice.add_transient(30e-9, t_step=10e-12)

    #TODO: Refactor test_write_netlist test here

    ngspice.save_signal('V(v_out)')
    ngspice.save_signal('V(v_in)')

    ngspice.measure.explicit('meas tran t_delay_l2h TRIG V(v_in) VAL=0.75 RISE=1 TARG V(v_out) VAL=0.75 RISE=1')
    ngspice.measure.explicit('meas tran t_delay_h2l TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=0.75 FALL=1')
    ngspice.measure.explicit('meas tran t_fail TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=1.75 FALL=1')

    output = ngspice.run(mc=True, mc_runs=2)
    assert output.stderr == ''