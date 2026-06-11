import pandas as pd

class Measure_ngspice():
        def __init__(self):
                self._measure = []

                self._results = pd.DataFrame()

# Internal methods

# Public methods

        def get_measurements(self) -> list:
                return self._measure
        
        def get_results(self) -> object:
                return self._results
        
        def explicit(self, measure) -> str:
                arguments = measure.split()

                self._measure.append({
                        "name": arguments[2],
                        "analysis": arguments[1],
                        "measure": measure
                        })
                
                return measure
        
        def process_measure(self, path) -> object:
                self._results = pd.read_csv(path, delimiter=' ', header=0)

                return self.get_results()