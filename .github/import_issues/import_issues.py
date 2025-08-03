#!/usr/bin/env python3
"""
GitHub Issues Importer

Este script importa automaticamente issues do GitHub a partir de arquivos JSON
no diretório atual e os move para uma pasta de 'imported' após a importação.

Requisitos:
- Python 3.6+
- PyGithub (instale com: pip install PyGithub)
- cryptography (instale com: pip install cryptography)

Uso:
1. Configure o token na primeira execução
2. Execute: python import_issues.py <owner>/<repo>
"""

import os
import sys
import json
import shutil
import base64
import getpass
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from github import Github, GithubException

def get_config_path():
    """Retorna o caminho para o arquivo de configuração."""
    config_dir = Path.home() / '.config' / 'github_importer'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'config.enc'

def generate_key(password: str, salt: bytes) -> bytes:
    """Gera uma chave de criptografia a partir de uma senha."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def save_token(token: str, password: str):
    """Salva o token de forma criptografada."""
    salt = os.urandom(16)
    key = generate_key(password, salt)
    f = Fernet(key)
    
    config = {
        'salt': base64.b64encode(salt).decode(),
        'token': f.encrypt(token.encode()).decode()
    }
    
    config_path = get_config_path()
    config_path.write_text(json.dumps(config))
    config_path.chmod(0o600)  # Permissões restritas

def load_token(password: str) -> str:
    """Carrega o token criptografado."""
    config_path = get_config_path()
    try:
        config = json.loads(config_path.read_text())
        salt = base64.b64decode(config['salt'])
        key = generate_key(password, salt)
        f = Fernet(key)
        return f.decrypt(config['token'].encode()).decode()
    except Exception as e:
        print(f"Erro ao carregar o token: {e}")
        return None

def get_github_client():
    """Inicializa e retorna o cliente da API do GitHub."""
    # Tenta carregar da variável de ambiente primeiro
    token = os.getenv('GITHUB_TOKEN')
    if token:
        return Github(token)
    
    # Tenta carregar do arquivo de configuração
    print("Autenticação necessária para acessar a API do GitHub")
    password = getpass.getpass("Digite sua senha de criptografia: ")
    token = load_token(password)
    
    if not token:
        print("\nToken não encontrado ou senha incorreta.")
        print("Por favor, forneça um token de acesso pessoal do GitHub com permissão 'repo'.")
        token = getpass.getpass("Token: ")
        save = input("Deseja salvar este token para uso futuro? (s/N): ").strip().lower()
        if save == 's':
            password_confirm = getpass.getpass("Crie uma senha para criptografar o token: ")
            save_token(token, password_confirm)
            print("Token salvo com sucesso!")
    
    return Github(token)

def parse_repo_identifier(identifier):
    """Analisa o identificador do repositório no formato 'owner/repo'."""
    parts = identifier.split('/')
    if len(parts) != 2 or not all(parts):
        print(f"Erro: Formato de repositório inválido: {identifier}")
        print("Use o formato: owner/repo")
        sys.exit(1)
    return parts[0], parts[1]

def import_issue(repo, issue_file):
    """Importa uma única issue para o repositório."""
    try:
        with open(issue_file, 'r', encoding='utf-8') as f:
            issue_data = json.load(f)
        
        print(f"\nImportando: {issue_file}")
        print(f"Título: {issue_data.get('title')}")
        
        # Lê o conteúdo do arquivo markdown se especificado
        body_content = issue_data['body']
        if isinstance(body_content, str) and body_content.endswith('.md'):
            md_file = issue_file.parent / body_content
            if md_file.exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    body_content = f.read()
            else:
                print(f"⚠️ Arquivo markdown não encontrado: {md_file}")
        
        # Cria a issue no GitHub
        issue = repo.create_issue(
            title=issue_data['title'],
            body=body_content,
            labels=issue_data.get('labels', []),
            assignees=issue_data.get('assignees', [])
        )
        
        print(f"✅ Issue criada com sucesso: {issue.html_url}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler o arquivo JSON {issue_file}: {e}")
        return False
    except GithubException as e:
        print(f"❌ Erro ao criar issue no GitHub: {e.data.get('message', str(e))}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado ao processar {issue_file}: {str(e)}")
        return False

def move_to_imported(issue_file):
    """Move o arquivo da issue para a pasta de importados."""
    try:
        # Cria o diretório de importados se não existir
        imported_dir = Path('imported')
        imported_dir.mkdir(exist_ok=True)
        
        # Gera um nome de arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_file = imported_dir / f"{timestamp}_{issue_file.name}"
        
        # Move o arquivo
        shutil.move(issue_file, dest_file)
        
        # Move também o arquivo .md correspondente se existir
        md_file = issue_file.with_suffix('.md')
        if md_file.exists():
            dest_md_file = imported_dir / f"{timestamp}_{md_file.name}"
            shutil.move(md_file, dest_md_file)
            print(f"Arquivos movidos para: {dest_file} e {dest_md_file}")
        else:
            print(f"Arquivo movido para: {dest_file}")
            
        return True
    except Exception as e:
        print(f"❌ Erro ao mover o(s) arquivo(s) {issue_file}: {str(e)}")
        return False

def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <owner>/<repo>")
        sys.exit(1)
    
    # Configuração
    repo_identifier = sys.argv[1]
    owner, repo_name = parse_repo_identifier(repo_identifier)
    
    # Inicializa cliente do GitHub
    g = get_github_client()
    
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        print(f"\nConectado ao repositório: {repo.full_name}")
    except GithubException as e:
        print(f"❌ Erro ao acessar o repositório {owner}/{repo_name}: {e.data.get('message', str(e))}")
        sys.exit(1)
    
    # Encontra todos os arquivos JSON de issues no diretório open
    issue_files = list(Path('open').glob('*.json'))
    
    if not issue_files:
        print("Nenhum arquivo de issue encontrado no diretório 'open'.")
        print("Por favor, coloque os arquivos de issue em .github/import_issues/open/")
        return
    
    print(f"\nEncontrados {len(issue_files)} arquivos de issue para importar:")
    for i, file in enumerate(issue_files, 1):
        print(f"{i}. {file.name}")
    
    # Confirmação do usuário
    confirm = input("\nDeseja continuar com a importação? (s/N): ").strip().lower()
    if confirm != 's':
        print("Importação cancelada.")
        return
    
    # Processa cada arquivo de issue
    success_count = 0
    for issue_file in issue_files:
        if import_issue(repo, issue_file):
            if move_to_imported(issue_file):
                success_count += 1
    
    # Resumo
    print(f"\n✅ Importação concluída!")
    print(f"- Total de issues processadas: {len(issue_files)}")
    print(f"- Issues importadas com sucesso: {success_count}")
    print(f"- Falhas: {len(issue_files) - success_count}")

if __name__ == "__main__":
    # Muda para o diretório do script para garantir caminhos relativos corretos
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
