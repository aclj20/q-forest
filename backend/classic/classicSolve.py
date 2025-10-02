import cvxpy as cp
import numpy as np
import pandas as pd

# === 1. Leer matrices ===
alphaMatrix = pd.read_csv("./preprocessing/data/map2_9nodes_benefits_normalized_matrix.csv", header=None).values
weightCostMatrix = pd.read_csv("./preprocessing/data/map2_9nodes_costs_matrix.csv", header=None).values

budget = 4

alphaList = alphaMatrix.flatten() 
weightCostList = weightCostMatrix.flatten()

n_nodes = len(alphaList)               
variables = cp.Variable(n_nodes, boolean=True)

objective = cp.Maximize(alphaList @ variables)  

constraint = [weightCostList @ variables <= budget]  

problem = cp.Problem(objective, constraint)
result = problem.solve()

selected_vector = np.round(variables.value).astype(int)

solution_matrix = selected_vector.reshape(alphaMatrix.shape)

print(f"Resultado óptimo: {result:.2f}")
print("Variables (vector 0/1):", selected_vector)
print("Matriz de solución (0/1):")
print(solution_matrix)

