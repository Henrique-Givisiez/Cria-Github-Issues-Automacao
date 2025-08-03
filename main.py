from create_issues import create_issues
from update_issues import update_issue, get_issues_ids, get_project_node_id

if __name__ == "__main__":
    path = input("Digite o caminho da planilha\n")
    user = input("Digite o nome do usuario GitHub\n")
    resultado = create_issues(path=path)
    if not resultado:
        exit()
    issues_ids = get_issues_ids()
    project_id = get_project_node_id(user=user)
    for id in issues_ids:
        print(update_issue(issue_node_id=id, project_id=project_id))
