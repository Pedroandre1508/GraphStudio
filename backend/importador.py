import csv
import os
import pandas as pd
from .grafo import Grafo

def importar_grafo(caminho_arquivo: str) -> Grafo:
    """
    Lê um arquivo CSV contendo cidades e distâncias,
    criando e retornando um objeto Grafo com vértices,
    arestas e coordenadas geográficas.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    grafo = Grafo(direcionado=False)
    cidades_coordenadas = {}

    with open(caminho_arquivo, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)
        for linha in leitor:
            origem = linha["origem"].strip()
            destino = linha["destino"].strip()
            peso = float(linha["peso"])

            lat_origem = float(linha["lat_origem"])
            long_origem = float(linha["long_origem"])
            lat_destino = float(linha["lat_destino"])
            long_destino = float(linha["long_destino"])

            # Adicionar vértices (evita duplicação)
            grafo.adicionar_vertice(origem)
            grafo.adicionar_vertice(destino)

            # Registrar coordenadas se ainda não tiver
            if origem not in cidades_coordenadas:
                grafo.definir_coordenada(origem, lat_origem, long_origem)
                cidades_coordenadas[origem] = True

            if destino not in cidades_coordenadas:
                grafo.definir_coordenada(destino, lat_destino, long_destino)
                cidades_coordenadas[destino] = True

            # Adicionar aresta
            grafo.adicionar_aresta(origem, destino, peso)

    return grafo

def importar_csv(arquivo):
    """
    Importa um CSV com colunas mínimas: origem, destino, peso
    Opcionalmente: lat_origem, long_origem, lat_destino, long_destino
    Retorna um objeto Grafo já populado.
    """
    df = pd.read_csv(arquivo)
    grafo = Grafo()

    for _, row in df.iterrows():
        origem = str(row['origem']).strip()
        destino = str(row['destino']).strip()

        # peso pode não existir; default 1
        peso = row.get('peso', 1)
        try:
            peso = float(peso)
        except Exception:
            pass

        # Adiciona vértices se não existirem (usa a presença na dict vertices)
        if origem not in grafo.vertices:
            try:
                grafo.adicionar_vertice(origem)
            except Exception:
                # se assinatura diferente, apenas ignore
                pass
        if destino not in grafo.vertices:
            try:
                grafo.adicionar_vertice(destino)
            except Exception:
                pass

        # Tenta salvar coordenadas usando o método definir_coordenada
        try:
            if 'lat_origem' in df.columns and 'long_origem' in df.columns:
                lat_orig = float(row['lat_origem'])
                long_orig = float(row['long_origem'])
                grafo.definir_coordenada(origem, lat_orig, long_orig)
        except Exception:
            pass

        try:
            if 'lat_destino' in df.columns and 'long_destino' in df.columns:
                lat_dest = float(row['lat_destino'])
                long_dest = float(row['long_destino'])
                grafo.definir_coordenada(destino, lat_dest, long_dest)
        except Exception:
            pass

        # Adiciona aresta (assume grafo.adicionar_aresta aceita origem,destino,peso)
        try:
            grafo.adicionar_aresta(origem, destino, peso=peso)
        except TypeError:
            # tentar sem nome do argumento peso se assinatura diferente
            try:
                grafo.adicionar_aresta(origem, destino, peso)
            except Exception:
                pass
        except Exception:
            pass

    return grafo
