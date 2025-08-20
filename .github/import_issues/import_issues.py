#!/usr/bin/env python3
"""
GitHub Issues Importer

Este script importa automaticamente issues do GitHub a partir de arquivos JSON
no diretório atual e, após a criação no GitHub, sincroniza os arquivos locais
renomeando-os com o número real da issue e movendo-os para a pasta 'imported'.

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
import subprocess
import argparse
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

def _keychain_service_name(owner: str, repo_name: str) -> str:
    """Nome do serviço no Keychain para este repositório."""
    return f"motorsport_calendar_github_token:{owner}/{repo_name}"

def _read_keychain_token(service_name: str, account: str | None = None) -> str | None:
    """Lê um token do macOS Keychain via 'security find-generic-password'."""
    try:
        cmd = ["security", "find-generic-password", "-s", service_name, "-w"]
        if account:
            cmd = ["security", "find-generic-password", "-a", account, "-s", service_name, "-w"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        token = result.stdout.strip()
        return token if token else None
    except Exception:
        return None

def get_github_client(owner: str, repo_name: str, allow_interactive: bool = True):
    """Inicializa e retorna o cliente da API do GitHub com prioridade:
    1) Variável de ambiente GITHUB_TOKEN
    2) macOS Keychain (serviço específico do repositório)
    3) Cofre criptografado local (~/.config/github_importer/config.enc)
    4) Token informado interativamente
    """
    # 1) Variável de ambiente
    token = os.getenv('GITHUB_TOKEN')
    if token:
        return Github(token)

    # 2) Keychain (serviço específico por repo)
    service = _keychain_service_name(owner, repo_name)
    account = os.getenv('USER') or None
    token = _read_keychain_token(service, account=account)
    if token:
        return Github(token)

    if allow_interactive:
        # 3) Cofre criptografado local
        print("Autenticação necessária para acessar a API do GitHub")
        try:
            password = getpass.getpass("Digite sua senha de criptografia: ")
            token = load_token(password)
        except Exception:
            token = None

        # 4) Interativo (fallback)
        if not token:
            print("\nToken não encontrado no Keychain nem no cofre.")
            print("Por favor, forneça um token de acesso pessoal do GitHub com permissão 'repo'.")
            token = getpass.getpass("Token: ")
            save = input("Deseja salvar este token para uso futuro? (s/N): ").strip().lower()
            if save == 's':
                password_confirm = getpass.getpass("Crie uma senha para criptografar o token: ")
                save_token(token, password_confirm)
                print("Token salvo com sucesso!")

        return Github(token)
    else:
        print("❌ Token não encontrado em GITHUB_TOKEN nem no Keychain (modo não interativo).")
        print("   Configure a variável GITHUB_TOKEN ou salve o token no Keychain para prosseguir.")
        sys.exit(1)

def parse_repo_identifier(identifier):
    """Analisa o identificador do repositório no formato 'owner/repo'."""
    parts = identifier.split('/')
    if len(parts) != 2 or not all(parts):
        print(f"Erro: Formato de repositório inválido: {identifier}")
        print("Use o formato: owner/repo")
        sys.exit(1)
    return parts[0], parts[1]

def find_existing_issue_by_title(repo, title: str):
    """Procura uma issue existente (aberta ou fechada) com título exatamente igual."""
    try:
        # Busca em 'open' primeiro por performance, depois 'closed'
        for state in ('open', 'closed'):
            for issue in repo.get_issues(state=state):
                if issue.title == title:
                    return issue
        return None
    except GithubException as e:
        print(f" Aviso: falha ao procurar issue existente por título: {e.data.get('message', str(e))}")
        return None

def import_issue(repo, issue_file):
    """Importa uma única issue para o repositório.

    Retorna:
        Issue | None: objeto Issue (PyGithub) criado em caso de sucesso; None caso contrário.
    """
    try:
        with open(issue_file, 'r', encoding='utf-8') as f:
            issue_data = json.load(f)
        
        print(f"\nImportando: {issue_file}")
        title = issue_data.get('title')
        print(f"Título: {title}")

        # Verifica se já existe uma issue com o mesmo título (evita duplicação)
        existing = find_existing_issue_by_title(repo, title)
        if existing is not None:
            print(f" Issue já existe no GitHub: #{existing.number} — {existing.html_url}")
            return existing
        
        # Lê o conteúdo do arquivo markdown se especificado
        body_content = issue_data['body']
        if isinstance(body_content, str) and body_content.endswith('.md'):
            md_file = issue_file.parent / body_content
            if md_file.exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    body_content = f.read()
            else:
                print(f" Arquivo markdown não encontrado: {md_file}")
        
        # Cria a issue no GitHub
        issue = repo.create_issue(
            title=issue_data['title'],
            body=body_content,
            labels=issue_data.get('labels', []),
            assignees=issue_data.get('assignees', [])
        )
        
        print(f" Issue criada com sucesso: {issue.html_url}")
        return issue
        
    except json.JSONDecodeError as e:
        print(f" Erro ao ler o arquivo JSON {issue_file}: {e}")
        return None
    except GithubException as e:
        print(f" Erro ao criar issue no GitHub: {e.data.get('message', str(e))}")
        return None
    except Exception as e:
        print(f" Erro inesperado ao processar {issue_file}: {str(e)}")
        return None

def _build_imported_names(issue_file: Path, issue_number: int) -> tuple[Path, Path | None, str]:
    """Gera nomes de destino (JSON e MD) em 'imported/' usando o número real da issue.

    Retorna (dest_json_path, dest_md_path_or_none, new_base_name).
    """
    imported_dir = Path('imported')
    imported_dir.mkdir(exist_ok=True)

    stem = issue_file.stem  # ex: "107-xfails-ics-tomadatempo"
    parts = stem.split('-', 1)
    slug = parts[1] if len(parts) == 2 else parts[0]
    new_base = f"{issue_number}-{slug}"

    dest_json = imported_dir / f"{new_base}.json"

    # Caso exista um .md com o mesmo prefixo ou especificado pelo campo body
    md_candidate = issue_file.with_suffix('.md')
    dest_md = imported_dir / f"{new_base}.md" if md_candidate.exists() else None

    return dest_json, dest_md, new_base

def sync_local_files_to_issue_number(issue_file: Path, issue, original_body_field: str | None = None) -> bool:
    """Sincroniza os arquivos locais após a importação, renomeando-os com o número da issue.

    - Atualiza o JSON com campos 'github_issue_number' e 'github_issue_url'.
    - Renomeia/move JSON e MD (se existir) para 'imported/<numero>-<slug>.*'.
    - Ajusta o campo 'body' do JSON para apontar para o novo MD, se aplicável.
    """
    try:
        issue_number = issue.number
        issue_url = getattr(issue, 'html_url', None)

        # Carrega JSON original
        with open(issue_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        dest_json, dest_md, new_base = _build_imported_names(issue_file, issue_number)

        # Detecta MD de origem: via 'body' que referencia arquivo .md, se existir
        md_path = None
        body_field = data.get('body')
        if isinstance(body_field, str) and body_field.endswith('.md'):
            candidate = issue_file.parent / body_field
            if candidate.exists():
                md_path = candidate

        # Atualiza campos de sincronismo
        data['github_issue_number'] = issue_number
        if issue_url:
            data['github_issue_url'] = issue_url
        data['state'] = 'open'
        # Se houver MD, ajuste o body para o novo nome
        if dest_md is not None:
            data['body'] = dest_md.name

        # Escreve JSON atualizado diretamente no destino
        with open(dest_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Move/renomeia MD se existir
        if md_path and dest_md is not None:
            shutil.move(str(md_path), str(dest_md))

        # Remove o JSON original após sucesso
        issue_file.unlink(missing_ok=False)

        if dest_md is not None:
            print(f"Arquivos sincronizados: {dest_json} e {dest_md}")
        else:
            print(f"Arquivo sincronizado: {dest_json}")
        return True
    except Exception as e:
        print(f" Erro ao sincronizar arquivos locais para a issue #{getattr(issue, 'number', '?')}: {e}")
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
        print(f" Erro ao mover o(s) arquivo(s) {issue_file}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Importa issues do diretório 'open/' para o GitHub com sincronismo local.")
    parser.add_argument("repo", help="<owner>/<repo>")
    parser.add_argument("--yes", "-y", action="store_true", help="não pedir confirmação para importar")
    parser.add_argument("--non-interactive", dest="non_interactive", action="store_true", help="não interagir para autenticação; falha se não houver token")
    parser.add_argument("--only", nargs="+", help="nome(s) de arquivo .json específicos em .github/import_issues/open/ a serem importados")
    args = parser.parse_args()

    # Configuração
    repo_identifier = args.repo
    owner, repo_name = parse_repo_identifier(repo_identifier)
    
    # Inicializa cliente do GitHub (usa Keychain específico por repositório, se disponível)
    g = get_github_client(owner, repo_name, allow_interactive=(not args.non_interactive))
    
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        print(f"\nConectado ao repositório: {repo.full_name}")
    except GithubException as e:
        print(f"❌ Erro ao acessar o repositório {owner}/{repo_name}: {e.data.get('message', str(e))}")
        sys.exit(1)
    
    # Encontra todos os arquivos JSON de issues no diretório open
    issue_files = list(Path('open').glob('*.json'))
    if args.only:
        names = set(args.only)
        filtered = [p for p in issue_files if p.name in names]
        missing = names - {p.name for p in filtered}
        if missing:
            print(f"Aviso: arquivos não encontrados em 'open/': {', '.join(sorted(missing))}")
        issue_files = filtered
    
    if not issue_files:
        print("Nenhum arquivo de issue encontrado no diretório 'open'.")
        print("Por favor, coloque os arquivos de issue em .github/import_issues/open/")
        return
    
    print(f"\nEncontrados {len(issue_files)} arquivos de issue para importar:")
    for i, file in enumerate(issue_files, 1):
        print(f"{i}. {file.name}")
    
    # Confirmação do usuário (pula se --yes)
    if not args.yes:
        confirm = input("\nDeseja continuar com a importação? (s/N): ").strip().lower()
        if confirm != 's':
            print("Importação cancelada.")
            return
    
    # Processa cada arquivo de issue
    success_count = 0
    for issue_file in issue_files:
        created_issue = import_issue(repo, issue_file)
        if created_issue is not None:
            if sync_local_files_to_issue_number(issue_file, created_issue):
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
