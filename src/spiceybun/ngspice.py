import subprocess
import os
import re
from pathlib import Path

from itertools import product

from spiceybun.measure_ngspice import Measure_ngspice
from spiceybun.variable import Variable

class Ngspice:
        def __init__(self, path_netlist, **kwargs):
                self._netlist           = []

                self._analysis          = []
                self._variables         = []
                self._libraries         = []
                self._plots             = []
                self._spiceinit         = ''

                # Control statements
                self._plot_all          = False

                self._path_netlist      = path_netlist

                self._output_path       = Path(__file__).parent

                self.measure            = Measure_ngspice()

                # Preparation during init
                self._read_dut_nelist()

# Internal methods

        def _read_dut_variables(self) -> None:
                variables = []

                for line in self._netlist_dut:
                        result = re.findall(r'\{\w+\}', line)

                        if len(result) > 0:
                                variables.extend(result)

                variables = list(set(variables))

                for variable in variables:
                        name = variable.strip('{}')
                        self._variables.append(Variable(name))

        def _read_dut_nelist(self) -> None:
                with open(self._path_netlist, 'r') as f:
                        self._netlist_dut = f.readlines()

                # TODO: Strip existing control statements

                # Extract variables
                self._read_dut_variables()

        def _include(self, path, **kwargs) -> str:
                # str = f'.include "{path}"'
                str = f'.include {path}'

                if 'section' in kwargs:
                        str = str + ' ' + kwargs['section']

                self._netlist.append(str)

                return str

        def _write_netlist_dut(self, **kwargs) -> str:
                subfolder = kwargs.get('id', '')

                output_path = os.path.join(self._output_path, subfolder)
                output_netlist = os.path.join(output_path, 'netlist.spice')

                with open(output_netlist, 'w') as f:
                        f.writelines(self._netlist_dut)
                os.chmod(output_netlist, 0o755)

                return output_netlist

        def _write_netlist(self, **kwargs) -> str:
                subfolder = kwargs.get('id', '')

                self._add_control(**kwargs)

                self._netlist.append('.end')

                output_path = os.path.join(self._output_path, subfolder)
                output_netlist = os.path.join(output_path, 'tb_test.spice')

                with open(output_netlist, 'w') as f:
                        f.write('\n'.join(self._netlist))
                os.chmod(output_netlist, 0o755)

                self._netlist_output = output_netlist

                return output_netlist

        def _write_run_command(self, **kwargs) -> str:
                subfolder = kwargs.get('id', '')

                folder_path = os.path.join(self._output_path, subfolder)

                path_output_netlist = self._netlist_output

                # command_format = "#!/bin/bash\nngspice -i -o {output_path} {input_path} -a || sh"
                command_format = "#!/bin/bash\nngspice -o {output_path} {input_path} -a"
                command_format = "#!/bin/bash\nngspice -b -o {output_path} {input_path} -a"

                command_path = os.path.join(folder_path, 'run_command')
                output_path = os.path.join(folder_path, 'output.log')
                input_path = path_output_netlist

                netlist_command = command_format.format(
                        output_path=output_path, 
                        input_path=input_path
                        )
                
                with open(command_path, 'w') as f:
                        f.write(netlist_command)
                os.chmod(command_path, 0o755)

                return command_path

        def _write_spiceinit(self, **kwargs) -> str:
                if self._spiceinit == '':
                        return ''

                subfolder = kwargs.get('id', '')

                output_path = os.path.join(self._output_path, subfolder)
                output_spiceinit = os.path.join(output_path, '.spiceinit')

                with open(self._spiceinit, 'r') as f:
                        spiceinit_content = f.read()

                with open(output_spiceinit, 'w') as f:
                        f.write(spiceinit_content)
                os.chmod(output_spiceinit, 0o755)

                return output_spiceinit

        def _add_control(self, **kwargs) -> list:
                # Kwargs
                mc = kwargs.get('mc', False)

                control_statement = []
                control_statement.append('\n* Control statements added by the tool')

                # Parameter definitions
                variables = kwargs.get('variables', self._libraries + self._variables)
                for variable in variables:
                        control_statement.append(variable.get_value_definition())

                if mc:
                        seed = kwargs.get('seed', 1)
                        mc_runs = kwargs.get('mc_runs', 350)

                # Start of control statements
                control_statement.append('\n.control')

                # Section
                # Measurement file preparation
                control_statement.extend(self._netlist_define_measurement_setup())

                # Section Monte Carlo
                if mc:
                        control_statement.append('\n\t* Monte Carlo analysis')
                        control_statement.append(f'\tsetseed {seed}')
                        control_statement.append(f'\tlet mc_runs={mc_runs}')
                        control_statement.append('\tlet mc_index=0')

                        control_statement.append('\n\twhile mc_index < mc_runs')

                # Section
                # Append analysis
                for element in self._analysis:
                        control_statement.append(f'\t\t{element}')

                        # suffix = element.split()[0]

                # Section
                # Save statements
                # TODO: Wrap measurements and save statments with their respective analysis
                control_statement.extend(self._netlist_define_plot(**kwargs))

                # Measureement definition and write to file
                control_statement.extend(self._netlist_define_measurement_write())

                if mc:
                        control_statement.append('\n\t\tlet mc_index = mc_index + 1')
                        control_statement.append('\t\treset')

                        control_statement.append('\n\t* End of Monte Carlo iteration')
                        control_statement.append('\tend')

                control_statement.append('\n\texit')
                control_statement.append('.endc\n')

                self._netlist.extend(control_statement)
                return control_statement

        def _netlist_define_plot(self, **kwargs) -> list:
                control_statement = []

                subfolder = kwargs.get('id', '')
                output_path = os.path.join(self._output_path, subfolder, 'output.raw')

                # Keep vector names in the header
                control_statement.append('\n\t\tset wr_vecnames')
                
                # Use a single scale (column) for all signals
                control_statement.append('\t\tset wr_singlescale')

                if not self._plot_all:
                        control_statement.append(f'\t\twrdata {output_path} {' '.join(self._plots)}')
                else:
                        control_statement.append('\t\tsave all')
                        control_statement.append(f'\t\twrdata {output_path} all')

                return control_statement

        def _netlist_define_measurement_setup(self) -> list:
                control_statement = []

                measurements = self.measure.get_all()
                if len(measurements)>0:
                        control_statement.append('\t*Prepare measurement output file with a header')
                        measurement_list = ' '.join([measure['name'] for measure in measurements])
                        control_statement.append(f'\techo "{measurement_list}" > {os.path.join(self._output_path, "results", "measurements.raw\n")}')

                return control_statement

        def _netlist_define_measurement_write(self) -> list:
                control_statement = []

                control_statement.append('\n\t\t* Measurements')

                measurements = self.measure.get_all()
                for measure in measurements:
                        control_statement.append(f'\t\t{measure["measure"]}')

                if len(measurements) > 0:
                        # control_statement.append('\n\t\tset filetype=ascii')
                        # control_statement.append('\t\tset nopadding')

                        # meas_string_list = ' '.join([measure['name'] for measure in measurements])
                        # control_statement.append(f'\twrdata {os.path.join(self._output_path, "measurement.raw")} {meas_string_list}')

                        control_statement.append('\n\t\t* Measurement output in separate files')
                        measurement_list = ' '.join([f'$&{measure['name']}' for measure in measurements])
                        control_statement.append(f'\t\techo "{measurement_list}" >> {os.path.join(self._output_path, "results", "measurements.raw")}')

                return control_statement

        def _run_single_run(self, **kwargs) -> str:
                subfolder = kwargs.get('id', '')

                output_path = os.path.join(self._output_path, subfolder)

                # Verify the output folder exists
                if not os.path.exists(output_path):
                        os.makedirs(output_path)

                # Verify that the results folder is available
                if not os.path.exists(os.path.join(output_path, "results")):
                        os.makedirs(os.path.join(output_path, "results"))

                path_input_netlist = self._write_netlist_dut(**kwargs)
                self._write_spiceinit(**kwargs)

                self._include(path_input_netlist)
                self._write_netlist(**kwargs)

                command_path = self._write_run_command(**kwargs)

                output = subprocess.run(
                        command_path, 
                        # env=self.env, 
                        shell=True, 
                        capture_output=True, 
                        text=True
                )

                run_path = os.path.join(output_path, 'run.log')

                with open(run_path, 'w') as f:
                        f.write(output.stdout)
                os.chmod(command_path, 0o755)

                # self.measure.process_measure(os.path.join(self._output_path, 'measurement.raw'))

                return output.stdout

        def _run_sweep(self, sweep_list, **kwargs) -> list:
                results = []

                for idx, run in enumerate(sweep_list):
                        self._netlist = []
                        results.append(self._run_single_run(variables=run, id=f'{idx}', **kwargs))

                return results

# Public methods

        def get_variables(self) -> list:
                return self._variables

        def set_variable(self, name, value) -> Variable | None:
                for variable in self._variables:
                        if variable.get_name() == name:
                                variable.set_value(value)
                                return variable

                return None

        def add_library(self, path, section=''):
                library = Variable(name=path, type='library')
                library.set_value(section)
                self._libraries.append(library)

                return library

        def add_transient(self, t_stop, **kwargs) -> str:
                # Overwrite previous transient statement if it exists
                self._analysis = [x for x in self._analysis if not x.startswith("tran")]

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

        def add_spiceinit(self, path) -> str:
                self._spiceinit = path

                return self._spiceinit

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

        def run(self, **kwargs) -> str | list:
                total_variations = self._libraries + self._variables

                if len(total_variations) == 0:
                        return self._run_single_run(**kwargs)
                
                #Create all variation combinations
                permutation_pre_list = [variable.get_split() for variable in total_variations]
                permutations = list(product(*permutation_pre_list))

                if len(permutations) == 1:
                        return self._run_single_run(**kwargs)

                return self._run_sweep(permutations, **kwargs)