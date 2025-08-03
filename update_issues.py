import requests
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
token = os.environ.get("GITHUB_TOKEN")
link_repositorio = os.environ.get("LINK_REPO")

# Cabecalho de autorizacao
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}


def get_issues_ids() -> list[int]:
    url = f"https://api.github.com/repos/{link_repositorio}/issues"
    response = requests.get(url=url, headers=headers)
    ids = []
    for item in response.json():
        if "pull_request" not in item:  # evita PRs
            id = item["node_id"]
            ids.append(id)
    return ids


def update_issue(issue_node_id, project_id):
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


def get_project_node_id(user: str, title: str):
    graphql_url = "https://api.github.com/graphql"
    query = """
    query {
      user(login: "%s") {
        projectsV2(first: 10) {
          nodes {
            id
            title
            number
          }
        }
      }
    }
    """ % user
    r = requests.post(graphql_url, headers=headers, json={"query": query})
    r.raise_for_status()
    for project in r.json()['data']['user']['projectsV2']['nodes']:
        if title.lower() in [str(i).lower() for i in project.values()]:
            return project['id']
    return
