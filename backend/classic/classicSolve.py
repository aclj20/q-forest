import cvxpy as cp
import numpy as np
import pandas as pd

def solve_optimization():
	alphaMatrix = pd.read_csv("./preprocessing/data/map2_9nodes_benefits_normalized_matrix.csv", header=None).values
	weightCostMatrix = pd.read_csv("./preprocessing/data/map2_9nodes_costs_matrix.csv", header=None).values

	budget = 2

	alphaList = alphaMatrix.flatten() 
	weightCostList = weightCostMatrix.flatten()

	n_nodes = len(alphaList)               
	variables = cp.Variable((n_nodes + 1, n_nodes + 1), symmetric=True)

	objective = cp.Maximize(sum((.5 *(1 + variables[0, i])*alphaList[i - 1] for i in range(1, n_nodes + 1))))  

	constraint = [sum((.5 *(1 + variables[0, i]) * weightCostList[i - 1] for i in range(1, n_nodes + 1))) <= budget]
	
	constraint += [variables >> 0]
	for i in range(n_nodes + 1):
		constraint += [variables[i, i] == 1]

	problem = cp.Problem(objective, constraint)
	result = problem.solve()
	variablesArray = np.delete(np.array(variables.value[0]), 0)  
	 
	selected_vector = variablesArray

	print("Estado del problema:", problem.status)
	unNormalizedSolutionMatrix = np.array(selected_vector).reshape(alphaMatrix.shape)
	normalizedSolutionMatrix =  [[np.round((element + 1 ) / 2, 5 )for element in line] for line in unNormalizedSolutionMatrix]
	print(f"Resultado óptimo: {result:.2f}")
	print("Variables (vector 0/1):", selected_vector)
	print("Matriz de solución (0/1):")
	print(normalizedSolutionMatrix)
	return normalizedSolutionMatrix

# Call the function
solve_optimization()

