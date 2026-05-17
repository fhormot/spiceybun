import subprocess
import os
import pandas as pd
from pathlib import Path

from spipy.measure_ngspice import Measure_ngspice

class Ngspice:
        def __init__(self, path_netlist, **kwargs):
                self._netlist = []

                self._analysis = []
                self._plots = []

                # Control statements
                self._plot_all          = False

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

        def _write_netlist(self, **kwargs) -> str:
                self._add_control(**kwargs)

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

        def _add_control(self, **kwargs) -> str:
                # Kwargs
                mc = kwargs.get('mc', False)

                if mc:
                        seed = kwargs.get('seed', 1)
                        mc_runs = kwargs.get('mc_runs', 350)

                control_statement = []

                control_statement.append('\n.control')
                # Section
                # Measurement file preparation
                measurements = self.measure.get_all()
                if len(measurements)>0:
                        control_statement.append('\t*Prepare measurement output file with a header')

                        for measure in measurements:
                                control_statement.append(f'\techo "{measure["name"]}" > {os.path.join(self._output_path, "results", f"meas_{measure["name"]}.raw")}')

                # Section Monte Carlo
                if mc:
                        control_statement.append('\n\t* Monte Carlo analysis')
                        control_statement.append('\tsetseed {seed}')
                        control_statement.append('\tlet mc_runs={mc_runs}')
                        control_statement.append('\tlet mc_index=0')

                        control_statement.append('\n\twhile mc_index < mc_runs')

                # Section
                # Append analysis
                for element in self._analysis:
                        control_statement.append(f'\t\t{element}')

                        suffix = element.split()[0]

                # Section
                # Save statements
                # TODO: Wrap measurements and save statments with their respective analysis
                output_path = os.path.join(self._output_path, 'output.raw')

                # Keep vector names in the header
                control_statement.append('\n\t\tset wr_vecnames')
                
                # Use a single scale (column) for all signals
                control_statement.append('\t\tset wr_singlescale')

                if not self._plot_all:
                        control_statement.append(f'\t\twrdata {output_path} {' '.join(self._plots)}')
                else:
                        control_statement.append('\t\tsave all')
                        control_statement.append(f'\t\twrdata {output_path} all')

                control_statement.append('\n\t\t* Measurements')

                for measure in measurements:
                        control_statement.append(f'\t\t{measure["measure"]}')

                if len(measurements) > 0:
                        # control_statement.append('\n\t\tset filetype=ascii')
                        # control_statement.append('\t\tset nopadding')

                        meas_string_list = ' '.join([measure['name'] for measure in measurements])

                        # control_statement.append(f'\twrdata {os.path.join(self._output_path, "measurement.raw")} {meas_string_list}')

                        control_statement.append('\n\t\t* Measurement output in separate files')
                        for measure in measurements:
                                control_statement.append(f'\t\techo "$&{measure["name"]}" >> {os.path.join(self._output_path, "results", f"meas_{measure["name"]}.raw")}')

                if mc:
                        control_statement.append('\n\t\tlet mc_index = mc_index + 1')
                        control_statement.append('\t\treset')

                        control_statement.append('\n\t* End of Monte Carlo iteration')
                        control_statement.append('\tend')

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

        def run(self, **kwargs) -> str:
                # Verify the output folder exists
                if not os.path.exists(self._output_path):
                        os.makedirs(self._output_path)

                # Verify that the results folder is available
                if not os.path.exists(os.path.join(self._output_path, "results")):
                        os.makedirs(os.path.join(self._output_path, "results"))

                path_input_netlist = self._write_netlist_dut()

                self._include(path_input_netlist)
                path_output_netlist = self._write_netlist(**kwargs)

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

                # self.measure.process_measure(os.path.join(self._output_path, 'measurement.raw'))

                return output
