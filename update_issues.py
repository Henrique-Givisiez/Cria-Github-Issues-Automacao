import requests
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
token = os.environ.get("GITHUB_TOKEN")
# Cabecalho de autorizacao
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}

def get_issues_ids() -> list[int]:
    link_repositorio = os.environ.get("LINK_REPO")


    url = f"https://api.github.com/repos/{link_repositorio}/issues"
    response = requests.get(url=url, headers=headers)
    ids = []
    for item in response.json():
        id = item["node_id"]
        ids.append(id)
    return ids


def update_issue(issue_node_id):
    graphql_url = "https://api.github.com/graphql"
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    """
    variables = {
        "projectId": "PVT_kwHOCK-Bws4A-fNU",
        "contentId": issue_node_id
    }
    r = requests.post(graphql_url, headers=headers, json={"query": query, "variables": variables})
    r.raise_for_status()
    return r.json()


issues_ids = get_issues_ids()
for id in issues_ids:
    print(update_issue(id))

