import requests
import os
from dotenv import load_dotenv
from update_issues import get_project_node_id
from read_excel import  read_excel

# Carrega variáveis do .env
load_dotenv()
token = os.environ.get("GITHUB_TOKEN")
link_repositorio = os.environ.get("LINK_REPO")

# Cabecalho de autorizacao
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
}
def get_fields_ids(user, title):
    query = """
        query ($id: ID!) {
          node(id: $id) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2Field {
                    id
                    name
                    dataType
                  }
                }
              }
            }
          }
        }
    """
    project_id = get_project_node_id(user=user, title=title)
    variables = {"id": project_id}
    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables}
    )

    response.raise_for_status()
    fields = response.json()["data"]["node"]["fields"]["nodes"]

    for field in fields:
        if field:
            print(f"- {field['name']} (type: {field['dataType']}, id: {field['id']})")

    return fields[12]['id']

def get_items_ids(project_id, status_label):
    query = """
        query ($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      title
                      number
                    }
                  }
                  fieldValues(first: 10) {
                    nodes {
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        field {
                          ... on ProjectV2SingleSelectField {
                            name
                          }
                        }
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
    variables = {"projectId": project_id}

    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables}
    )
    response.raise_for_status()
    items = response.json()["data"]["node"]["items"]["nodes"]

    filtrados = []
    for item in items:
        status_value = next(
            (f["name"] for f in item["fieldValues"]["nodes"]
             if f.get("field", {}).get("name") == "Status"), None
        )

        if status_value == status_label:
            filtrados.append(item)

    print(f"📦 Itens com Status = '{status_label}':")
    for item in filtrados:
        print(f"- #{item['content']['number']}: {item['content']['title']} | itemId: {item['id']}")

    return filtrados

def get_items(project_id):
    query = """
    query ($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on Issue {
                  title
                  number
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    field {
                      ... on ProjectV2SingleSelectField {
                        name
                      }
                    }
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"projectId": project_id}

    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables}
    )
    response.raise_for_status()
    data = response.json()
    items = data["data"]["node"]["items"]["nodes"]

    sem_status = []
    for item in items:
        status_value = next(
            (f.get("name") for f in item["fieldValues"]["nodes"]
             if f.get("field", {}).get("name") == "Status"),
            None
        )

        if status_value is None:
            sem_status.append(item)
    ids = []
    for item in sem_status:
        ids.append(item['id'])
        print(f"- #{item['content']['number']}: {item['content']['title']} | itemId: {item['id']}")

    return ids


def update_field(item_id, field_id, project_id, estimate):
    query = """
        mutation UpdateNumberField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $number: Float!) {
          updateProjectV2ItemFieldValue(
            input: {
              projectId: $projectId
              itemId: $itemId
              fieldId: $fieldId
              value: { number: $number }
            }
          ) {
            projectV2Item {
              id
            }
          }
        }
        """
    variables = {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "number": estimate
    }
    r = requests.post("https://api.github.com/graphql", headers=headers, json={"query": query, "variables": variables})
    r.raise_for_status()
    print(f"Campo 'Estimate' atualizado para {estimate} no item {item_id}")


field_id = get_fields_ids("Henrique-Givisiez", "Projeto Comida Portuguesa")
project_id = get_project_node_id("Henrique-Givisiez", "Projeto Comida Portuguesa")
items_ids = get_items(project_id)

issues = read_excel(path="Issues por Sprint.xlsx")
count = 0
for issue in issues:
    estimate = issue["esforco"]
    update_field(items_ids[count], field_id, project_id, float(estimate))
    count+=1
