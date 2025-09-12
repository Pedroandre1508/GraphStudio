# streamlit_app/app.py
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.grafo import Grafo

st.set_page_config(page_title="Projeto Grafos", layout="wide")

# ----------------------------
# Inicialização
# ----------------------------
if "grafo" not in st.session_state:
    st.session_state.grafo = Grafo(direcionado=False)

grafo: Grafo = st.session_state.grafo

# ----------------------------
# Layout principal
# ----------------------------
st.markdown(
    "<div style='border:2px solid #444; padding:10px; border-radius:6px;'>"
    "<h2 style='margin:0;'>⚛️GraphStudio</h2>"
    "</div>",
    unsafe_allow_html=True
)

menu_principal = st.sidebar.radio(
    "Menu principal",
    ["Inserção", "Algoritmos", "Matrizes"]
)

# ----------------------------
# Inserção
# ----------------------------
if menu_principal == "Inserção":
    st.subheader("Configuração do grafo")
    modo = st.radio("Modo do grafo", options=["Não-direcionado", "Direcionado"])
    if (modo == "Direcionado") != grafo.direcionado:
        if st.button("Recriar grafo vazio neste modo"):
            st.session_state.grafo = Grafo(direcionado=(modo == "Direcionado"))
            grafo = st.session_state.grafo

    st.markdown("---")
    st.subheader("Inserir vértice")
    v = st.text_input("Nome do vértice", key="inp_vertice")
    if st.button("Adicionar vértice"):
        if v:
            grafo.adicionar_vertice(v)
            st.success(f"Vértice '{v}' inserido.")

    st.markdown("---")
    st.subheader("Inserir aresta/arco")
    u = st.text_input("Origem (u)", key="inp_u")
    vv = st.text_input("Destino (v)", key="inp_v")
    peso = st.number_input("Peso", value=1.0, key="inp_peso")
    aid = st.text_input("ID da aresta (opcional)", key="inp_aid")
    label = st.text_input("Rótulo (opcional)", key="inp_label")
    if st.button("Adicionar aresta/arco"):
        if u and vv:
            _id = grafo.adicionar_aresta(
                u, vv, peso=peso, id_aresta=(aid or None), rotulo=(label or None)
            )
            st.success(f"Aresta inserida: {_id} ({u} -> {vv})")

    st.markdown("---")
    st.subheader("Remover elementos")
    rem_v = st.text_input("Remover vértice (nome)", key="rem_v")
    if st.button("Remover vértice"):
        if rem_v:
            ok = grafo.remover_vertice(rem_v)
            if ok:
                st.success(f"Vértice {rem_v} removido")
            else:
                st.error("Vértice não existe")

    rem_aid = st.text_input("Remover aresta/arco (id)", key="rem_aid")
    if st.button("Remover aresta/arco"):
        if rem_aid:
            ok = grafo.remover_aresta(rem_aid)
            if ok:
                st.success(f"Aresta {rem_aid} removida")
            else:
                st.error("ID de aresta não encontrado")

# ----------------------------
# Algoritmos
# ----------------------------
elif menu_principal == "Algoritmos":
    st.subheader("Execução de algoritmos")

    alg = st.selectbox("Escolha o algoritmo", ["Prim (AGM)", "BFS", "DFS", "Roy (SCCs)"])
    start_vert = st.text_input("Vértice inicial (quando aplicável)", key="start_vert_alg")

    if st.button("Executar algoritmo"):
        try:
            if alg == "Prim (AGM)":
                T, Tmin, total = grafo.prim(start_vert if start_vert else None)
                st.write("Vértices em T:", sorted(list(T)))
                st.write("Arestas Tmin (ids):", Tmin)
                st.write("Peso total:", total)
                st.session_state.ultimo_destaque = {"tipo": "prim", "arestas": Tmin}

            elif alg == "BFS":
                pai, ordem, exploradas = grafo.bfs(start_vert)
                st.write("Ordem BFS:", ordem)
                st.write("Mapa de pais:", pai)
                st.session_state.ultimo_destaque = {
                    "tipo": "bfs",
                    "arestas_arvore": [(pai[k], k) for k in pai if pai[k]]
                }

            elif alg == "DFS":
                pai, ordem, exploradas = grafo.dfs(start_vert)
                st.write("Ordem DFS:", ordem)
                st.write("Mapa de pais:", pai)
                st.session_state.ultimo_destaque = {
                    "tipo": "dfs",
                    "arestas_arvore": [(pai[k], k) for k in pai if pai[k]]
                }

            elif alg == "Roy (SCCs)":
                sccs = grafo.roy()
                st.write("Componentes fortemente conexas:")
                for i, s in enumerate(sccs, 1):
                    st.write(f"S{i} = {sorted(list(s))}")
                st.session_state.ultimo_destaque = {
                    "tipo": "scc",
                    "conjuntos": [list(s) for s in sccs]
                }
        except Exception as e:
            st.error(str(e))

# ----------------------------
# Matrizes
# ----------------------------
elif menu_principal == "Matrizes":
    st.subheader("Matriz de Adjacência")
    verts, mat = grafo.matriz_adjacencia()
    if verts:
        df = pd.DataFrame(mat, index=verts, columns=verts)
        st.dataframe(df)

    st.subheader("Matriz de Incidência")
    vlist, edges, inc = grafo.matriz_incidencia()
    if vlist and edges:
        df2 = pd.DataFrame(inc, index=vlist, columns=edges)
        st.dataframe(df2)

# ----------------------------
# Visualização
# ----------------------------
st.header("Visualização do grafo")
net = Network(height="650px", width="100%", directed=grafo.direcionado)

ultimo = st.session_state.get("ultimo_destaque", None)

# adicionar nós
for n in sorted(grafo.vertices):
    cor = None
    if ultimo and ultimo["tipo"] == "scc":
        cores = ["#f1c40f","#2ecc71","#e74c3c","#9b59b6","#3498db","#e67e22"]
        for i, conj in enumerate(ultimo["conjuntos"]):
            if n in conj:
                cor = cores[i % len(cores)]
                break
    net.add_node(n, label=str(n), color=cor)

# adicionar arestas (com destaque se necessário)
for aid, a in grafo.arestas.items():
    cor, largura, titulo = "#848484", 1, f"{aid} ({a.peso})"

    if ultimo:
        if ultimo["tipo"] == "prim" and aid in ultimo.get("arestas", []):
            cor, largura, titulo = "red", 4, f"MST {aid}"
        elif ultimo["tipo"] in ("bfs", "dfs"):
            if (a.origem, a.destino) in ultimo.get("arestas_arvore", []):
                cor, largura, titulo = "blue", 3, "tree-edge"

    net.add_edge(
        a.origem, a.destino,
        title=titulo,
        font={"align": "horizontal", "size": 14, "color": "#000000"},
        label=str(a.peso),
        id=aid,
        color=cor,
        width=largura
    )

net.toggle_physics(True)
path = "temp_graph.html"
net.save_graph(path)
with open(path, "r", encoding="utf-8") as f:
    html = f.read()
components.html(html, height=700, scrolling=True)
