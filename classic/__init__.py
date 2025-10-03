"""
Q-FOREST Classic Optimization Module

Classical optimization using semidefinite programming (SDP)
"""

from .classic_solver import ClassicSolver, solve_optimization_from_files

__all__ = ['ClassicSolver', 'solve_optimization_from_files']
__version__ = '1.0.0'

