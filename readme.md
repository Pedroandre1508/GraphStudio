# ⚛️ GraphStudio

Sistema avançado para manipulação e análise de grafos desenvolvido para a disciplina de Grafos.

**Desenvolvido por:** Pedro André e Eduardo Ueda  
**Instituição:** UNIVALI - Ciência da Computação 2025/2  
**Professora:** Fernanda Cunha

### 🎨 Visualização Gráfica (Requisito Obrigatório)
- ✅ Grafo original renderizado com pyvis
- ✅ Welsh-Powell: vértices coloridos
- ✅ A*: caminho destacado em azul com largura maior
- ✅ Interface profissional com Streamlit

## 🚀 Como Executar

### 1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

### 2. **Rodar aplicação:**
```bash
streamlit run streamlit_app/app.py
```

### 3. **Acessar:** 
http://localhost:8501

## 📂 Estrutura do Projeto

```
GraphStudio-main/
├── backend/
│   ├── grafo.py           # Classe principal com algoritmos
│   └── importador.py      # Importação de CSV
├── data/
│   ├── cidades.csv        # Mapa do Paraná (lat/long)
│   ├── k33_nao_planar.csv # Grafo K₃,₃ (teste de planaridade)
│   └── teste.csv          # Outros testes
├── streamlit_app/
│   └── app.py             # Interface Streamlit
└── requirements.txt       # Dependências
```

## ⚙️ Funcionalidades Completas

### Algoritmos Implementados
- **Prim** - Árvore Geradora Mínima
- **BFS** - Busca em Largura  
- **DFS** - Busca em Profundidade
- **Roy** - Componentes Fortemente Conexas
- **A*** - Caminho mínimo com heurística Manhattan
- **Welsh-Powell** - Coloração de vértices
- **Verificação de Planaridade** - Teoremas de Euler

## 📊 Formato do CSV

```csv
origem,destino,peso,lat_origem,long_origem,lat_destino,long_destino
Arad,Zerind,75,46.1667,21.3167,46.6167,21.5167
Arad,Timisoara,118,46.1667,21.3167,45.7597,21.23
```

- **Obrigatórios:** origem, destino, peso
- **Opcionais:** lat_origem, long_origem, lat_destino, long_destino (para A*)

## 📋 Requisitos Técnicos

- Python 3.8+
- streamlit >= 1.10
- pyvis >= 0.2.1
- pandas >= 1.3

---
**© 2025 - UNIVALI - Ciência da Computação**

