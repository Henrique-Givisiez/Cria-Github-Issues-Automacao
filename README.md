# GitHub Issues Automation

Este projeto automatiza a criação, atualização e gerenciamento de **issues** e **campos personalizados** dentro de um **GitHub Project v2** (beta). A automação é feita via **GraphQL API**.

Foi criado com o intuito de auxiliar na criação de issues para um projeto pessoal, mas pode ser adaptado com a ajuda dos métodos da classe `helper.py`. A leitura das issues é feita a partir de um arquivo Excel com as colunas Etapa, Tarefa, Esforco, Sprint. 
---

## Funcionalidades

- Criação automática de issues com verificação de duplicidade
- Atribuição de issues a um projeto
- Atualização do status das tarefas
- Preenchimento automático de campos personalizados como:
  - `Estimate` (numérico)
  - `Sprint` (iteração)
- Recuperação de itens por status
- Identificação de itens sem status
- Integração com variáveis de ambiente via `.env`

---

## Estrutura principal do `helper.py`

| Método                            | Descrição                                                                 |
|----------------------------------|---------------------------------------------------------------------------|
| `__init__(username, project_name)`| Inicializa a automação com o nome do usuário e título do projeto GitHub. |
| `get_env_variables()`            | Carrega `GITHUB_TOKEN` e `LINK_REPO` do `.env`.                          |
| `issue_exists(titulo)`          | Verifica se uma issue já existe no repositório.                          |
| `create_issue(title, labels)`    | Cria uma nova issue no repositório, evitando duplicação.                |
| `get_project_id(project_name)`   | Retorna o ID do Project v2 baseado no nome.                              |
| `get_issue_id(title)`            | Busca o ID da issue com base no título.                                  |
| `assign_issue_to_project(id)`    | Adiciona uma issue existente ao Project v2.                              |
| `update_item_status(id)`         | Atualiza o campo de status de um item do projeto.                        |
| `get_fields()`                   | Retorna todos os campos personalizados (`fields`) do projeto.            |
| `get_items_project_ids()`        | Retorna os itens que **não têm status definido** no projeto.             |
| `get_item_ids_por_status(status)`| Retorna os itens associados a um determinado `Status`.                   |
| `update_estimate_field(id, field_id, value)` | Atualiza um campo numérico (`Estimate`) de um item.         |
| `update_sprint_field(id, field_id, iteration_id)` | Atualiza o campo `Sprint` (tipo `ITERATION`).       |
| `get_sprint_options(field_id)`   | Retorna as opções de sprint (iteração) disponíveis no campo.             |

---

## Pré-requisitos

- Python 3.8+
- Biblioteca `requests`
- Biblioteca `python-dotenv`

Instalação das dependências:

```bash
pip install -r requirements.txt


## Uso

Crie um arquivo `.env` com o seguinte conteúdo:

```env
GITHUB_TOKEN=seu_token_do_github
LINK_REPO=usuario/nome-do-repositorio
```

## Observações

- O script atualmente suporta até 100 itens por requisição.
- A automação utiliza a API GraphQL e REST do GitHub.
- Campos como `Status`, `Estimate` e `Sprint` precisam existir no Project para serem atualizados.
