import random
import math
import pandas as pd
from typing import List, Tuple, Dict

INF = 10**9

class GeneticTSP:
    def __init__(self, edges_df: pd.DataFrame):
        df = edges_df.rename(columns={c:c.lower() for c in edges_df.columns})
        if 'origem' not in df.columns or 'destino' not in df.columns or 'peso' not in df.columns:
            raise ValueError("CSV must contain origem,destino,peso columns")
        self.df = df
        self.cities = sorted(set(df['origem']).union(set(df['destino'])))
        self.n = len(self.cities)
        self.index = {c:i for i,c in enumerate(self.cities)}
        self.dist = [[INF]*self.n for _ in range(self.n)]
        for _, row in df.iterrows():
            i = self.index[row['origem']]
            j = self.index[row['destino']]
            w = float(row['peso'])
            self.dist[i][j] = w
            self.dist[j][i] = w  # assume undirected
        for i in range(self.n):
            self.dist[i][i] = 0.0

    def route_cost(self, route: List[int], start_idx: int=0) -> float:
        """route is list of city indices (permutation of all cities) — cost includes return to start."""
        cost = 0.0
        if len(route) != self.n:
            return INF
        for k in range(len(route)-1):
            w = self.dist[route[k]][route[k+1]]
            if w >= INF:
                return INF
            cost += w
        # return to origin
        w = self.dist[route[-1]][route[0]]
        if w >= INF:
            return INF
        cost += w
        return cost

    def random_population(self, pop_size: int, fixed_start: int=None) -> List[List[int]]:
        pop = []
        base = list(range(self.n))
        for _ in range(pop_size):
            arr = base.copy()
            random.shuffle(arr)
            if fixed_start is not None:
                # move fixed_start to first position
                arr.remove(fixed_start)
                arr = [fixed_start] + arr
            pop.append(arr)
        return pop

    def pmx_crossover(self, parent1: List[int], parent2: List[int], cx1: int, cx2: int) -> List[int]:
        """PMX crossover with fixed points cx1 < cx2 (indices absolute). Works on full-permutation lists."""
        size = len(parent1)
        child = [-1]*size
        # copy segment
        for i in range(cx1, cx2+1):
            child[i] = parent1[i]
        # mapping
        for i in range(cx1, cx2+1):
            p2 = parent2[i]
            if p2 not in child:
                pos = i
                val = p2
                while True:
                    val_in_p1 = parent1[pos]
                    pos = parent2.index(val_in_p1)
                    if child[pos] == -1:
                        child[pos] = p2
                        break
        # fill remaining
        for i in range(size):
            if child[i] == -1:
                child[i] = parent2[i]
        return child

    def swap_mutation(self, individual: List[int], mutation_rate: float) -> List[int]:
        """Per-individual mutation: with probability mutation_rate swap two positions."""
        if random.random() > mutation_rate:
            return individual
        a,b = random.sample(range(len(individual)), 2)
        individual = individual.copy()
        individual[a], individual[b] = individual[b], individual[a]
        return individual

    def evolve(self,
               pop_size: int = 200,
               generations: int = 50,
               crossover_rate: float = 0.7,
               mutation_rate: float = 0.01,
               elitism: int = 2,
               cx_points: Tuple[int,int] = None,
               show_population_callback = None,
               fixed_start_idx: int = None,
               replace_invalid: bool = True):

        if pop_size < 100:
            raise ValueError("Tamanho da população mínimo é 100")
        if generations < 1:
            raise ValueError("Gerações deve ser >=1")
        if cx_points is None:
            # choose default fixed indexes in interior (not first/last)
            cx1 = max(1, self.n//4)
            cx2 = min(self.n-2, (self.n*3)//4)
            cx_points = (cx1, cx2)
        cx1, cx2 = cx_points
        # generate initial population
        population = self.random_population(pop_size, fixed_start=fixed_start_idx)
        best_overall = None
        best_cost_overall = float('inf')

        for gen in range(1, generations+1):
            # evaluate
            costs = [self.route_cost(ind) for ind in population]
            # replace impossible (INF) if requested
            if replace_invalid:
                for i,c in enumerate(costs):
                    if c >= INF:
                        # replace
                        new = list(range(self.n))
                        random.shuffle(new)
                        if fixed_start_idx is not None:
                            new.remove(fixed_start_idx)
                            new = [fixed_start_idx] + new
                        population[i] = new
                        costs[i] = self.route_cost(population[i])

            # sort by fitness (lower cost)
            paired = sorted(zip(costs, population), key=lambda x: x[0])
            costs = [p[0] for p in paired]
            population = [p[1] for p in paired]

            if costs[0] < best_cost_overall:
                best_cost_overall = costs[0]
                best_overall = population[0].copy()

            # optional callback for UI
            if show_population_callback:
                show_population_callback(gen, population, costs)

            # prepare next generation
            next_pop = population[:elitism]  # elitist keep
            # selection: tournament selection to choose parents for crossover
            def tournament_select(k=3):
                contenders = random.sample(list(zip(population,costs)), k)
                contenders.sort(key=lambda x: x[1])
                return contenders[0][0]

            while len(next_pop) < pop_size:
                if random.random() < crossover_rate:
                    p1 = tournament_select()
                    p2 = tournament_select()
                    child = self.pmx_crossover(p1, p2, cx1, cx2)
                else:
                    # reproduction without crossover (copy parent)
                    child = tournament_select().copy()
                # mutation
                child = self.swap_mutation(child, mutation_rate)
                next_pop.append(child)
            population = next_pop

            yield {
                'generation': gen,
                'best_route_idx': population[0],
                'best_cost': costs[0],
                'population_costs': costs,
                'best_overall_idx': best_overall,
                'best_overall_cost': best_cost_overall,
                'cities': self.cities
            }