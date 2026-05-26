import pytest
from pathlib import Path

from spiceybun.ngspice import Ngspice
from pprint import pprint

@pytest.fixture
def ngspice_basic():
    test_dir = Path(__file__).parent

    path_netlist = test_dir / "netlists" / "input_flat_variables.spice"

    return Ngspice(path_netlist)

@pytest.fixture
def ngspice_no_variables():
    test_dir = Path(__file__).parent

    path_netlist = test_dir / "netlists" / "input_flat_no_variables.spice"

    path = Path(__file__).parent
    path_output = path / "outputs" / "output_flat_variables"

    ngspice = Ngspice(path_netlist)
    ngspice.set_output_path(path_output)

    ngspice.add_transient(500e-9, t_step=10e-12)

    ngspice.save_signal_all(False)

    ngspice.save_signal('V(v_out)')
    ngspice.save_signal('V(v_in)')

    ngspice.set_variable('v_vdd', '1.5')
    ngspice.set_variable('t_edge', '500e-12')
    ngspice.set_variable('c_load', '1e-15')

    ngspice.measure.explicit('meas tran t_delay_l2h TRIG V(v_in) VAL=0.75 RISE=1 TARG V(v_out) VAL=0.75 RISE=1')
    ngspice.measure.explicit('meas tran t_delay_h2l TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=0.75 FALL=1')
    ngspice.measure.explicit('meas tran t_fail TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=1.75 FALL=1')

    return ngspice

@pytest.fixture
def ngspice():
    test_dir = Path(__file__).parent

    path_netlist = test_dir / "netlists" / "input_flat_variables.spice"

    path = Path(__file__).parent
    path_output = path / "outputs" / "output_flat_variables"

    ngspice = Ngspice(path_netlist)
    ngspice.set_output_path(path_output)

    ngspice.add_transient(500e-9, t_step=10e-12)

    ngspice.save_signal_all(False)

    ngspice.save_signal('V(v_out)')
    ngspice.save_signal('V(v_in)')

    ngspice.set_variable('v_vdd', '1.5')
    ngspice.set_variable('t_edge', '500e-12')
    ngspice.set_variable('c_load', '1e-15')

    ngspice.measure.explicit('meas tran t_delay_l2h TRIG V(v_in) VAL=0.75 RISE=1 TARG V(v_out) VAL=0.75 RISE=1')
    ngspice.measure.explicit('meas tran t_delay_h2l TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=0.75 FALL=1')
    ngspice.measure.explicit('meas tran t_fail TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=1.75 FALL=1')

    return ngspice

def test_include(ngspice_basic):
    path = 'foo.sp'
    expected_include = f'.include {path}'

    assert ngspice_basic._include(path) == expected_include
    assert ngspice_basic._netlist[-1] == expected_include

def test_read_dut_netlist(ngspice_basic):
    ngspice_basic._read_dut_nelist()

    assert len(ngspice_basic._netlist_dut) > 0

    variables = ngspice_basic.get_variables()

    assert len(variables) == 3

def test_set_output_path(ngspice_basic):
    path_new = Path(__file__).parent

    path_old = ngspice_basic._output_path

    ngspice_basic.set_output_path(path_new)

    assert ngspice_basic._output_path == path_new
    assert ngspice_basic._output_path != path_old

def test_write_netlist(ngspice_basic):
    t_step = '1e-11'
    t_stop =' 500e-9'
    t_start = '0'
    t_max = '100e-12'

    statement = ngspice_basic.add_transient(t_stop, t_step=t_step)
    assert len(ngspice_basic._analysis) == 1

    # Test that every call overwrites the previous transient statement
    t_stop =' 500e-9'

    statement = ngspice_basic.add_transient(t_stop, t_step=t_step, t_start=t_start, t_max=t_max)
    assert len(ngspice_basic._analysis) == 1

    assert statement == f'tran {t_step} {t_stop} {t_start} {t_max}'

    ngspice_basic._write_netlist()

def test_run_single_no_variables(ngspice_no_variables):
    output = ngspice_no_variables.run()
    assert output != ''

def test_run_single_variables(ngspice):
    output = ngspice.run()
    assert output != ''

def test_run_mc(ngspice):
    output = ngspice.run(mc=True, mc_runs=2)
    assert output != ''

def test_run_sweep(ngspice):
    ngspice.set_variable('v_vdd', ['1.35', '1.65'])

    output = ngspice.run()

    assert type(output) is list

    for output_single in output:
        assert output_single != ''