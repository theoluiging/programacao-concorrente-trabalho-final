#!/usr/bin/env python3

"""
Script para gerar tabelas resumidas a partir dos resultados de benchmark
"""

import csv
import sys
from collections import defaultdict

def calcular_media(valores):
    """Calcula a média de uma lista de valores"""
    return sum(valores) / len(valores) if valores else 0

def gerar_tabela_resumo(arquivo_csv):
    """Gera tabela resumo com médias de tempo, speedup e eficiência"""

    # Dicionário para armazenar dados: [arquivo][threads] = [tempos]
    dados = defaultdict(lambda: defaultdict(list))
    info_testes = {}  # arquivo -> (descrição, vértices)

    # Lê o arquivo CSV
    with open(arquivo_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            arquivo = row['Arquivo']
            descricao = row['Descrição']
            vertices = row['Vértices']
            threads = int(row['Threads'])
            tempo = float(row['Tempo(s)'])
            speedup = float(row['Speedup'])
            eficiencia = float(row['Eficiência'])

            info_testes[arquivo] = (descricao, vertices)
            dados[arquivo][threads].append({
                'tempo': tempo,
                'speedup': speedup,
                'eficiencia': eficiencia
            })

    # Gera tabela formatada
    print("\n" + "="*100)
    print("TABELA RESUMO - RESULTADOS DE DESEMPENHO")
    print("="*100)
    print()

    for arquivo in sorted(dados.keys()):
        descricao, vertices = info_testes[arquivo]
        print(f"Teste: {arquivo} - {descricao} ({vertices} vértices)")
        print("-" * 100)
        print(f"{'Threads':<10} {'Tempo Médio (s)':<20} {'Speedup':<15} {'Eficiência':<15}")
        print("-" * 100)

        for threads in sorted(dados[arquivo].keys()):
            medidas = dados[arquivo][threads]

            tempo_medio = calcular_media([m['tempo'] for m in medidas])
            speedup_medio = calcular_media([m['speedup'] for m in medidas])
            eficiencia_media = calcular_media([m['eficiencia'] for m in medidas])

            print(f"{threads:<10} {tempo_medio:<20.6f} {speedup_medio:<15.4f} {eficiencia_media:<15.4f}")

        print()

    print("="*100)
    print()

    # Salva tabela em arquivo texto
    arquivo_saida = 'resultados_desempenho/tabela_resumo.txt'
    with open(arquivo_saida, 'w') as f:
        f.write("="*100 + "\n")
        f.write("TABELA RESUMO - RESULTADOS DE DESEMPENHO\n")
        f.write("="*100 + "\n\n")

        for arquivo in sorted(dados.keys()):
            descricao, vertices = info_testes[arquivo]
            f.write(f"Teste: {arquivo} - {descricao} ({vertices} vértices)\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Threads':<10} {'Tempo Médio (s)':<20} {'Speedup':<15} {'Eficiência':<15}\n")
            f.write("-" * 100 + "\n")

            for threads in sorted(dados[arquivo].keys()):
                medidas = dados[arquivo][threads]

                tempo_medio = calcular_media([m['tempo'] for m in medidas])
                speedup_medio = calcular_media([m['speedup'] for m in medidas])
                eficiencia_media = calcular_media([m['eficiencia'] for m in medidas])

                f.write(f"{threads:<10} {tempo_medio:<20.6f} {speedup_medio:<15.4f} {eficiencia_media:<15.4f}\n")

            f.write("\n")

        f.write("="*100 + "\n")

    print(f"Tabela salva em: {arquivo_saida}")

if __name__ == "__main__":
    arquivo_csv = 'resultados_desempenho/resultados.csv'

    if len(sys.argv) > 1:
        arquivo_csv = sys.argv[1]

    try:
        gerar_tabela_resumo(arquivo_csv)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_csv}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        sys.exit(1)
