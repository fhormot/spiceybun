from spiceybun.ngspice import Ngspice

from pathlib import Path

# Setup of relevant paths
path_file = Path(__file__).parent
path_netlist = path_file / "netlist.spice"  # Input file
path_output = path_file / "outputs"         # Output folder for raw files and plots

# Simulator setup
simulator = Ngspice(path_netlist)
simulator.set_output_path(path_output)

simulator.add_transient(500e-9, t_step=10e-12)

# Save signal setup
simulator.save_signal('V(v_out)')
simulator.save_signal('V(v_in)')

# Measurement setup
simulator.measure.explicit('meas tran t_delay_l2h TRIG V(v_in) VAL=0.75 RISE=1 TARG V(v_out) VAL=0.75 RISE=1')
simulator.measure.explicit('meas tran t_delay_h2l TRIG V(v_in) VAL=0.75 FALL=1 TARG V(v_out) VAL=0.75 FALL=1')

output = simulator.run()

measurements = simulator.get_measurements()

print(measurements[0])