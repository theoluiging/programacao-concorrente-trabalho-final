import sys
import random
import networkx as nx
import os
from visualizar_grafo import desenhar_grafo

def gerar_grafo(tipo, v, peso_max=10, densidade=0.2, seed=None):
    random.seed(seed)

    if seed is not None:
        nx.utils.seed_sequence.SeedSequence(seed)

    if tipo == "conectado":
        G = nx.gnm_random_graph(v, int(densidade * v * (v - 1)), directed=True)
        # Garantir conectividade
        while not nx.is_strongly_connected(G):
            G = nx.gnm_random_graph(v, int(densidade * v * (v - 1)), directed=True)

    elif tipo == "desconectado":
        G = nx.gnm_random_graph(v, int(densidade * v * (v - 1) / 3), directed=True)
        # Gera várias componentes desconectadas
        comps = list(nx.weakly_connected_components(G))
        if len(comps) < 2:
            # Forçar desconexão removendo algumas arestas
            edges = list(G.edges())
            for e in random.sample(edges, len(edges) // 4):
                G.remove_edge(*e)

    elif tipo == "ciclo":
        G = nx.DiGraph()
        G.add_nodes_from(range(v))
        for i in range(v):
            G.add_edge(i, (i + 1) % v)

    elif tipo == "denso":
        G = nx.gnm_random_graph(v, int(0.9 * v * (v - 1)), directed=True)

    elif tipo == "esparso":
        # Gerar árvore (v-1 arestas)
        G = nx.random_tree(v, seed=seed, create_using=nx.DiGraph())
        # Direcionar aleatoriamente
        for (u, v_) in list(G.edges()):
            if random.random() < 0.5:
                G.remove_edge(u, v_)
                G.add_edge(v_, u)

    elif tipo == "isolado":
        G = nx.gnm_random_graph(v, int(densidade * v * (v - 1)), directed=True)
        # Remove arestas de alguns vértices
        isolados = random.sample(G.nodes(), max(1, v // 10))
        for n in isolados:
            for viz in list(G.successors(n)) + list(G.predecessors(n)):
                G.remove_edge(n, viz)
                G.remove_edge(viz, n)

    else:
        raise ValueError(f"Tipo de grafo '{tipo}' não reconhecido.")

    # Adicionar pesos
    for (u, v_) in G.edges():
        G[u][v_]["weight"] = random.randint(1, peso_max)

    return G

def salvar_grafo(G, nome_arquivo):
    """Salva o grafo no formato: v e / origem destino peso"""
    with open(nome_arquivo, "w") as f:
        f.write(f"{G.number_of_nodes()} {G.number_of_edges()}\n")
        for (u, v, dados) in G.edges(data=True):
            f.write(f"{u} {v} {int(dados['weight'])}\n")
    print(f"Grafo salvo em '{nome_arquivo}'")

def main():
    if len(sys.argv) < 4:
        print("Uso: python gerar_grafo.py <tipo> <num_vertices> <saida.txt> [peso_max] [densidade] [--seed N] [--show]")
        print("Tipos: conectado, desconectado, ciclo, denso, esparso, isolado")
        sys.exit(1)

    tipo = sys.argv[1].lower()
    v = int(sys.argv[2])
    saida = os.path.join("Testes",sys.argv[3])
    peso_max = int(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else 10
    densidade = float(sys.argv[5]) if len(sys.argv) > 5 and not sys.argv[5].startswith("--") else 0.2

    # Parâmetros opcionais
    seed = None
    show = False
    for i, arg in enumerate(sys.argv):
        if arg == "--seed" and i + 1 < len(sys.argv):
            seed = int(sys.argv[i + 1])
        if arg == "--show":
            show = True

    G = gerar_grafo(tipo, v, peso_max, densidade, seed)
    salvar_grafo(G, saida)

    if show:
        desenhar_grafo(G, titulo=f"{tipo.capitalize()} ({v} vértices)")

if __name__ == "__main__":
    main()
