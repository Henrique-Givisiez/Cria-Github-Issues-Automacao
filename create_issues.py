import requests
import os
from dotenv import load_dotenv
from read_excel import read_excel

# Carrega variáveis do .env
load_dotenv()
token = os.environ.get("GITHUB_TOKEN")
link_repositorio = os.environ.get("LINK_REPO")

# Cabecalho de autorizacao
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}

def issue_exists(titulo: str) -> bool:
    url = f"https://api.github.com/repos/{link_repositorio}/issues?state=all&per_page=100"
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    issues = response.json()
    for issue in issues:
        if issue.get("title", "").strip().lower() == titulo.strip().lower():
            return True
    return False


def create_issues(path):
    issues = read_excel(path=path)
    response = ""

    for issue in issues:
        titulo = issue["titulo"]
        labels = issue["etapa"].split("/")

        if issue_exists(titulo):
            print(f"Issue duplicada não criada: {titulo}")
            continue

        payload = {
            "title": titulo,
            "labels": labels
        }
        url = f"https://api.github.com/repos/{link_repositorio}/issues"
        response = requests.post(url=url, headers=headers, json=payload)

        if response.status_code == 201:
            print(f"Issue criada: {titulo}")
        else:
            print(f"Erro ao criar a issue '{titulo}': {response.status_code}")
            print(response.json())

    return response.json() if response else None
