# -*- coding: utf-8 -*-
__title__ = "Inserir PCs\nPreencher Cargas"
__doc__ = """
Rotina que permite a inserção da família de ponto de carga exatamente no CG de Blocos de Fundação que não tenham um
pilar imediatamente acima, junto com a possibilidade de preencher as cargas dos PCs e pilares de acordo com a planilha
de cargas.

Podemos escolher só lançar os PCs, só preencher as cargas ou os dois!
 
A família de Ponto de Carga deve estar carregada no projeto.

O pilar precisa estar faceando o bloco e com o valor do parâmetro Chave preenchido e contendo "//0" (o que indica que
ele é primeiro lance)
"""

from Autodesk.Revit.DB import *
from pyrevit import forms
from System.Collections.Generic import List
import clr
clr.AddReference('Microsoft.Office.Interop.Excel')
from Microsoft.Office.Interop import Excel


doc = __revit__.ActiveUIDocument.Document   #type: UIDocument


# Input do usuário, janela de seleção e failsafe caso feche a janela (variável vazia)
op1 = "Inserir Pontos de Carga em blocos sem pilares em cima"
op2 = "Preencher cargas de pilares e Pontos de Carga do projeto"
options = [op1, op2]
result = forms.SelectFromList.show(options, "Selecione um", multiselect=True)
if not result:
    forms.alert("Seleção cancelada",
                sub_msg="Operação foi abortada",
                exitscript=True
                )

# Verificamos se a família de Ponto de Carga está carregada no projeto antes de mais nada, pois ela é necessária para os
# 2 casos que temos dessa automação
fams = FilteredElementCollector(doc).OfClass(Family).ToElements()
achou = False
for fam in fams:
    if fam.Name == "Ponto de Carga":
        ponto_de_carga = fam
        achou = True
        break
if not achou:
    forms.alert("Família de Ponto de Carga não carregada no modelo ou com nome alterado",
                title="Alerta!",
                exitscript=True
                )

# Código de fato, com base no resultado
for r in result:

    # Código da opção 1 - Inserir PCs
    if r == op1:

        # 1a etapa é verificar se a vista ativa é do Type Locação e cargas, para poder locar os PCs
        vista_ativa = doc.ActiveView
        type_vista_ativa = doc.GetElement(vista_ativa.GetTypeId())
        nome_tipo_vista = type_vista_ativa.LookupParameter("Type Name").AsString()
        if "locação" not in nome_tipo_vista.lower():
            forms.alert(msg="Vista ativa não é uma planta de Locação",
                        sub_msg="Ou pode ser que o nome do Tipo da Vista não tenha \'Locação\' escrito",
                        exitscript=True
                        )

        # Então pegamos todas as Fundações - blocos ou sapatas, indo pelo filtro "not_cubetas", removendo de todas as
        # connections apenas as cubetas e blocos de transição. Isso pode ser um problema se tivermos Connections que
        # não são cubetas, mas precisaríamos tirar
        sconnections = (FilteredElementCollector(doc) \
                        .OfCategory(BuiltInCategory.OST_StructConnections) \
                        .WhereElementIsNotElementType() \
                        .ToElements())
        funds = []
        for s in sconnections:
            tipo = s.Symbol
            famname = tipo.FamilyName
            if not famname == "Cubeta":
                if "Trans" not in famname:
                    funds.append(s)

        # Então pegamos todos os pilares, filtramos pelos primeiros lances (chave -> //0)
        scolumns = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_StructuralColumns) \
            .WhereElementIsNotElementType() \
            .ToElements()

        dict_pilares = {}

        for p in scolumns:
            chave = p.LookupParameter("Chave").AsString()
            if chave:
                if "//0" in chave:
                    ponto = p.Location.Point
                    x = ponto.X
                    y = ponto.Y
                    z = p.get_BoundingBox(None).Min.Z
                    dict_pilares[p] = [x, y, z]
                    # Eu usei esse dicionário para ter o pilar como chave e a chave é uma lista de três índices:
                    # lista[0] = ponto X do pilar, do CG
                    # lista[1] = ponto Y do pilar, do CG
                    # lista[2] = ponto Z do pilar, menor ponto da geometria dele (BoundingBox). O CG ficaria no meio del
                    # No fim, essa lista representa o CG na face inferior do pilar

        # Então passamos para a etapa de filtrar os blocos/fundações que não tenham pilares imediatamente acima.
        # No Dynamo isso é feito por um Node só, aqui, fizemos a lógica do zero.
        # Basicamente fomos pela BoundingBox da fundação e verificamos se o ponto adquirido no dicionário na etapa
        # anterior está dentro dos limites de XY dela, além de estar na mesma altura (Z igual)
        fund_sem_pilar = []

        for fund in funds:
            encontrou_pilar = False
            x_fund_min = fund.get_BoundingBox(None).Min.X
            x_fund_max = fund.get_BoundingBox(None).Max.X
            y_fund_min = fund.get_BoundingBox(None).Min.Y
            y_fund_max = fund.get_BoundingBox(None).Max.Y
            z_fund_max = fund.get_BoundingBox(None).Max.Z
            for pil, lista_xyz in dict_pilares.items():
                if (
                    round(lista_xyz[2], 2) == round(z_fund_max, 2)
                    and x_fund_min <= lista_xyz[0] <= x_fund_max
                    and y_fund_min <= lista_xyz[1] <= y_fund_max
                ):
                    encontrou_pilar = True
                    break
            if not encontrou_pilar:
                fund_sem_pilar.append(fund)

        # Preparar lista de pontos XY onde já temos PCs existentes para não criar duplicados
        lista_xy_existente = []
        annotations_vista_ativa = FilteredElementCollector(doc, vista_ativa.Id)\
            .OfCategory(BuiltInCategory.OST_GenericAnnotation)\
            .WhereElementIsNotElementType()\
            .ToElements()
        for anot in annotations_vista_ativa:
            if anot.Symbol.Family.Id == ponto_de_carga.Id:
                x_pc = round(anot.Location.Point.X, 2)
                y_pc = round(anot.Location.Point.Y, 2)
                lista_xy_existente.append([x_pc, y_pc])

        # A transação é onde, de fato, criamos as instâncias de PCs. Mudei o título dela, temos uma para cada opção

        t = Transaction(doc, "Inserir PCs")

        t.Start()

        symbol_ids = ponto_de_carga.GetFamilySymbolIds()
        symbol_id_list = List[ElementId](symbol_ids)
        symbols = [doc.GetElement(id) for id in symbol_id_list]
        for funda in fund_sem_pilar:
            ponto_inser = funda.Location.Point  # Usamos o ponto de inserção sendo o Location Point da fundação
            ponto_inser_x = round(ponto_inser.X, 2)
            ponto_inser_y = round(ponto_inser.Y, 2)
            lista_inser = [ponto_inser_x, ponto_inser_y]
            # Só criamos para os pontos que não tenham um PC já criado, com base na lista populada na etapa anterior
            if lista_inser not in lista_xy_existente:
                new_pc = doc.Create.NewFamilyInstance(ponto_inser, symbols[0], vista_ativa)
                tit = funda.LookupParameter("Titulo").AsString() #S91 ou
                tit_subst_pc = tit.replace("B", "PC").replace("S", "PC")
                new_pc.LookupParameter("Titulo").Set(tit_subst_pc)

        t.Commit()

    # Código da opção 2 - Preencher Cargas
    if r == op2:
        # Primeiro vou pegar o input do arquivo do usuário
        excel_file_path = forms.pick_file()
        if excel_file_path:
            exten = excel_file_path.split(".")[-1] # Uso split e acesso o último item splitado, que é a extensão do arqu
            # Só vou permitir arquivos da extensão de Excel. Não filtrei na seleção, mas eu verifico aqui depois
            if exten != "xlsm" and exten != "xlsx":
                forms.alert(msg="Seleção Inválida",
                            sub_msg="Tente novamente e selecione um arquivo Excel (xlsx ou xlsm).\n\n" +
                                    "Se o problema persistir, chame a equipe BIM para te auxiliar",
                            exitscript=True
                            )
        else:
            forms.alert(msg="Seleção cancelada",
                        exitscript=True
                        )

        # Aqui vamos trabalhar com os dados do Excel
        excel_program = Excel.ApplicationClass()        # Cria uma instância do Excel (como se você abrisse o app)
        excel_file = excel_program.Workbooks.Open(excel_file_path) # Abre o arquivo de acordo com o path inputado
        opts_planilhas = []
        for planilha in excel_file.Sheets:              # Cada Sheet do arquivo (planilha), vamos adicionar à lista
            opts_planilhas.append(planilha)             # Vamos ter as planilhas do doc p servir como seleção do input

        # Agora pegamos o input do usuário pela última vez: A planilha do documento que ele quer usar o DESPIL
        # O método do forms.pick_file(), pelo visto, já puxa o .Name das planilhas quando exibe na lista de seleção
        # Podemos passar direto sem ter que fazer uma lista análoga com os Names das Sheets
        sheet = forms.SelectFromList.show(opts_planilhas,
                                          title="Selecione a planilha onde está o Despil desejado",
                                          multiselect=False
                                          )
        if not sheet:
            forms.alert(msg="Seleção cancelada",
                        exitscript=True
                        )

        # Vamos loopar toda a planilha, fazemos um range de linhas que têm valores (UsedRange) e para cada linha vamos..
        for ro in range(1, sheet.UsedRange.Rows.Count + 1):
            # ..percorrer todas as colunas
            for c in range(1, sheet.UsedRange.Columns.Count + 1):
                try:
                    # Pegamos o valor da célula na linha e coluna da vez do loop
                    cell_value = sheet.Cells(ro, c).Value2
                except:
                    # Exceção necessária para fazer funcionar, se não da erro no if abaixo
                    cell_value = None
                # Se o valor da célula for DESPIL, achamos a coluna que ela está e podemos prosseguir com a lógica
                if cell_value == "DESPIL":
                    despil_col = c          # Salvamos o valor da coluna..
                    despil_row = ro         # ..e da célula em que está o DESPIL
                    break                   # Quebramos o loop porque já achamos o DESPIL, não precisamos mais procurar
            if despil_col:                  # Se deslip_col tem valor, quer dizer que achamos o DESPIL..
                break                       # ..então, quebramos o loop de linhas, na linha acima quebramos das colunas

        valores = {}                        # Dicionário que será populado com {Título -> Carga}

        if not despil_col:                      # Se descipl_col tem valor, achamos o despil
            forms.alert("O programa não conseguiu achar o DESPIL na tabela.\n\nNada foi feito.", exitscript=True)
        row = despil_row + 2  # começaremos o loop abaixo duas linhas abaixo do DESPIL, porque ele é mesclado
        # Loop while True que vamos quebrar com o break, mais simples do que fazer um for para o range de dados
        while True:                                                     # Esse loop percorre todas as linhas do tit|carg
            titulo_excel = sheet.Cells(row, despil_col).Value2          # Valor do título do pilar/PC no Excel
            titulo_dict = str(titulo_excel).strip()                     # Valor do título "limpo" para o dicionário
            carga_excel = sheet.Cells(row, despil_col + 1).Value2       # Valor da carga do pilar/PC no Excel
            carga_dict = str(carga_excel).strip()                       # Valor da carga "limpa" para o dicionário
            if (
                    (titulo_excel is None or titulo_dict == "")         # Precisei "limpar" os valores do Excel para..
                    and                                                 # ..tirar os espaços vazios, que entravam como..
                    (carga_excel is None or carga_dict == "")           # ..valores != de None e n eram desconsiderados
            ):                                                          # Se uma das variáveis = None, n há mais valores
                break                                                   # Quando não há mais valores, quebramos o loop
            # Só vamos adicionar ao dicionário abaixo se não houve break, ou seja, ainda temos valores válidos para add
            valores[titulo_dict] = float(carga_dict)                    # Adicionamos ao dicionário o conjunto de tit+cg
            row += 1                                                    # Adicionamos 1 ao valor de linhas e recomeçamos
        excel_file.Close(False)                                         # Essas duas linhas servem para fechar o..
        excel_program.Quit()                                            # ..processo do Excel corretamente e evitar bugs


        # Lista com todos os pilares (Struct_Columns). No Template parâmetro Carga está aplicado à categoria - n da erro
        struct_cols = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_StructuralColumns) \
            .WhereElementIsNotElementType() \
            .ToElements()

        # Para todas as anotações do projeto, filtramos pelos PCs com base na família, por isso tirei do 1º if a parte
        # que pegamos a Family Class do ponto_de_carga
        annotations = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_GenericAnnotation)\
            .WhereElementIsNotElementType()\
            .ToElements()
        pcs = []
        for anote in annotations:
            if anote.Symbol.Family.Id == ponto_de_carga.Id:
                pcs.append(anote)

        # A transação é onde, de fato, criamos as instâncias de PCs. Mudei o título dela, temos uma para cada opção

        t = Transaction(doc, "Preencher cargas")

        t.Start()

        # Primeiro pegamos os títulos do PILARES e setamos a carga com base no que adquirimos do Excel
        for pilar in struct_cols:
            titulo_pilar = pilar.LookupParameter("Titulo").AsString()
            if titulo_pilar in valores.keys():
                pilar.LookupParameter("Carga").Set(valores[titulo_pilar])
        # Segundo pegamos os títulos do PCs e setamos a carga com base no que adquirimos do Excel
        for pc in pcs:
            titulo_pc = pc.LookupParameter("Titulo").AsString()
            if titulo_pc in valores.keys():
                pc.LookupParameter("Carga").Set(valores[titulo_pc])

        t.Commit()
