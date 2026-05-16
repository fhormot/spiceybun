import subprocess
import os
import numpy as np
from pathlib import Path

class Ngspice:
        def __init__(self, path_netlist, **kwargs):
                self._netlist = []

                self._analysis = []
                self._plots = []

                self._path_netlist = path_netlist
                self._include(path_netlist)

                self._output_path = Path(__file__).parent

        def _read_dut_nelist(self) -> None:
                with open(self._path_netlist, 'r') as f:
                        self._netlist_dut = f.readlines()

        def _include(self, path, **kwargs) -> str:
                # str = f'.include "{path}"'
                str = f'.include {path}'

                if 'section' in kwargs:
                        str = str + ' ' + kwargs['section']

                self._netlist.append(str)

                return str
        
        def set_output_path(self, path) -> None:
                self._output_path = path

        def _write_netlist(self) -> None:
                self._add_control()

                self._netlist.append('.end')

                output_netlist = os.path.join(self._output_path, 'tb_test.spice')

                with open(output_netlist, 'w') as f:
                        f.write('\n'.join(self._netlist))

                return output_netlist

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

        def _add_control(self) -> str:
                control_statement = []

                control_statement.append('\n.control')

                #TODO: Fix hardcode
                control_statement.append('\tsave all')

                control_statement.append('\top')

                # Append analysis
                for element in self._analysis:
                        control_statement.append(f'\t{element}')

                output_path = os.path.join(self._output_path, 'output.raw')
                control_statement.append('\n\tset wr_vecnames')
                control_statement.append('\tset wr_singlescale')
                control_statement.append(f'\twrdata {output_path} V(v_in)')

                control_statement.append('\n\texit')
                control_statement.append('.endc\n')

                self._netlist.extend(control_statement)

                return control_statement

        def run(self) -> str:
                path_output_netlist = self._write_netlist()

                command_format = "ngspice -i -o {output_path} {input_path} -a || sh"

                output_path = os.path.join(self._output_path, 'output.log')
                run_path = os.path.join(self._output_path, 'run.log')
                raw_path = os.path.join(self._output_path, 'output.raw')
                input_path = path_output_netlist

                netlist_command = command_format.format(
                        output_path=output_path, 
                        raw_path=raw_path,
                        input_path=input_path
                        )

                print(netlist_command)

                output = subprocess.run(
                        netlist_command, 
                        # env=self.env, 
                        shell=True, 
                        capture_output=True, 
                        text=True
                )

                with open(run_path, 'w') as f:
                        f.write(output.stdout)

                return output

