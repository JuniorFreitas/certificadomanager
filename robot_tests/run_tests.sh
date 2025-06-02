#!/bin/bash

# Script para execução dos testes Robot Framework
# Uso: ./run_tests.sh [smoke|regression|api|web|integration|all] [browser] [headless]

set -e

# Configurações padrão
TEST_TYPE="${1:-smoke}"
BROWSER="${2:-chrome}"
HEADLESS="${3:-true}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="results/${TEST_TYPE}_${TIMESTAMP}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Robot Framework Test Execution ===${NC}"
echo -e "${YELLOW}Test Type: ${TEST_TYPE}${NC}"
echo -e "${YELLOW}Browser: ${BROWSER}${NC}"
echo -e "${YELLOW}Headless: ${HEADLESS}${NC}"
echo -e "${YELLOW}Results Dir: ${RESULTS_DIR}${NC}"
echo ""

# Verificar se o diretório do projeto existe
if [ ! -f "../manage.py" ]; then
    echo -e "${RED}Erro: Script deve ser executado da pasta robot_tests${NC}"
    exit 1
fi

# Criar diretório de resultados
mkdir -p "$RESULTS_DIR"

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual...${NC}"
    python3 -m venv venv
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências se necessário
if [ ! -f "venv/.dependencies_installed" ]; then
    echo -e "${YELLOW}Instalando dependências...${NC}"
    pip install -r requirements.txt
    touch venv/.dependencies_installed
fi

# Verificar se o Django está rodando
if ! curl -s http://localhost:8000 > /dev/null; then
    echo -e "${YELLOW}Iniciando servidor Django...${NC}"
    cd ..
    python manage.py runserver 0.0.0.0:8000 &
    DJANGO_PID=$!
    cd robot_tests
    
    # Aguardar servidor iniciar
    echo -e "${YELLOW}Aguardando servidor iniciar...${NC}"
    sleep 10
    
    # Verificar se subiu
    if ! curl -s http://localhost:8000 > /dev/null; then
        echo -e "${RED}Erro: Não foi possível iniciar o servidor Django${NC}"
        exit 1
    fi
    
    CLEANUP_DJANGO=true
else
    echo -e "${GREEN}Servidor Django já está rodando${NC}"
    CLEANUP_DJANGO=false
fi

# Função para limpeza
cleanup() {
    if [ "$CLEANUP_DJANGO" = true ] && [ ! -z "$DJANGO_PID" ]; then
        echo -e "${YELLOW}Parando servidor Django...${NC}"
        kill $DJANGO_PID 2>/dev/null || true
    fi
}

# Registrar função de limpeza
trap cleanup EXIT

# Executar testes baseado no tipo
case $TEST_TYPE in
    "smoke")
        echo -e "${GREEN}Executando testes Smoke...${NC}"
        robot -d "$RESULTS_DIR" -i smoke -v BROWSER:$BROWSER -v HEADLESS:$HEADLESS tests/
        ;;
    "regression")
        echo -e "${GREEN}Executando testes de Regressão...${NC}"
        robot -d "$RESULTS_DIR" -i regression -v BROWSER:$BROWSER -v HEADLESS:$HEADLESS tests/
        ;;
    "api")
        echo -e "${GREEN}Executando testes de API...${NC}"
        robot -d "$RESULTS_DIR" -v BROWSER:$BROWSER tests/api/
        ;;
    "web")
        echo -e "${GREEN}Executando testes Web...${NC}"
        robot -d "$RESULTS_DIR" -v BROWSER:$BROWSER -v HEADLESS:$HEADLESS tests/web/
        ;;
    "integration")
        echo -e "${GREEN}Executando testes de Integração...${NC}"
        robot -d "$RESULTS_DIR" -v BROWSER:$BROWSER -v HEADLESS:$HEADLESS tests/integration/
        ;;
    "all")
        echo -e "${GREEN}Executando todos os testes...${NC}"
        robot -d "$RESULTS_DIR" -v BROWSER:$BROWSER -v HEADLESS:$HEADLESS tests/
        ;;
    "parallel")
        echo -e "${GREEN}Executando testes em paralelo...${NC}"
        if ! command -v pabot &> /dev/null; then
            echo -e "${YELLOW}Instalando pabot para execução paralela...${NC}"
            pip install robotframework-pabot
        fi
        pabot -d "$RESULTS_DIR" -v BROWSER:$BROWSER -v HEADLESS:$HEADLESS --pabotlib tests/
        ;;
    *)
        echo -e "${RED}Tipo de teste inválido: $TEST_TYPE${NC}"
        echo -e "${YELLOW}Tipos disponíveis: smoke, regression, api, web, integration, all, parallel${NC}"
        exit 1
        ;;
esac

TEST_EXIT_CODE=$?

# Gerar relatório combinado se múltiplos arquivos de output existirem
if [ $(find "$RESULTS_DIR" -name "output.xml" | wc -l) -gt 1 ]; then
    echo -e "${YELLOW}Gerando relatório combinado...${NC}"
    rebot -d "$RESULTS_DIR/combined" "$RESULTS_DIR"/*/output.xml
fi

# Mostrar resultados
echo ""
echo -e "${BLUE}=== Resultados dos Testes ===${NC}"
if [ -f "$RESULTS_DIR/report.html" ]; then
    echo -e "${GREEN}Relatório: $RESULTS_DIR/report.html${NC}"
    echo -e "${GREEN}Log: $RESULTS_DIR/log.html${NC}"
elif [ -f "$RESULTS_DIR/combined/report.html" ]; then
    echo -e "${GREEN}Relatório: $RESULTS_DIR/combined/report.html${NC}"
    echo -e "${GREEN}Log: $RESULTS_DIR/combined/log.html${NC}"
fi

# Mostrar estatísticas rápidas
if [ -f "$RESULTS_DIR/output.xml" ]; then
    TOTAL=$(grep -o 'stat.*total="[0-9]*"' "$RESULTS_DIR/output.xml" | head -1 | grep -o '[0-9]*')
    PASSED=$(grep -o 'stat.*pass="[0-9]*"' "$RESULTS_DIR/output.xml" | head -1 | grep -o '[0-9]*')
    FAILED=$(grep -o 'stat.*fail="[0-9]*"' "$RESULTS_DIR/output.xml" | head -1 | grep -o '[0-9]*')
    
    echo -e "${BLUE}Total: $TOTAL | ${GREEN}Passed: $PASSED${NC} | ${RED}Failed: $FAILED${NC}"
fi

# Abrir relatório no browser se disponível (apenas em ambiente desktop)
if [ "$HEADLESS" = "false" ] && command -v xdg-open &> /dev/null; then
    read -p "Abrir relatório no browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "$RESULTS_DIR/report.html" ]; then
            xdg-open "$RESULTS_DIR/report.html"
        elif [ -f "$RESULTS_DIR/combined/report.html" ]; then
            xdg-open "$RESULTS_DIR/combined/report.html"
        fi
    fi
fi

echo -e "${GREEN}Execução concluída!${NC}"
exit $TEST_EXIT_CODE 