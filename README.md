# SPIPy

An NGSPICE wrapper for simplified verification.

# Usage

```Python
import spipy

simulator = spipy.ngspice('./netlist.spice')

ngspice.add_transient(1e-6)

simulator.save_signal('V(v_out)')
simulator.save_signal('V(v_in)')

simulator.run()

```

# Documentation
TBD

# Long term roadmap

- [ ] Enabling basic functionality:
    - [ ] All analysis statements
    - [ ] Variables
        - [x] Simple variables
        - [ ] Equations
        - [ ] Advanced variable features (distribution, limits, etc.)
    - [ ] Measurements
        - [x] Explicit spice input
- [x] Sweeps
- [x] Monte Carlo
- [ ] Advanced features
    - [ ] Netlist from XSchem
    - [ ] Simulator options
    - [ ] Report generation