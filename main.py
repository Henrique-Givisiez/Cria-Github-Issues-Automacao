from helper import GitHubIssueAutomation
from read_excel import read_excel

if __name__ == "__main__":
    path = input("Digite o caminho da planilha\n")
    user = input("Digite o nome do usuario GitHub\n")
    project = input("Digite o nome do projeto\n")
    if not path or not user or not project:
        print("Todos os campos são obrigatórios.")
        exit()

    automation = GitHubIssueAutomation(username=user, project_name=project)
    issues = read_excel(path=path)

    estimate_dict = []
    for issue in issues:
        # Pega dados retornados do Excel e cria campos necessarios para criar a issue
        title = issue["titulo"]
        labels = issue["etapa"].split("/")
        sprint = issue["sprint"]
        estimate_dict.append(issue["esforco"])

        # Cria a issue no GitHub
        automation.create_issue(title=title, labels=labels)

        # Se a issue já existir, pega o ID dela
        issue_id = automation.get_issue_id(title=title)
        # Atribui a issue ao projeto
        automation.assign_issue_to_project(item_id=issue_id)

    estimate_dict = dict(enumerate(estimate_dict))

    # Atualiza os campos de estimativa e sprint para cada issue criada
    issues_ids = automation.get_items_project_ids()

    count = len(issues_ids) - 1
    for id in issues_ids:
        # Atualiza o campo de estimativa
        automation.update_estimate_field(item_id=id, field_id="PVTF_lAHOCK-Bws4A-fNUzgx4DH4", value=float(estimate_dict[count]))
        
        # Vefifica as sprints disponíveis e atualiza o campo de sprint
        sprints = automation.get_sprint_options(field_id="PVTIF_lAHOCK-Bws4A-fNUzgx4DH8")
        for s in sprints:
            if s["name"] == sprint:
                # Atualiza o campo de sprint para aquela issue
                automation.update_sprint_field(item_id=id, field_id="PVTIF_lAHOCK-Bws4A-fNUzgx4DH8", iteration_id=s["id"])
                break

        # Atualiza o status da issue para "A fazer"
        automation.update_item_status(item_id=id)
        count -= 1
