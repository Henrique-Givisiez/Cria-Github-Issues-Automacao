import requests
import os
from dotenv import load_dotenv
from read_excel import read_excel

def create_issues():
    # Carrega variáveis do .env
    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN")
    link_repositorio = os.environ.get("LINK_REPO")

    # Cabecalho de autorizacao
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    issues = read_excel(path="Issues por Sprint.xlsx")

    for issue in issues:
        titulo = issue["titulo"]
        labels = issue["etapa"].split("/")
        esforco = issue["esforco"]

        payload = {
            "title": titulo,
            "labels": labels
        }
        url = f"https://api.github.com/repos/{link_repositorio}/issues"
        response = requests.post(url=url,headers=headers,json=payload)

        if response.status_code == 201:
            print(f"Issue criada: {titulo}")
        else:
            print(f"Erro ao criar a issue '{titulo}': {response.status_code}")
            print(response.json())

    return response.json()

