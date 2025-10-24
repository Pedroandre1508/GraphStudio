import os
import sys
import base64
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from backend.importador import importar_csv
from backend.grafo import Grafo
from pyvis.network import Network
import tempfile

st.set_page_config(
    page_title="GraphStudio",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Função para carregar imagem como base64
# ----------------------------
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

# Carregar logo
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
logo_base64 = get_base64_image(logo_path)

# ----------------------------
# CSS Customizado
# ----------------------------
st.markdown("""
    <style>
    /* Remover padding do container principal */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 4rem;
        max-width: 100%;
    }
    
    /* Cabeçalho Principal - Largura Total */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem 2rem;
        margin: -1rem -5rem 2rem -5rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        text-align: center;
        width: calc(100% + 10rem);
    }
    
    .main-header .logo-img {
        width: 200px;
        height: 200px;
        margin: 0 auto;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
    
    .main-header h1 {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }
    
    .main-header .subtitle {
        color: #e0e7ff;
        font-size: 1.3rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Rodapé */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        padding: 0.8rem;
        font-size: 0.9rem;
        z-index: 999;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    
    .footer a {
        color: #fff;
        text-decoration: none;
        font-weight: 600;
    }
    
    .footer a:hover {
        color: #e0e7ff;
        text-decoration: underline;
    }
    
    /* Estilo dos botões */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Ajustar margens do conteúdo */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    /* Fundo escuro para o resto */
    .stApp {
        background-color: #0e0e0e;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Inicialização
# ----------------------------
if "grafo" not in st.session_state:
    st.session_state.grafo = Grafo()

grafo = st.session_state.grafo

if logo_base64:
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">'
else:
    logo_html = '<div style="font-size: 5rem; margin-bottom: 1rem;">⚛️</div>'

st.markdown(f"""
    <div class="main-header">
        {logo_html}
    </div>
""", unsafe_allow_html=True)

# ----------------------------
# Upload e importação de CSV
# ----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Importar Grafo")
uploaded_file = st.sidebar.file_uploader("Escolha um arquivo CSV", type=['csv'])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    st.session_state.grafo = importar_csv(tmp_path)
    st.session_state.pop("ultimo_destaque", None)
    st.success(f"Grafo importado de **{uploaded_file.name}**")
    grafo = st.session_state.grafo

st.sidebar.markdown("---")

# ----------------------------
# Menu Principal
# ----------------------------
menu_principal = st.sidebar.radio(
    "Menu Principal",
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
    st.subheader("Algoritmos")

    opc = st.selectbox("Escolha o algoritmo", [
        "Prim (Árvore Geradora Mínima)",
        "BFS",
        "DFS",
        "A* (caminho mínimo)",
        "Welsh–Powell (coloração)",
        "Verificar planaridade"
    ])

    verts = sorted(grafo.vertices)

    # mostra apenas quando for necessário
    inicio = None
    destino = None
    if opc in ("Prim (Árvore Geradora Mínima)", "BFS", "DFS"):
        if verts:
            inicio = st.selectbox("Vértice inicial", verts, index=0)
        else:
            st.info("Grafo vazio — adicione vértices/arestas para usar este algoritmo.")
    if opc == "A* (caminho mínimo)":
        if len(verts) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                inicio = st.selectbox("Origem", verts, index=0)
            with col2:
                destino = st.selectbox("Destino", verts, index=min(1, len(verts)-1))
        else:
            st.info("Precisam existir pelo menos 2 vértices para executar A*.")

    if st.button("Executar"):
        try:
            if opc == "Prim (Árvore Geradora Mínima)":
                if inicio is None:
                    st.error("Selecione um vértice inicial.")
                else:
                    T, arestas, total = grafo.prim(inicio)
                    st.session_state["ultimo_destaque"] = {"tipo": "prim", "arestas": arestas}
                    st.success(f"Árvore geradora mínima com custo {total:.2f}. Arestas: {arestas}")

            elif opc == "BFS":
                if inicio is None:
                    st.error("Selecione um vértice inicial.")
                else:
                    pai, ordem, exploradas = grafo.bfs(inicio)
                    # convertendo exploradas para lista de pares
                    exploradas_list = list(exploradas)
                    st.session_state["ultimo_destaque"] = {"tipo": "bfs", "arestas": exploradas_list}
                    st.success(f"Ordem BFS: {ordem}")

            elif opc == "DFS":
                if inicio is None:
                    st.error("Selecione um vértice inicial.")
                else:
                    pai, ordem, exploradas = grafo.dfs(inicio)
                    exploradas_list = list(exploradas)
                    st.session_state["ultimo_destaque"] = {"tipo": "dfs", "arestas": exploradas_list}
                    st.success(f"Ordem DFS: {ordem}")

            elif opc == "A* (caminho mínimo)":
                if inicio is None or destino is None:
                    st.error("Selecione origem e destino.")
                elif inicio == destino:
                    st.info("Origem e destino iguais — custo 0.")
                    st.session_state["ultimo_destaque"] = {"tipo": "aestrela", "caminho": [inicio], "destino": destino}
                else:
                    caminho, custo = grafo.a_estrela(inicio, destino)
                    if caminho:
                        st.session_state["ultimo_destaque"] = {
                            "tipo": "aestrela", 
                            "caminho": caminho,
                            "destino": destino
                        }
                        st.success(f"Caminho encontrado: {' → '.join(caminho)}  (custo total: {custo:.2f})")
                    else:
                        st.warning("Nenhum caminho encontrado.")

            elif opc == "Welsh–Powell (coloração)":
                cores = grafo.welsh_powell()
                st.session_state["ultimo_destaque"] = {"tipo": "coloracao", "cores": cores}
                st.success(f"Cores atribuídas a {len(cores)} vértices.")

            elif opc == "Verificar planaridade":
                planar, msg = grafo.verificar_planaridade()
                if planar:
                    st.success(msg)
                else:
                    st.warning(msg)

        except Exception as e:
            st.error(f"Erro ao executar {opc}: {e}")

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
    elif ultimo and ultimo["tipo"] == "coloracao":
        cores = ultimo["cores"]
        paleta = ["#1abc9c", "#3498db", "#9b59b6", "#e74c3c", "#f1c40f", "#2ecc71"]
        if n in cores:
            cor = paleta[(cores[n] - 1) % len(paleta)]
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
        elif ultimo and ultimo["tipo"] == "aestrela":
            caminho = ultimo.get("caminho", [])
            for i in range(len(caminho)-1):
                if (a.origem == caminho[i] and a.destino == caminho[i+1]) or \
                   (not grafo.direcionado and a.destino == caminho[i] and a.origem == caminho[i+1]):
                    cor, largura = "blue", 4

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

# ----------------------------
# TABELAS A*
# ----------------------------
if ultimo and ultimo["tipo"] == "aestrela" and "destino" in ultimo:
    st.markdown("---")
    
    destino_atual = ultimo["destino"]
    st.subheader(f"Tabela Heurística h(n) - Destino: **{destino_atual}**")
    
    tabela_hn = grafo.calcular_tabela_heuristica(destino_atual)
    
    if tabela_hn:
        df_hn = pd.DataFrame([
            {"Vértice": v, "h(n)": f"{h:.2f}"}
            for v, h in sorted(tabela_hn.items(), key=lambda x: x[1])
        ])
        
        st.dataframe(
            df_hn,
            use_container_width=True,
            hide_index=True,
            height=min(400, len(df_hn) * 35 + 38)
        )
        
        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Total de Vértices", len(tabela_hn))
        with col_info2:
            min_h = min(tabela_hn.values())
            st.metric("h(n) Mínimo", f"{min_h:.2f}")
        with col_info3:
            max_h = max(tabela_hn.values())
            st.metric("h(n) Máximo", f"{max_h:.2f}")
    else:
        st.warning("Não há coordenadas definidas para calcular h(n)")
    
    st.markdown("---")
    
    caminho = ultimo.get("caminho", [])
    if len(caminho) > 0:
        st.subheader("Valores do Caminho Encontrado")
        
        g_acumulado = 0.0
        dados_caminho = []
        
        for i, cidade in enumerate(caminho):
            h_valor = tabela_hn.get(cidade, 0.0)
            f_valor = g_acumulado + h_valor
            dados_caminho.append({
                "Posição": i+1,
                "Cidade": cidade,
                "g(n)": f"{g_acumulado:.2f}",
                "h(n)": f"{h_valor:.2f}",
                "f(n)": f"{f_valor:.2f}"
            })
            
            # Calcular peso da aresta para próximo nó
            if i < len(caminho) - 1:
                proximo = caminho[i+1]
                for (viz, peso, _) in grafo.adjacencia[cidade]:
                    if viz == proximo:
                        g_acumulado += peso
                        break
        
        df_caminho = pd.DataFrame(dados_caminho)
        st.dataframe(df_caminho, use_container_width=True, hide_index=True)
        
        # Métricas do caminho
        col_cam1, col_cam2, col_cam3 = st.columns(3)
        with col_cam1:
            st.metric("Cidades no Caminho", len(caminho))
        with col_cam2:
            st.metric("Custo Total g(n)", f"{g_acumulado:.2f}")
        with col_cam3:
            ultimo_f = dados_caminho[-1]["f(n)"]
            st.metric("f(n) Final", ultimo_f)


st.markdown(f"""
    <div class="footer">
        Desenvolvido por <strong>Pedro André</strong> e <strong>Eduardo Ueda</strong> | 
        UNIVALI - Ciência da Computação 2025/2 | 
        Disciplina: Grafos
    </div>
""", unsafe_allow_html=True)
