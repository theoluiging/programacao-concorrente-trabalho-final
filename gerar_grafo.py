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
        # Quantidade de componentes (2 a 5, ajusta conforme tamanho)
        k = max(2, min(5, v // 5))
        tamanhos = [v // k] * k
        resto = v % k
        for i in range(resto):
            tamanhos[i] += 1

        G = nx.DiGraph()
        offset = 0
        for tam in tamanhos:
            # Gera um subgrafo conectado (aleatório)
            sub = nx.gnm_random_graph(
                tam,
                max(1, int(densidade * tam * (tam - 1) / 2)),
                directed=True
            )

            # Reindexar os nós para que não se sobreponham
            mapeamento = {n: n + offset for n in sub.nodes()}
            sub = nx.relabel_nodes(sub, mapeamento)
            G.update(sub)
            offset += tam

    elif tipo == "ciclo":
        G = nx.DiGraph()
        G.add_nodes_from(range(v))
        for i in range(v):
            G.add_edge(i, (i + 1) % v)

    elif tipo == "denso":
        G = nx.gnm_random_graph(v, int(0.9 * v * (v - 1)), directed=True)

    elif tipo == "esparso":
        # Gerar árvore (v-1 arestas)
        G = nx.random_unlabeled_tree(v, seed=seed)

    elif tipo == "isolado":
        G = nx.gnm_random_graph(v, int(densidade * v * (v - 1) / 3), directed=True)
        edges = list(G.edges())
        for e in random.sample(edges, max(1, len(edges) // 5)):
            G.remove_edge(*e)

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
