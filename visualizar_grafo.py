import sys
import networkx as nx
import matplotlib.pyplot as plt

def ler_grafo(arquivo):
    """Lê um grafo no formato: v e / origem destino peso"""
    with open(arquivo, "r") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    v, e = map(int, linhas[0].split())
    G = nx.DiGraph()  # use nx.Graph() se seu grafo for não-dirigido
    G.add_nodes_from(range(v))

    for linha in linhas[1:]:
        try:
            a, b, w = map(float, linha.split())
            G.add_edge(int(a), int(b), weight=w)
        except ValueError:
            print(f"Ignorando linha inválida: {linha}")

    return G

def desenhar_grafo(G, titulo="Grafo", salvar_como=None):
    """Desenha o grafo com cores e pesos das arestas"""
    pos = nx.spring_layout(G, seed=42)  # layout automático

    # Identificar vértices isolados
    isolados = list(nx.isolates(G))
    normais = [n for n in G.nodes if n not in isolados]

    plt.figure(figsize=(8, 6))
    plt.title(titulo)

    # Arestas com pesos
    pesos = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edges(
        G,
        pos,
        arrowstyle='-|>',
        arrowsize=14,
        edge_color='gray',
        alpha=0.7,
        min_source_margin=15,
        min_target_margin=13
    )

    nx.draw_networkx_labels(G, pos, font_size=10)

    # Vértices
    nx.draw_networkx_nodes(G, pos, nodelist=normais, node_color='skyblue', node_size=600)
    nx.draw_networkx_nodes(G, pos, nodelist=isolados, node_color='lightcoral', node_size=600)

    # Rótulos de peso
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos, font_size=8)

    plt.axis("off")
    plt.tight_layout()

    if salvar_como:
        plt.savefig(salvar_como, dpi=300)
        print(f"Figura salva como {salvar_como}")
    else:
        plt.show()

def main():
    if len(sys.argv) < 2:
        print("Uso: python visualizar_grafo.py <arquivo_grafo> [--save nome.png]")
        sys.exit(1)

    arquivo = sys.argv[1]
    salvar = None
    if len(sys.argv) > 3 and sys.argv[2] == "--save":
        salvar = sys.argv[3]

    G = ler_grafo(arquivo)
    print(f"Grafo lido: {G.number_of_nodes()} vértices, {G.number_of_edges()} arestas")
    desenhar_grafo(G, titulo=arquivo, salvar_como=salvar)

if __name__ == "__main__":
    main()
