from wsgiref import headers
from dotenv import load_dotenv
import requests
import os

class GitHubIssueAutomation:
    def __init__(self, username: str, project_name: str):
        self.username = username
        self.get_env_variables()
        self.project_id = self.get_project_id(project_name)

    def get_env_variables(self):
        load_dotenv()
        self.token = os.environ.get("GITHUB_TOKEN")
        self.link_repo = os.environ.get("LINK_REPO")
        if not self.token or not self.link_repo:
            raise ValueError("GITHUB_TOKEN and LINK_REPO must be set in the .env file")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def issue_exists(self, titulo: str) -> bool:
        url = f"https://api.github.com/repos/{self.link_repo}/issues?state=all&per_page=100"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        issues = response.json()
        for issue in issues:
            if issue.get("title", "").strip().lower() == titulo.strip().lower():
                return True
        return False
    

    def create_issue(self, title, labels):
        if self.issue_exists(title):
            print(f"Issue duplicada não criada: {title}")
            return

        payload = {
            "title": title,
            "labels": labels
        }
        url = f"https://api.github.com/repos/{self.link_repo}/issues"
        response = requests.post(url=url, headers=self.headers, json=payload)

        if response.status_code == 201:
            print(f"Issue criada: {title}")
        else:
            print(f"Erro ao criar a issue '{title}': {response.status_code}")
            print(response.json())

    def get_project_id(self, project_name: str):
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
        """ % self.username
        response = requests.post(graphql_url, headers=self.headers, json={"query": query})
        response.raise_for_status()
        for project in response.json()['data']['user']['projectsV2']['nodes']:
            if project_name.lower() in [str(i).lower() for i in project.values()]:
                return project['id']
        return
    
    def get_issue_id(self, title: str) -> list[int]:
        url = f"https://api.github.com/repos/{self.link_repo}/issues"
        response = requests.get(url=url, headers=self.headers)
        for item in response.json():
            if "pull_request" not in item:  # evita PRs
                if item.get("title", "").strip().lower() == title.strip().lower():
                    id = item["node_id"]
                    return id
        return None

    def assign_issue_to_project(self, item_id):
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
            "projectId": self.get_project_id(),
            "contentId": item_id
        }
        response = requests.post(graphql_url, headers=self.headers, json={"query": query, "variables": variables})

        if response.status_code == 200:
            print(f"Issue '{item_id}' atribuída ao projeto com sucesso.")
        else:
            print(f"Erro ao atribuir a issue '{item_id}' ao projeto")
            print(response.json())
            print(response.status_code)

    def update_item_status(self, item_id):
        query = """
        mutation UpdateStatusField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
            updateProjectV2ItemFieldValue(
                input: {
                    projectId: $projectId
                    itemId: $itemId
                    fieldId: $fieldId
                    value: {
                        singleSelectOptionId: $optionId
                    }
                }
            ) {
                projectV2Item {
                    id
                }
            }
        }
        """
        field_id = "PVTSSF_lAHOCK-Bws4A-fNUzgx4DCQ"
        option_id = "f75ad846"
        variables = {
            "projectId": self.project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "optionId": option_id,
        }

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables}
        )

        response.raise_for_status()
        print(f"Status do item {item_id} atualizado.")

    def get_fields(self):
        query = """
        query ($projectId: ID!) {
        node(id: $projectId) {
            ... on ProjectV2 {
            fields(first: 50) {
                nodes {
                __typename
                ... on ProjectV2Field {
                    id
                    name
                }
                ... on ProjectV2SingleSelectField {
                    id
                    name
                }
                ... on ProjectV2IterationField {
                    id
                    name
                }
                }
            }
            }
        }
        }
        """
        variables = {"projectId": self.project_id}

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables}
        )

        response.raise_for_status()
        print(response.json())
        fields = response.json()["data"]["node"]["fields"]["nodes"]

        fields_return = []
        for f in fields:
            if not f:
                continue
            fields_return.append({
                "name": f['name'],
                "id": f['id']
            })
        return fields_return

    def get_items_project_ids(self):
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
        variables = {"projectId": self.project_id}

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
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

        return ids        

    def get_item_ids_por_status(self, status_desejado: str):
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
                        name
                        field {
                        ... on ProjectV2SingleSelectField {
                            name
                        }
                        }
                    }
                    }
                }
                }
            }
            }
        }
        }
        """
        variables = {"projectId": self.project_id}

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables}
        )

        response.raise_for_status()
        data = response.json()
        items = data["data"]["node"]["items"]["nodes"]

        ids = []
        for item in items:
            status_value = next(
                (f["name"] for f in item["fieldValues"]["nodes"]
                if f.get("field", {}).get("name") == "Status"),
                None
            )

            if status_value == status_desejado:
                ids.append(item["id"])

        return ids

    def update_estimate_field(self, item_id, field_id, value):
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
            "projectId": self.project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "number": value
        }
        response = requests.post("https://api.github.com/graphql", headers=self.headers, json={"query": query, "variables": variables})
        if response.status_code == 200:
            print(f"Campo atualizado com sucesso para o item {item_id}")
        else:
            print(f"Erro ao atualizar o campo para o item {item_id}")
            print(response.json())
            print(response.status_code)

    def update_sprint_field(self, item_id, field_id, iteration_id):
        query = """
        mutation UpdateSprintField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $iterationId: String!) {
        updateProjectV2ItemFieldValue(
            input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: {
                iterationId: $iterationId
            }
            }
        ) {
            projectV2Item {
            id
            }
        }
        }
        """
        variables = {
            "projectId": self.project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "iterationId": iteration_id
        }

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables}
        )
        response.raise_for_status()


    def get_sprint_options(self, field_id: str):
        query = """
        query ($id: ID!) {
        node(id: $id) {
            ... on ProjectV2IterationField {
            name
            configuration {
                iterations {
                id
                title
                startDate
                duration
                }
            }
            }
        }
        }
        """
        variables = {"id": field_id}

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables}
        )

        response.raise_for_status()
        options = response.json()["data"]["node"]["configuration"]["iterations"]
        options_return = []
        for option in options:
            options_return.append({
                "name": option['title'],
                "id": option['id']
            })
        return options_return

    
