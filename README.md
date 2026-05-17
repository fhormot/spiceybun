# SPPY

An NGSPICE wrapper for simplified verification.

# Usage

```Python
import sppy

simulator = sppy.ngspice('./netlist.spice')

ngspice.add_transient(1e-6)

simulator.save_signal('V(v_out)')
simulator.save_signal('V(v_in)')

simulator.run()

```

# Documentation
TBD

# Long term roadmap

- [ ] Enabling basic functionality:
    - [ ] Analysis statements
    - [ ] Variables
    - [ ] Measurements
- [ ] Sweeps and Monte Carlo
- [ ] Advanced features
    - [ ] Netlist from XSchem
    - [ ] Simulator options
    - [ ] Report generation