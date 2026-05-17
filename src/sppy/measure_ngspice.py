import pandas as pd

class Measure_ngspice():
        def __init__(self):
                self._measure = []

        def get_all(self) -> list:
                return self._measure
        
        def explicit(self, measure) -> str:
                arguments = measure.split()

                self._measure.append({
                        "name": arguments[2],
                        "analysis": arguments[1],
                        "measure": measure
                        })
                
                return measure
        
        def process_measure(self, path) -> object:
                with open(path, 'r') as f:
                        header = f.readline().strip().split()
                        values = f.readline().strip().split()

                # df = pd.read_csv(
                #     path,    
                #     delimiter=' ',
                #     nrows=1,
                #     skipinitialspace=True 
                # )

                # Extract header and first row
                output = pd.DataFrame([values], columns=header)

                output.to_csv(path, index=False, header=True)

                return output