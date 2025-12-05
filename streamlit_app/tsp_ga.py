import streamlit as st
import pandas as pd
import os
from backend.genetic_tsp import GeneticTSP
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATA_DIR = os.path.abspath(DATA_DIR)

def list_data_files():
    files = []
    if os.path.isdir(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.lower().endswith('.csv'):
                files.append(os.path.join(DATA_DIR, f))
    return files

def load_edges(path):
    return pd.read_csv(path)

def show_pyvis_route(cities, dist_matrix, route_idx, title="Melhor rota"):
    # build pyvis network and highlight route edges
    net = Network(height="650px", width="100%", notebook=False)
    # add nodes with labels
    for i, city in enumerate(cities):
        net.add_node(i, label=city)
    # add all edges (light)
    n = len(cities)
    for i in range(n):
        for j in range(i+1, n):
            w = dist_matrix[i][j]
            if w < 10**8:
                net.add_edge(i, j, value=1, title=str(w), color="#B0B0B0")
    # highlight route edges
    for k in range(len(route_idx)-1):
        a = route_idx[k]; b = route_idx[k+1]
        net.add_edge(a, b, color="red", width=3)
    # close loop
    net.add_edge(route_idx[-1], route_idx[0], color="red", width=3)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    tmpfile.close()
    # usar save_graph / write_html em vez de show() para evitar notebook=True no pyvis
    try:
        net.save_graph(tmpfile.name)
    except Exception:
        # fallback: write_html com notebook=False
        try:
            net.write_html(tmpfile.name, notebook=False)
        except Exception as e:
            raise
    return tmpfile.name

def run_app():
    st.header("Algoritmo Genético — Problema do Caixeiro Viajante (PCV)")

    data_files = list_data_files()
    if not data_files:
        st.warning("Nenhum arquivo CSV encontrado na pasta data/. Coloque um arquivo com colunas origem,destino,peso")
        return
    selected = st.selectbox("Escolha o arquivo de grafo (CSV)", data_files, format_func=lambda p: os.path.basename(p))
    df = load_edges(selected)
    st.write("Número de arestas:", len(df))

    col1, col2 = st.columns(2)
    with col1:
        pop_size = st.number_input("Tamanho da população (>=100)", value=200, min_value=100, step=10)
        generations = st.number_input("Gerações (>=20)", value=50, min_value=20, step=10)
        crossover_rate = st.slider("Taxa de cruzamento", 0.0, 1.0, 0.7)
    with col2:
        mutation_rate = st.number_input("Taxa de mutação (0.0-1.0)", value=0.01, min_value=0.0, max_value=1.0, step=0.001)
        elitism = st.number_input("Elitismo (quantos mantêm intactos)", value=2, min_value=0, max_value=10, step=1)
        show_pop = st.checkbox("Mostrar indivíduos por geração (top N)", value=False)
        top_n = 20
        if show_pop:
            top_n = st.number_input("Mostrar top N por geração", value=10, min_value=1, max_value=100, step=1)

    # instantiate GA
    try:
        ga = GeneticTSP(df)
    except Exception as e:
        st.error(f"Erro ao construir grafo: {e}")
        return

    n = ga.n
    st.write(f"Cidades detectadas: {n} (máx {n} índices 0..{n-1})")
    # choose fixed crossover points
    st.write("Escolha 2 pontos fixos para PMX (índices baseados em permutação 0..n-1)")
    default_c1 = max(1, n//4)
    default_c2 = min(n-2, (n*3)//4)
    c1 = st.number_input("Ponto de cruzamento 1 (cx1)", value=default_c1, min_value=0, max_value=max(0,n-1), step=1)
    c2 = st.number_input("Ponto de cruzamento 2 (cx2)", value=default_c2, min_value=0, max_value=max(0,n-1), step=1)
    if c2 <= c1:
        st.warning("cx2 deve ser maior que cx1 — ajustando automaticamente")
        c2 = min(n-1, c1+1)

    fixed_start = st.selectbox("Escolher cidade de partida (opcional)", options=["(aleatório)"]+ga.cities)
    fixed_start_idx = None
    if fixed_start != "(aleatório)":
        fixed_start_idx = ga.index[fixed_start]

    if st.button("Executar AG"):
        progress_bar = st.progress(0)
        status = st.empty()
        plot_placeholder = st.empty()
        best_cost_chart = []
        gens = []
        best_route_final = None
        best_cost_final = None

        def show_population_callback(gen, population, costs):
            # called every generation
            if show_pop:
                rows = []
                for i in range(min(top_n, len(population))):
                    route_names = [ga.cities[idx] for idx in population[i]]
                    rows.append({"rank": i+1, "rota": " -> ".join(route_names), "custo": costs[i]})
                plot_placeholder.table(rows)
            # update progress
            progress = int(100*gen/generations)
            progress_bar.progress(min(progress,100))
            status.text(f"Geração {gen}/{generations} — melhor custo desta geração: {costs[0]:.3f}")

        for out in ga.evolve(pop_size=pop_size,
                             generations=generations,
                             crossover_rate=crossover_rate,
                             mutation_rate=mutation_rate,
                             elitism=elitism,
                             cx_points=(int(c1),int(c2)),
                             show_population_callback=show_population_callback,
                             fixed_start_idx=fixed_start_idx):
            gens.append(out['generation'])
            best_cost_chart.append(out['best_cost'])
            best_route_final = out['best_overall_idx']
            best_cost_final = out['best_overall_cost']

        st.success(f"Execução finalizada — melhor custo: {best_cost_final:.3f}")
        # show best route textual
        route_names = [ga.cities[idx] for idx in best_route_final]
        st.write("Melhor rota encontrada (ciclo):")
        st.write(" -> ".join(route_names) + " -> " + route_names[0])
        # draw pyvis graph
        html_file = show_pyvis_route(ga.cities, ga.dist, best_route_final, title="Melhor rota GA")
        st.markdown("### Visualização da rota (grafo)")
        components.html(open(html_file, 'r', encoding='utf-8').read(), height=700)

        # show convergence chart
        st.line_chart({"best_cost": best_cost_chart}, use_container_width=True)

# export for app.py
def mount():
    run_app()

if __name__ == "__main__":
    run_app()