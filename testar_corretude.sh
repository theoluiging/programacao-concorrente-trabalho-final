#!/bin/bash

# Script para testar a corretude da solução concorrente
# Compara resultados da versão sequencial com a versão concorrente

echo "====================================="
echo "TESTES DE CORRETUDE - AMD"
echo "====================================="
echo ""

# Compila os programas
echo "Compilando versões sequencial e concorrente..."
cd Sequencial && make clean && make && cd ..
cd Concorrente && make clean && make && cd ..
echo ""

# Define os casos de teste
TESTES=(
    "simples_p.txt:3"
    "ciclo_p.txt:3"
    "arvore_p.txt:5"
    "desconectado_p.txt:2"
    "isolado_p.txt:3"
    "simples_m.txt:20"
    "simples_g.txt:100"
    "denso_g.txt:500"
)

# Define número de threads para testar
THREADS=(1 2 4 8)

# Cria diretório para resultados
mkdir -p resultados_corretude

# Arquivo de saída
RESULTADO="resultados_corretude/relatorio_corretude.txt"

# Função para extrair apenas a solução (ignorando o tempo)
extrair_solucao() {
    grep "Solucao:" | awk '{print $2}' | tr -d '.'
}

# Inicializa arquivo de resultados
{
    echo "====================================="
    echo "TESTES DE CORRETUDE - AMD"
    echo "====================================="
    echo ""
    echo "Data: $(date)"
    echo ""
} > "$RESULTADO"

echo "Executando testes de corretude..."
echo "=================================="
echo ""

TOTAL_TESTES=0
TESTES_OK=0
TESTES_FALHA=0

# Para cada caso de teste
for TESTE_INFO in "${TESTES[@]}"; do
    ARQUIVO=$(echo $TESTE_INFO | cut -d':' -f1)
    VERTICES=$(echo $TESTE_INFO | cut -d':' -f2)

    echo "Teste: $ARQUIVO ($VERTICES vértices)"
    echo "-----------------------------------"

    # Salva no arquivo também
    {
        echo "Teste: $ARQUIVO ($VERTICES vértices)"
        echo "-----------------------------------"
    } >> "$RESULTADO"

    # Executa versão sequencial
    SOL_SEQ=$(./Sequencial/amd < Testes/$ARQUIVO | extrair_solucao)

    if [ -z "$SOL_SEQ" ]; then
        echo "  ❌ Erro ao executar versão sequencial"
        echo "  ❌ Erro ao executar versão sequencial" >> "$RESULTADO"
        ((TESTES_FALHA++))
        continue
    fi

    echo "  Solução sequencial: $SOL_SEQ"
    echo "  Solução sequencial: $SOL_SEQ" >> "$RESULTADO"

    # Testa com diferentes números de threads
    for T in "${THREADS[@]}"; do
        SOL_CONC=$(./Concorrente/amdc $T < Testes/$ARQUIVO | extrair_solucao)

        ((TOTAL_TESTES++))

        if [ "$SOL_SEQ" == "$SOL_CONC" ]; then
            echo "  ✓ Concorrente ($T threads): $SOL_CONC [OK]"
            echo "  ✓ Concorrente ($T threads): $SOL_CONC [OK]" >> "$RESULTADO"
            ((TESTES_OK++))
        else
            echo "  ✗ Concorrente ($T threads): $SOL_CONC [FALHA - esperado $SOL_SEQ]"
            echo "  ✗ Concorrente ($T threads): $SOL_CONC [FALHA - esperado $SOL_SEQ]" >> "$RESULTADO"
            ((TESTES_FALHA++))
        fi
    done

    echo ""
    echo "" >> "$RESULTADO"
done

echo "====================================="
echo "RESUMO DOS TESTES"
echo "====================================="
echo "Total de testes: $TOTAL_TESTES"
echo "Testes OK: $TESTES_OK"
echo "Testes com falha: $TESTES_FALHA"
echo ""

# Salva resumo no arquivo
{
    echo "====================================="
    echo "RESUMO DOS TESTES"
    echo "====================================="
    echo "Total de testes: $TOTAL_TESTES"
    echo "Testes OK: $TESTES_OK"
    echo "Testes com falha: $TESTES_FALHA"
    echo ""
} >> "$RESULTADO"

if [ $TESTES_FALHA -eq 0 ]; then
    echo "✓ TODOS OS TESTES PASSARAM!"
    echo "✓ TODOS OS TESTES PASSARAM!" >> "$RESULTADO"
    echo ""
    echo "Resultados salvos em: $RESULTADO"
    exit 0
else
    echo "✗ ALGUNS TESTES FALHARAM"
    echo "✗ ALGUNS TESTES FALHARAM" >> "$RESULTADO"
    echo ""
    echo "Resultados salvos em: $RESULTADO"
    exit 1
fi
