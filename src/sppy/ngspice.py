import subprocess
import os
import numpy as np
from pathlib import Path

from sppy.measure_ngspice import Measure_ngspice

class Ngspice:
        def __init__(self, path_netlist, **kwargs):
                self._netlist = []

                self._analysis = []
                self._plots = []
                self._plot_all = False

                self._path_netlist = path_netlist

                self._output_path = Path(__file__).parent

                self.measure = Measure_ngspice()

        def _read_dut_nelist(self) -> None:
                with open(self._path_netlist, 'r') as f:
                        self._netlist_dut = f.readlines()

                # TODO: Strip existing control statements

                # TODO: Extract variables

        def _include(self, path, **kwargs) -> str:
                # str = f'.include "{path}"'
                str = f'.include {path}'

                if 'section' in kwargs:
                        str = str + ' ' + kwargs['section']

                self._netlist.append(str)

                return str

        def _write_netlist_dut(self) -> str:
                self._read_dut_nelist()

                output_netlist = os.path.join(self._output_path, 'netlist.spice')

                with open(output_netlist, 'w') as f:
                        f.writelines(self._netlist_dut)
                os.chmod(output_netlist, 0o755)

                return output_netlist

        def _write_netlist(self) -> str:
                self._add_control()

                self._netlist.append('.end')

                output_netlist = os.path.join(self._output_path, 'tb_test.spice')

                with open(output_netlist, 'w') as f:
                        f.write('\n'.join(self._netlist))
                os.chmod(output_netlist, 0o755)

                self._netlist_output = output_netlist

                return output_netlist
        
        def _write_run_command(self) -> str:
                path_output_netlist = self._netlist_output

                command_format = "#!/bin/bash\nngspice -i -o {output_path} {input_path} -a || sh"

                command_path = os.path.join(self._output_path, 'run_command')
                output_path = os.path.join(self._output_path, 'output.log')
                input_path = path_output_netlist

                netlist_command = command_format.format(
                        output_path=output_path, 
                        input_path=input_path
                        )
                
                with open(command_path, 'w') as f:
                        f.write(netlist_command)
                os.chmod(command_path, 0o755)

                return command_path

        def _add_control(self) -> str:
                control_statement = []

                control_statement.append('\n.control')

                # Section
                # Append analysis
                for element in self._analysis:
                        control_statement.append(f'\t{element}')

                        suffix = element.split()[0]

                # Section
                # Save statements
                # TODO: Wrap measurements and save statments with their respective analysis
                output_path = os.path.join(self._output_path, 'output.raw')

                # Keep vector names in the header
                control_statement.append('\n\tset wr_vecnames')
                
                # Use a single scale (column) for all signals
                control_statement.append('\tset wr_singlescale')

                if not self._plot_all:
                        control_statement.append(f'\twrdata {output_path} {' '.join(self._plots)}')
                else:
                        control_statement.append('\tsave all')
                        control_statement.append(f'\twrdata {output_path} all')

                # Section
                # Apply ngspice measurements
                # control_statement.append('\tmeas tran t_delay_l2h TRIG V(v_in) VAL=0.75 RISE=1 TARG V(v_out) VAL=0.75 RISE=1')
                # control_statement.append('\tset filetype=ascii')
                # control_statement.append('\tset nopadding')
                # control_statement.append(f'\twrdata {os.path.join(self._output_path, "measurement.raw")} m_t_delay_l2h')

                control_statement.append('\n\t* Measurements')

                measurements = self.measure.get_all()
                for measure in measurements:
                        control_statement.append(f'\t{measure["measure"]}')

                if len(measurements) > 0:
                        control_statement.append('\n\tset filetype=ascii')
                        control_statement.append('\tset nopadding')

                        meas_string_list = ' '.join([measure['name'] for measure in measurements])

                        control_statement.append(f'\twrdata {os.path.join(self._output_path, "measurement.raw")} {meas_string_list}')

                measurements = self.measure.get_all()
                        
                control_statement.append('\n\texit')
                control_statement.append('.endc\n')

                self._netlist.extend(control_statement)
                return control_statement

        def add_transient(self, t_stop, **kwargs) -> str:

                # TODO: Calculate suggested/maximum steps
                # Step 1: calculate based on stop time --> Bad for long sims with sharp transients
                # Step 2: Find/assume fastest signal in netlist and adjust t_step accordingly
                # --> Not accounting for fast digital signals 
                # TODO: Define transient statement using variables
                t_step = kwargs.get('t_step', 1e-9)
                t_start = kwargs.get('t_start', '0')
                t_max = kwargs.get('t_max', t_step*10)

                transient_statement = f'tran {t_step} {t_stop} {t_start} {t_max}'

                self._analysis.append(transient_statement)

                return transient_statement

        def save_signal(self, signals) -> list:
                #TODO: Check if valid net/port
                if type(signals) is list:
                        self._plots.extend(signals)
                else:
                        self._plots.append(signals)

                return self._plots

        def save_signal_all(self, flag) -> bool:
                self._plot_all = flag

                return self._plot_all

        def set_output_path(self, path) -> None:
                self._output_path = path

        def run(self) -> str:
                # Verify the output folder exists
                if not os.path.exists(self._output_path):
                        os.makedirs(self._output_path)

                path_input_netlist = self._write_netlist_dut()

                self._include(path_input_netlist)
                path_output_netlist = self._write_netlist()

                command_path = self._write_run_command()

                output = subprocess.run(
                        command_path, 
                        # env=self.env, 
                        shell=True, 
                        capture_output=True, 
                        text=True
                )

                run_path = os.path.join(self._output_path, 'run.log')

                with open(run_path, 'w') as f:
                        f.write(output.stdout)
                os.chmod(command_path, 0o755)

                self.measure.process_measure(os.path.join(self._output_path, 'measurement.raw'))

                return output
