import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'quadqaoa.py')))

import csv
import knapsack
import circuits
from quadqaoa import find_optimal_angles, get_probs_dict
import visualization

def read_knapsack_csv(filepath):
    """Lee un CSV y retorna listas de beneficios, costos y el peso máximo."""
    values = []
    weights = []
    max_weight = None
    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            values.append(float(row['beneficio']))
            weights.append(float(row['costo']))
            if 'max_weight' in row and max_weight is None:
                max_weight = float(row['max_weight'])
    if max_weight is None:
        # Si no viene en el CSV, puedes definirlo manualmente aquí
        max_weight = sum(weights) / 2  # ejemplo: la mitad del total
    return values, weights, max_weight

def main():
    # Cambia el path al archivo CSV que quieras usar
    csv_path = "datos.csv"
    values, weights, max_weight = read_knapsack_csv(csv_path)
    print(f"Valores: {values}")
    print(f"Pesos: {weights}")
    print(f"Peso máximo: {max_weight}")

    # Crear el problema de Knapsack
    problem = knapsack.KnapsackProblem(values, weights, max_weight)
    print(f"Problem: {problem}")

    # Parámetros para QAOA
    a = 10
    b = 10
    p = 3

    print("Building Circuit...")
    circuit = circuits.QuadQAOA(problem, p=p)
    print("Done!")
    print("Optimizing Angles...")
    angles = find_optimal_angles(circuit, problem, a, b)
    if angles is None:
        print("Error: No se encontraron ángulos óptimos. Revisa la definición del problema o los parámetros.")
        return

    print("Done!")
    print(f"Optimized Angles: {angles}")
    probs = get_probs_dict(circuit, problem, angles, a, b)
    print(f"Probabilities of Bitstrings: {probs}")
    # visualization.hist(probs)

if __name__ == "__main__":
    main()