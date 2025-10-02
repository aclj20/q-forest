"""Helper functions for optimizing the parameters beta, gamma."""
import numpy as np
from scipy.optimize import shgo


def average_value(probs_dict, func):
    """Calculate the average value of a function over a probability dict."""
    bitstrings = list(probs_dict.keys())
    values = np.array(list(map(func, bitstrings)))
    probs = np.array(list(probs_dict.values()))
    return sum(values * probs)


def optimize_angles(p, angles_to_value, gamma_range, beta_range):
    """Optimize the parameters beta, gamma for a given function angles_to_value"""
    bounds = np.array([gamma_range, beta_range] * p)
    print(f"Optimizando con bounds: {bounds}")
    try:
        result = shgo(angles_to_value, bounds, iters=3)
        print(f"Resultado de shgo: {result}")
        if hasattr(result, "x") and result.x is not None:
            return result.x
        else:
            #Error
            print("shgo no encontró una solución válida.")
            return None
    except Exception as e:
        print(f"Error en shgo: {e}")
        return None
