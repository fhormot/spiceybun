# SPICEybun

An NGSPICE wrapper for simplified verification.

# Usage

```Python
from spiceybun import ngspice

simulator = ngspice('./netlist.spice')

simulator.add_transient(1e-6)

simulator.save_signal('V(v_out)')
simulator.save_signal('V(v_in)')

simulator.run()

```

# Documentation
TBD

# Long term roadmap

- [ ] Enabling basic functionality:
    - [ ] All analysis statements
    - [ ] Libraries
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
    - [ ] Simulator error handling