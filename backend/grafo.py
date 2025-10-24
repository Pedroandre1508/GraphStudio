# backend/grafo.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set
from collections import deque, defaultdict
import heapq
from typing import Optional, Tuple, List, Dict, Set

@dataclass
class Aresta:
    id: str
    origem: str
    destino: str
    peso: float
    rotulo: Optional[str] = None
    direcionada: bool = False
    

class Vertice:
    def __init__(self, rotulo, lat=None, long=None):
        self.rotulo = rotulo
        self.lat = lat
        self.long = long
        self.adjacentes = {}

class Grafo:
    def __init__(self, direcionado: bool = False):
        self.direcionado = direcionado
        # adj: vertice -> lista de tuplas (vizinho, peso, id_aresta)
        self.adjacencia: Dict[str, List[Tuple[str, float, str]]] = defaultdict(list)
        self.arestas: Dict[str, Aresta] = {}
        self.vertices: Set[str] = set()
        self._contador_arestas = 0
        self.coordenadas: Dict[str, Tuple[float, float]] = {}

    def definir_coordenada(self, v: str, x: float, y: float):
        self.coordenadas[v] = (x, y)

    # ---------------------------
    # utilitários de id
    # ---------------------------
    def _proximo_id_aresta(self) -> str:
        self._contador_arestas += 1
        return f"a{self._contador_arestas}"

    # ---------------------------
    # inserções / remoções
    # ---------------------------
    def adicionar_vertice(self, v: str) -> None:
        self.vertices.add(v)
        _ = self.adjacencia[v]  # garante chave

    def adicionar_aresta(self, u: str, v: str, peso: float = 1.0, id_aresta: Optional[str] = None, rotulo: Optional[str] = None) -> str:
        if id_aresta is None:
            id_aresta = self._proximo_id_aresta()
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)
        aresta = Aresta(id=id_aresta, origem=u, destino=v, peso=peso, rotulo=rotulo, direcionada=self.direcionado)
        self.arestas[id_aresta] = aresta
        self.adjacencia[u].append((v, peso, id_aresta))
        if not self.direcionado:
            self.adjacencia[v].append((u, peso, id_aresta))
        return id_aresta

    def remover_aresta(self, id_aresta: str) -> bool:
        if id_aresta not in self.arestas:
            return False
        aresta = self.arestas.pop(id_aresta)
        self.adjacencia[aresta.origem] = [(x,p,i) for (x,p,i) in self.adjacencia[aresta.origem] if i != id_aresta]
        if not self.direcionado:
            self.adjacencia[aresta.destino] = [(x,p,i) for (x,p,i) in self.adjacencia[aresta.destino] if i != id_aresta]
        return True

    def remover_vertice(self, v: str) -> bool:
        if v not in self.vertices:
            return False
        incidentes = []
        for (vizinho, _, id_aresta) in list(self.adjacencia[v]):
            incidentes.append(id_aresta)
        if self.direcionado:
            for x in list(self.vertices):
                if x == v: 
                    continue
                for (vizinho, _, id_aresta) in list(self.adjacencia[x]):
                    if vizinho == v and id_aresta not in incidentes:
                        incidentes.append(id_aresta)
        for id_aresta in set(incidentes):
            if id_aresta in self.arestas:
                self.remover_aresta(id_aresta)
        if v in self.adjacencia:
            del self.adjacencia[v]
        self.vertices.remove(v)
        return True

    # ---------------------------
    # matrizes
    # ---------------------------
    def matriz_adjacencia(self) -> Tuple[List[str], List[List[int]]]:
        vertices = sorted(self.vertices)
        indice = {v: i for i, v in enumerate(vertices)}
        n = len(vertices)
        matriz = [[0 for _ in range(n)] for __ in range(n)]
        for u in vertices:
            for (v, _, _) in self.adjacencia[u]:
                matriz[indice[u]][indice[v]] = 1  # 1 se existe ligação
        return vertices, matriz

    def matriz_incidencia(self) -> Tuple[List[str], List[str], List[List[int]]]:
        vertices = sorted(self.vertices)
        arestas = sorted(self.arestas.keys())
        indice_vert = {v:i for i,v in enumerate(vertices)}
        matriz = [[0 for _ in arestas] for __ in vertices]
        for j, id_aresta in enumerate(arestas):
            a = self.arestas[id_aresta]
            if self.direcionado:
                matriz[indice_vert[a.origem]][j] = 1
                matriz[indice_vert[a.destino]][j] = -1
            else:
                matriz[indice_vert[a.origem]][j] = 1
                matriz[indice_vert[a.destino]][j] = 1
        return vertices, arestas, matriz

    # ---------------------------
    # Algoritmo de Prim
    # ---------------------------
    def prim(self, inicio: Optional[str] = None) -> Tuple[Set[str], List[str], float]:
        if self.direcionado:
            raise ValueError("Prim requer grafo não-direcionado.")
        if not self.vertices:
            return set(), [], 0.0
        inicio = inicio or next(iter(self.vertices))
        T: Set[str] = {inicio}
        V: Set[str] = set(self.vertices) - T
        Tmin: List[str] = []
        total = 0.0

        while T != set(self.vertices):
            melhor = None  # (peso, j, k, id_aresta)
            for j in T:
                for (k, peso, id_aresta) in self.adjacencia[j]:
                    if k in V:
                        if melhor is None or peso < melhor[0]:
                            melhor = (peso, j, k, id_aresta)
            if melhor is None:
                break
            peso, j, k, id_aresta = melhor
            T.add(k)
            V.remove(k)
            Tmin.append(id_aresta)
            total += peso
        return T, Tmin, total

    # ---------------------------
    # BFS
    # ---------------------------
    def bfs(self, inicio: str) -> Tuple[Dict[str, Optional[str]], List[str], Set[Tuple[str,str]]]:
        if inicio not in self.vertices:
            raise KeyError("vértice inicial não existe")
        fila = deque()
        marcados: Set[str] = set()
        pai: Dict[str, Optional[str]] = {v: None for v in self.vertices}
        exploradas: Set[Tuple[str,str]] = set()

        fila.append(inicio)
        marcados.add(inicio)
        ordem: List[str] = []

        while fila:
            v = fila.popleft()
            ordem.append(v)
            for (w, _, _) in self.adjacencia[v]:
                if w not in marcados:
                    exploradas.add((v,w))
                    pai[w] = v
                    fila.append(w)
                    marcados.add(w)
                else:
                    if (v,w) not in exploradas:
                        exploradas.add((v,w))
        return pai, ordem, exploradas

    # ---------------------------
    # DFS
    # ---------------------------
    def dfs(self, inicio: str) -> Tuple[Dict[str, Optional[str]], List[str], Set[Tuple[str,str]]]:
        if inicio not in self.vertices:
            raise KeyError("vértice inicial não existe")
        marcados: Set[str] = set()
        pai: Dict[str, Optional[str]] = {v: None for v in self.vertices}
        exploradas: Set[Tuple[str,str]] = set()
        ordem: List[str] = []

        def visitar(v: str):
            marcados.add(v)
            ordem.append(v)
            for (w, _, _) in self.adjacencia[v]:
                if w not in marcados:
                    exploradas.add((v,w))
                    pai[w] = v
                    visitar(w)
                else:
                    if (v,w) not in exploradas:
                        exploradas.add((v,w))
        visitar(inicio)
        return pai, ordem, exploradas

    # ---------------------------
    # Algoritmo de Roy (SCCs)
    # ---------------------------
    def roy(self) -> List[Set[str]]:
        if not self.direcionado:
            raise ValueError("Roy aplica-se a grafos dirigidos (SCCs).")
        restantes = set(self.vertices)
        componentes: List[Set[str]] = []

        def alcancaveis_para_frente(seed: str, permitidos: Set[str]) -> Set[str]:
            marcados = {seed}
            fila = deque([seed])
            while fila:
                u = fila.popleft()
                for (vizinho, _, _) in self.adjacencia[u]:
                    if vizinho in permitidos and vizinho not in marcados:
                        marcados.add(vizinho)
                        fila.append(vizinho)
            return marcados

        def alcancaveis_para_tras(seed: str, permitidos: Set[str]) -> Set[str]:
            marcados = {seed}
            fila = deque([seed])
            while fila:
                u = fila.popleft()
                for a in permitidos:
                    for (vizinho, _, _) in self.adjacencia[a]:
                        if vizinho == u and a not in marcados:
                            marcados.add(a)
                            fila.append(a)
            return marcados

        while restantes:
            v = next(iter(restantes))
            frente = alcancaveis_para_frente(v, restantes)
            tras = alcancaveis_para_tras(v, restantes)
            intersecao = frente.intersection(tras)
            if not intersecao:
                intersecao = {v}
            componentes.append(intersecao)
            restantes -= intersecao
        return componentes
    
    # ---------------------------
    # Verificação de planaridade
    # ---------------------------
    def verificar_planaridade(self) -> Tuple[bool, str]:
        """
        Verifica condições necessárias de planaridade baseadas nos teoremas:
        1. Fórmula de Euler: V - E + R = 2
        2. Se V >= 3 então E <= 3V - 6
        3. Se V >= 3 e não há ciclos de comprimento 3, então E <= 2V - 4
        """
        n = len(self.vertices)
        m = len(self.arestas)
        
        # Grafo trivial
        if n < 3:
            return True, "Grafo com menos de 3 vértices é planar por definição."
        
        # Condição 1: E <= 3V - 6 (para grafos simples, planares e conexos)
        if m > 3 * n - 6:
            return False, f"Não planar: |E|={m} > 3|V|-6={3*n-6} (viola teorema de Euler)"
        
        # Verificar se há triângulos (ciclos de comprimento 3)
        tem_triangulo = self._tem_ciclo_comprimento_3()
        
        # Condição 2: Se não há triângulos, E <= 2V - 4
        if not tem_triangulo and m > 2 * n - 4:
            return False, f"Não planar: sem triângulos e |E|={m} > 2|V|-4={2*n-4}"
        
        # Passou nas condições necessárias
        if tem_triangulo:
            return True, f"Possivelmente planar: |E|={m} <= 3|V|-6={3*n-6} (condição necessária satisfeita)"
        else:
            return True, f"Possivelmente planar: sem triângulos e |E|={m} <= 2|V|-4={2*n-4} (condição necessária satisfeita)"

    def _tem_ciclo_comprimento_3(self) -> bool:
        """
        Verifica se existe um ciclo de comprimento 3 (triângulo) no grafo.
        Retorna True se encontrar pelo menos um triângulo.
        """
        for u in self.vertices:
            vizinhos_u = {v for (v, _, _) in self.adjacencia[u]}
            for (v, _, _) in self.adjacencia[u]:
                # Para cada vizinho v de u, verificar se há um w adjacente a ambos
                vizinhos_v = {w for (w, _, _) in self.adjacencia[v]}
                # Interseção dos vizinhos (excluindo u e v)
                comum = (vizinhos_u & vizinhos_v) - {u, v}
                if comum:
                    return True  # Encontrou triângulo: u-v-w-u
        return False

    # ---------------------------
    # Algoritmo de Welsh–Powell
    # ---------------------------
    def welsh_powell(self) -> Dict[str, int]:
        """Coloração de grafo pelo algoritmo Welsh–Powell."""
        graus = {v: len(self.adjacencia[v]) for v in self.vertices}
        vertices_ordenados = sorted(self.vertices, key=lambda v: graus[v], reverse=True)
        cor_atual = 0
        cores: Dict[str, int] = {}

        for v in vertices_ordenados:
            if v in cores:
                continue
            cor_atual += 1
            cores[v] = cor_atual
            for u in vertices_ordenados:
                if u not in cores:
                    if all(cores.get(viz) != cor_atual for (viz, _, _) in self.adjacencia[u]):
                        cores[u] = cor_atual
        return cores

    # ---------------------------
    # Algoritmo A*
    # ---------------------------
    def _coord_do_vertice(self, nome: str) -> Optional[Tuple[float, float]]:
        """
        Retorna (lat, lon) do vértice a partir do dicionário self.coordenadas.
        """
        c = self.coordenadas.get(nome)
        if c is None:
            return None
        try:
            return float(c[0]), float(c[1])
        except Exception:
            return None

    def a_estrela(self, inicio: str, destino: str) -> Tuple[List[str], float]:
        """
        Executa A* do vértice inicio ao destino usando self.adjacencia e
        self.coordenadas. Heurística: distância Manhattan sobre (lat,lon).
        Retorna (caminho, custo) ou ([], inf) se não há caminho.
        """
        if inicio not in self.vertices or destino not in self.vertices:
            raise KeyError("Vértice início ou destino inexistente")

        dest_coord = self._coord_do_vertice(destino)

        def h(n: str) -> float:
            c = self._coord_do_vertice(n)
            if c is None or dest_coord is None:
                return 0.0
            return abs(c[0] - dest_coord[0]) + abs(c[1] - dest_coord[1])

        def vizinhos_e_peso(u: str):
            # retorna lista de (vizinho, peso)
            if u not in self.adjacencia:
                return []
            return [(viz, float(peso)) for (viz, peso, _id) in self.adjacencia[u]]

        # A* clássico com heap (f = g + h)
        open_set = []
        heapq.heappush(open_set, (h(inicio), 0.0, inicio))  # (f, g, node)
        came_from: Dict[str, Optional[str]] = {}
        g_score: Dict[str, float] = {inicio: 0.0}
        closed: Set[str] = set()

        while open_set:
            fcur, gcur, node = heapq.heappop(open_set)
            if node in closed:
                continue
            if node == destino:
                # reconstruir caminho
                path = []
                cur = node
                while cur is not None:
                    path.append(cur)
                    cur = came_from.get(cur)
                path.reverse()
                return path, g_score.get(destino, 0.0)
            closed.add(node)

            for (nbr, peso) in vizinhos_e_peso(node):
                tentative_g = gcur + float(peso)
                if tentative_g < g_score.get(nbr, float("inf")):
                    came_from[nbr] = node
                    g_score[nbr] = tentative_g
                    heapq.heappush(open_set, (tentative_g + h(nbr), tentative_g, nbr))

        return [], float("inf")

    def calcular_tabela_heuristica(self, destino: str) -> Dict[str, float]:
        """
        Calcula h(n) para todos os vértices em relação ao destino.
        Retorna dicionário {vertice: h(n)}
        """
        if destino not in self.vertices:
            return {}
        
        dest_coord = self._coord_do_vertice(destino)
        if dest_coord is None:
            return {v: 0.0 for v in self.vertices}
        
        tabela = {}
        for v in self.vertices:
            v_coord = self._coord_do_vertice(v)
            if v_coord is None:
                tabela[v] = 0.0
            else:
                # Distância de Manhattan
                tabela[v] = abs(v_coord[0] - dest_coord[0]) + abs(v_coord[1] - dest_coord[1])
        
        return tabela
