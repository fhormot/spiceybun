import pytest
from pathlib import Path

from sppy.ngspice import Ngspice
from pprint import pprint

@pytest.fixture
def ngspice():
    test_dir = Path(__file__).parent

    path_netlist = test_dir / "netlists" / "input_flat_no_variables.spice"

    return Ngspice(path_netlist)

def test_include(ngspice):
    path = 'foo.sp'
    expected_include = f'.include "{path}"'

    assert ngspice._include(path) == expected_include
    assert ngspice._netlist[-1] == expected_include

def test_read_dut_netlist(ngspice):
    ngspice._read_dut_nelist()

    assert len(ngspice._netlist) > 0

def test_set_output_path(ngspice):
    path_new = Path(__file__).parent

    path_old = ngspice._output_path

    ngspice.set_output_path(path_new)

    assert ngspice._output_path == path_new
    assert ngspice._output_path != path_old

def test_write_netlist(ngspice):
    path = Path(__file__).parent
    path_output = path / "outputs"

    ngspice.set_output_path(path_output)

    t_stop = '10e-12'
    t_step =' 30e-9'
    t_start = '0'
    t_max = '100e-12'
    statement = ngspice.add_transient(30e-9, t_step=10e-12)

    assert statement == f'tran {t_step} {t_stop} {t_start} {t_max}'

    ngspice._write_netlist()

def test_run(ngspice):
    path = Path(__file__).parent
    path_output = path / "outputs"

    ngspice.set_output_path(path_output)
    ngspice.add_transient(30e-9, t_step=10e-12)

    output = ngspice.run()

    assert output.stderr == ''