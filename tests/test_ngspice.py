import pytest

import os
from pathlib import Path

from spiceybun.ngspice import Ngspice

@pytest.fixture
def set_env_var():
    original_pdk = os.environ.get("PDK")
    original_pdk_root = os.environ.get("PDK_ROOT")
    original_spiceinit = os.environ.get("SPICEINIT")    

    top_dir = Path(__file__).parent.parent
    path_pdk = top_dir / "ng-libs"
    path_spiceinit = path_pdk / "ihp-sg13g2" / "libs.tech" / "ngspice" / ".spiceinit"
    os.environ["PDK"] = "ihp-sg13g2"
    os.environ["PDK_ROOT"] = str(path_pdk)
    os.environ["SPICEINIT"] = str(path_spiceinit)

    yield

    # Restore the original value
    if original_pdk is None:
        os.environ.pop("$PDK", None)
    else:
        os.environ["PDK"] = original_pdk

    if original_pdk_root is None:
        os.environ.pop("PDK_ROOT", None)
    else:
        os.environ["PDK_ROOT"] = original_pdk_root

    if original_spiceinit is None:
        os.environ.pop("SPICEINIT", None)
    else:
        os.environ["SPICEINIT"] = original_spiceinit

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

@pytest.fixture
def ngspice_no_variables_lib(set_env_var):
    test_dir = Path(__file__).parent

    path_netlist = test_dir / "netlists" / "input_subckt_lib_no_variables.spice"

    path = Path(__file__).parent
    path_output = path / "outputs" / "output_subckt_lib_no_variables"

    ngspice = Ngspice(path_netlist)
    ngspice.set_output_path(path_output)

    ngspice.add_spiceinit(os.environ.get("SPICEINIT"))
    path_library = "cornerMOSlv.lib" 
    ngspice.add_library(path_library, section='mos_tt')

    ngspice.add_transient(2e-3, t_step=1e-10, t_max=1e-7)

    ngspice.save_signal('V(v_out)')
    ngspice.save_signal('V(v_in)')

    ngspice.measure.explicit('meas tran v_th_l2h FIND V(v_in) WHEN V(v_out)=0.75 RISE=1')
    ngspice.measure.explicit('meas tran v_th_h2l FIND V(v_in) WHEN V(v_out)=0.75 FALL=1')

    ngspice.save_signal_all(False)

    return ngspice

def test_environment(set_env_var):
    print(f'$PDK: {os.environ.get("PDK")}')
    print(f'$PDK_ROOT: {os.environ.get("PDK_ROOT")}')

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

def test_run_no_variables_lib(ngspice_no_variables_lib):
    output = ngspice_no_variables_lib.run()
    assert output != ''