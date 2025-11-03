#!/usr/bin/env python3

"""
Script para avaliar o desempenho da solução concorrente
Mede tempo de execução, calcula speedup e eficiência
"""

import subprocess
import os
import csv
import statistics
from collections import defaultdict

# Configuração
REPETICOES = 5
THREADS = [1, 2, 4, 8]

TESTES = [
    ("simples_m.txt", "Médio (20 vértices)"),
    ("simples_g.txt", "Grande (100 vértices)"),
    ("denso_g.txt", "Denso (500 vértices)"),
]

def compilar():
    """Compila versões sequencial e concorrente"""
    print("Compilando versões sequencial e concorrente...")

    # Sequencial
    subprocess.run(["make", "clean"], cwd="Sequencial", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["make"], cwd="Sequencial", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Concorrente
    subprocess.run(["make", "clean"], cwd="Concorrente", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["make"], cwd="Concorrente", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("Compilação concluída!\n")

def extrair_tempo(output):
    """Extrai o tempo de execução da saída do programa"""
    for line in output.split('\n'):
        if "Tempo:" in line:
            try:
                return float(line.split("Tempo:")[1].strip())
            except:
                return None
    return None

def executar_sequencial(arquivo_teste):
    """Executa a versão sequencial e retorna o tempo"""
    with open(f"Testes/{arquivo_teste}", "r") as f:
        result = subprocess.run(
            ["./Sequencial/amd"],
            stdin=f,
            capture_output=True,
            text=True
        )
    return extrair_tempo(result.stdout)

def executar_concorrente(arquivo_teste, num_threads):
    """Executa a versão concorrente e retorna o tempo"""
    with open(f"Testes/{arquivo_teste}", "r") as f:
        result = subprocess.run(
            ["./Concorrente/amdc", str(num_threads)],
            stdin=f,
            capture_output=True,
            text=True
        )
    return extrair_tempo(result.stdout)

def contar_vertices(arquivo_teste):
    """Conta o número de vértices no arquivo de teste"""
    with open(f"Testes/{arquivo_teste}", "r") as f:
        primeira_linha = f.readline().strip().split()
        return int(primeira_linha[0])

def main():
    print("=" * 70)
    print("AVALIAÇÃO DE DESEMPENHO - AMD")
    print("=" * 70)
    print()

    compilar()

    # Cria diretório para resultados
    os.makedirs("resultados_desempenho", exist_ok=True)

    # Arquivo de saída
    resultado_csv = "resultados_desempenho/resultados.csv"

    with open(resultado_csv, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Arquivo", "Descrição", "Vértices", "Threads", "Repetição", "Tempo(s)", "Speedup", "Eficiência"])

        print("Iniciando benchmarks...")
        print("=" * 70)
        print()

        for arquivo, descricao in TESTES:
            vertices = contar_vertices(arquivo)

            print(f"Teste: {arquivo} - {descricao}")
            print("-" * 70)

            # Executa versão sequencial
            print(f"  Sequencial: ", end="", flush=True)
            tempos_seq = []

            for r in range(1, REPETICOES + 1):
                tempo = executar_sequencial(arquivo)
                if tempo is None:
                    print("Erro!")
                    continue

                tempos_seq.append(tempo)
                writer.writerow([arquivo, descricao, vertices, 1, r, f"{tempo:.6f}", "1.0000", "1.0000"])
                print(".", end="", flush=True)

            media_seq = statistics.mean(tempos_seq) if tempos_seq else 0
            print(f" Média: {media_seq:.6f}s")

            # Executa versões concorrentes
            for t in THREADS:
                if t == 1:
                    continue

                print(f"  Concorrente ({t} threads): ", end="", flush=True)
                tempos_conc = []

                for r in range(1, REPETICOES + 1):
                    tempo = executar_concorrente(arquivo, t)
                    if tempo is None:
                        print("Erro!")
                        continue

                    tempos_conc.append(tempo)
                    speedup = media_seq / tempo if tempo > 0 else 0
                    eficiencia = speedup / t if t > 0 else 0

                    writer.writerow([arquivo, descricao, vertices, t, r, f"{tempo:.6f}", f"{speedup:.4f}", f"{eficiencia:.4f}"])
                    print(".", end="", flush=True)

                media_conc = statistics.mean(tempos_conc) if tempos_conc else 0
                speedup_medio = media_seq / media_conc if media_conc > 0 else 0
                eficiencia_media = speedup_medio / t if t > 0 else 0

                print(f" Média: {media_conc:.6f}s (Speedup: {speedup_medio:.4f}x, Eficiência: {eficiencia_media:.4f})")

            print()

    print("=" * 70)
    print(f"Resultados salvos em: {resultado_csv}")
    print("=" * 70)
    print()

    # Gera tabela resumo
    print("Gerando tabela resumo...")
    subprocess.run(["python3", "gerar_tabela.py", resultado_csv])

if __name__ == "__main__":
    main()
