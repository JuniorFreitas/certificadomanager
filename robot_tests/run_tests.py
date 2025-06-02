#!/usr/bin/env python3
"""
Script Python para execução avançada dos testes Robot Framework
Oferece mais opções e flexibilidade que o script bash
"""

import os
import sys
import argparse
import subprocess
import time
import requests
from datetime import datetime
from pathlib import Path

class RobotTestRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.robot_dir = Path(__file__).parent
        self.results_dir = self.robot_dir / "results"
        
    def setup_environment(self):
        """Configura o ambiente para execução dos testes"""
        print("🔧 Configurando ambiente...")
        
        # Verificar se estamos no diretório correto
        if not (self.project_root / "manage.py").exists():
            print("❌ Erro: manage.py não encontrado. Execute o script da pasta robot_tests")
            sys.exit(1)
            
        # Criar diretório de resultados
        self.results_dir.mkdir(exist_ok=True)
        
        # Verificar se o servidor Django está rodando
        if not self.is_django_running():
            print("🚀 Iniciando servidor Django...")
            self.start_django_server()
            time.sleep(10)  # Aguardar servidor iniciar
            
            if not self.is_django_running():
                print("❌ Erro: Não foi possível iniciar o servidor Django")
                sys.exit(1)
        else:
            print("✅ Servidor Django já está rodando")
    
    def is_django_running(self):
        """Verifica se o servidor Django está rodando"""
        try:
            response = requests.get("http://localhost:8000", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def start_django_server(self):
        """Inicia o servidor Django em background"""
        os.chdir(self.project_root)
        subprocess.Popen([
            sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(self.robot_dir)
    
    def run_tests(self, test_type="smoke", browser="chrome", headless=True, 
                  parallel=False, include_tags=None, exclude_tags=None):
        """Executa os testes Robot Framework"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.results_dir / f"{test_type}_{timestamp}"
        output_dir.mkdir(exist_ok=True)
        
        # Construir comando robot
        cmd = ["robot"]
        
        # Diretório de saída
        cmd.extend(["-d", str(output_dir)])
        
        # Variáveis
        cmd.extend(["-v", f"BROWSER:{browser}"])
        cmd.extend(["-v", f"HEADLESS:{headless}"])
        
        # Tags
        if include_tags:
            for tag in include_tags:
                cmd.extend(["-i", tag])
        elif test_type != "all":
            cmd.extend(["-i", test_type])
            
        if exclude_tags:
            for tag in exclude_tags:
                cmd.extend(["-e", tag])
        
        # Determinar diretório de testes
        if test_type == "api":
            test_dir = "tests/api/"
        elif test_type == "web":
            test_dir = "tests/web/"
        elif test_type == "integration":
            test_dir = "tests/integration/"
        else:
            test_dir = "tests/"
        
        cmd.append(test_dir)
        
        print(f"🧪 Executando testes: {' '.join(cmd)}")
        
        # Executar testes
        if parallel:
            cmd[0] = "pabot"
            cmd.extend(["--pabotlib"])
        
        try:
            result = subprocess.run(cmd, cwd=self.robot_dir, capture_output=True, text=True)
            
            # Mostrar resultados
            self.show_results(output_dir, result.returncode)
            
            return result.returncode == 0
            
        except FileNotFoundError:
            if parallel:
                print("❌ pabot não encontrado. Instale com: pip install robotframework-pabot")
            else:
                print("❌ robot não encontrado. Instale as dependências: pip install -r requirements.txt")
            return False
    
    def show_results(self, output_dir, exit_code):
        """Mostra os resultados dos testes"""
        print("\n" + "="*50)
        print("📊 RESULTADOS DOS TESTES")
        print("="*50)
        
        # Verificar se há arquivos de resultado
        report_file = output_dir / "report.html"
        log_file = output_dir / "log.html"
        output_file = output_dir / "output.xml"
        
        if report_file.exists():
            print(f"📄 Relatório: {report_file}")
        if log_file.exists():
            print(f"📋 Log: {log_file}")
            
        # Extrair estatísticas do output.xml se existir
        if output_file.exists():
            self.extract_statistics(output_file)
        
        if exit_code == 0:
            print("✅ Todos os testes passaram!")
        else:
            print("❌ Alguns testes falharam!")
            
        print(f"📁 Resultados salvos em: {output_dir}")
    
    def extract_statistics(self, output_file):
        """Extrai estatísticas do arquivo output.xml"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(output_file)
            root = tree.getroot()
            
            # Encontrar estatísticas
            stats = root.find('.//statistics/total/stat')
            if stats is not None:
                total = stats.get('pass', '0')
                failed = stats.get('fail', '0')
                print(f"📈 Total: {int(total) + int(failed)} | ✅ Passou: {total} | ❌ Falhou: {failed}")
                
        except Exception as e:
            print(f"⚠️  Não foi possível extrair estatísticas: {e}")
    
    def run_security_tests(self):
        """Executa testes de segurança específicos"""
        print("🔒 Executando testes de segurança...")
        return self.run_tests(
            test_type="all",
            include_tags=["security", "negative"],
            exclude_tags=["slow"]
        )
    
    def run_smoke_tests(self):
        """Executa testes de smoke"""
        print("💨 Executando testes de smoke...")
        return self.run_tests(
            test_type="smoke",
            exclude_tags=["slow"]
        )
    
    def run_regression_tests(self):
        """Executa testes de regressão completos"""
        print("🔄 Executando testes de regressão...")
        return self.run_tests(
            test_type="regression",
            parallel=True
        )

def main():
    parser = argparse.ArgumentParser(description="Executor de testes Robot Framework")
    parser.add_argument("--type", choices=["smoke", "regression", "api", "web", "integration", "security", "all"],
                       default="smoke", help="Tipo de teste a executar")
    parser.add_argument("--browser", choices=["chrome", "firefox", "safari", "headlesschrome"],
                       default="chrome", help="Browser para testes web")
    parser.add_argument("--headless", action="store_true", help="Executar browser em modo headless")
    parser.add_argument("--parallel", action="store_true", help="Executar testes em paralelo")
    parser.add_argument("--include", nargs="+", help="Tags para incluir")
    parser.add_argument("--exclude", nargs="+", help="Tags para excluir")
    parser.add_argument("--no-setup", action="store_true", help="Pular configuração do ambiente")
    
    args = parser.parse_args()
    
    runner = RobotTestRunner()
    
    if not args.no_setup:
        runner.setup_environment()
    
    # Executar testes baseado no tipo
    if args.type == "security":
        success = runner.run_security_tests()
    elif args.type == "smoke":
        success = runner.run_smoke_tests()
    elif args.type == "regression":
        success = runner.run_regression_tests()
    else:
        success = runner.run_tests(
            test_type=args.type,
            browser=args.browser,
            headless=args.headless,
            parallel=args.parallel,
            include_tags=args.include,
            exclude_tags=args.exclude
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 