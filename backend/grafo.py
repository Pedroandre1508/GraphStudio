# backend/grafo.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set
from collections import deque, defaultdict

@dataclass
class Aresta:
    id: str
    origem: str
    destino: str
    peso: float
    rotulo: Optional[str] = None
    direcionada: bool = False

class Grafo:
    def __init__(self, direcionado: bool = False):
        self.direcionado = direcionado
        # adj: vertice -> lista de tuplas (vizinho, peso, id_aresta)
        self.adjacencia: Dict[str, List[Tuple[str, float, str]]] = defaultdict(list)
        self.arestas: Dict[str, Aresta] = {}
        self.vertices: Set[str] = set()
        self._contador_arestas = 0

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
