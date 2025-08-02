import openpyxl

def read_excel(path: str) -> list[dict]:
    # Abre a planilha
    wb = openpyxl.load_workbook(path)
    sheet = wb.active

    dados = []  # dados para serem retornados

    # Le as linhas
    for row in sheet.iter_rows(min_row=2, values_only=True):
        tag_etapa, titulo, esforco = row
        esforco = esforco[0]
        user_isssue = {
            "titulo": titulo,
            "etapa": tag_etapa,
            "esforco": esforco
        }
        dados.append(user_isssue)

    return dados

