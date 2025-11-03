#!/bin/bash

# Script para coletar informações do sistema para o relatório

echo "====================================="
echo "INFORMAÇÕES DO SISTEMA"
echo "====================================="
echo ""

# Informações do processador
echo "Processador:"
echo "------------"
if command -v lscpu &> /dev/null; then
    echo "  Modelo: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
    echo "  Arquitetura: $(lscpu | grep 'Architecture' | cut -d':' -f2 | xargs)"
    echo "  CPU(s): $(lscpu | grep '^CPU(s):' | cut -d':' -f2 | xargs)"
    echo "  Thread(s) por núcleo: $(lscpu | grep 'Thread(s) per core' | cut -d':' -f2 | xargs)"
    echo "  Núcleo(s) por socket: $(lscpu | grep 'Core(s) per socket' | cut -d':' -f2 | xargs)"
    echo "  Socket(s): $(lscpu | grep 'Socket(s)' | cut -d':' -f2 | xargs)"
    echo "  Frequência máxima: $(lscpu | grep 'CPU max MHz' | cut -d':' -f2 | xargs) MHz"
else
    echo "  Núcleos disponíveis: $(nproc)"
    if [ -f /proc/cpuinfo ]; then
        echo "  Modelo: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d':' -f2 | xargs)"
    fi
fi

echo ""

# Sistema Operacional
echo "Sistema Operacional:"
echo "--------------------"
if [ -f /etc/os-release ]; then
    echo "  Distribuição: $(grep 'PRETTY_NAME' /etc/os-release | cut -d'=' -f2 | tr -d '"')"
fi
echo "  Kernel: $(uname -s) $(uname -r)"
echo "  Arquitetura: $(uname -m)"

echo ""

# Memória RAM
echo "Memória:"
echo "--------"
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -h | grep 'Mem:' | awk '{print $2}')
    echo "  Total: $TOTAL_MEM"
else
    echo "  (informação não disponível)"
fi

echo ""

# Informações sobre compilação
echo "Compilador:"
echo "-----------"
if command -v gcc &> /dev/null; then
    echo "  GCC: $(gcc --version | head -1)"
fi

if command -v python3 &> /dev/null; then
    echo "  Python: $(python3 --version)"
fi

echo ""
echo "====================================="
echo ""

# Salva em arquivo
INFO_FILE="resultados_desempenho/info_sistema.txt"
mkdir -p resultados_desempenho

{
    echo "====================================="
    echo "INFORMAÇÕES DO SISTEMA"
    echo "====================================="
    echo ""
    echo "Processador:"
    echo "------------"
    if command -v lscpu &> /dev/null; then
        echo "  Modelo: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
        echo "  Arquitetura: $(lscpu | grep 'Architecture' | cut -d':' -f2 | xargs)"
        echo "  CPU(s): $(lscpu | grep '^CPU(s):' | cut -d':' -f2 | xargs)"
        echo "  Thread(s) por núcleo: $(lscpu | grep 'Thread(s) per core' | cut -d':' -f2 | xargs)"
        echo "  Núcleo(s) por socket: $(lscpu | grep 'Core(s) per socket' | cut -d':' -f2 | xargs)"
        echo "  Socket(s): $(lscpu | grep 'Socket(s)' | cut -d':' -f2 | xargs)"
    else
        echo "  Núcleos disponíveis: $(nproc)"
    fi
    echo ""
    echo "Sistema Operacional:"
    echo "--------------------"
    if [ -f /etc/os-release ]; then
        echo "  Distribuição: $(grep 'PRETTY_NAME' /etc/os-release | cut -d'=' -f2 | tr -d '"')"
    fi
    echo "  Kernel: $(uname -s) $(uname -r)"
    echo ""
    echo "Memória:"
    echo "--------"
    if command -v free &> /dev/null; then
        echo "  Total: $(free -h | grep 'Mem:' | awk '{print $2}')"
    fi
    echo ""
    echo "Compilador:"
    echo "-----------"
    if command -v gcc &> /dev/null; then
        echo "  GCC: $(gcc --version | head -1)"
    fi
    echo ""
} > "$INFO_FILE"

echo "Informações salvas em: $INFO_FILE"
