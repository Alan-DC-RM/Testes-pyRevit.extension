# -*- coding: utf-8 -*-
__title__ = "Inserir PCs"
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
op1 = "Inserir PCS em blocos sem pilares"
op2 = "Preencher cargas"
options = [op1, op2]
result = forms.SelectFromList.show(options, "Selecione um", multiselect=True)
if not result:
    forms.alert("Seleção cancelada",
                sub_msg="Operação foi abortada",
                exitscript=True
                )


# Código de fato, com base no resultado
for r in result:
    if r == op1:
        # Código da opção 1 - Inserir PCs

        # 1a etapa é verificar se a vista ativa é do Type Locação e cargas, para poder locar os PCs
        vista_ativa = doc.ActiveView
        type_vista_ativa = doc.GetElement(vista_ativa.GetTypeId())
        nome_tipo_vista = type_vista_ativa.LookupParameter("Type Name").AsString()
        if "locação" not in nome_tipo_vista.lower():
            forms.alert(msg="Vista ativa não é uma planta de Locação",
                        sub_msg="Ou pode ser que o nome do Tipo da Vista não tenha \'Locação\' escrito",
                        exitscript=True
                        )

        # Na sequência, verificamos se a família de Ponto de Carga está carregada no projeto
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

        # A transação é onde, de fato, criamos as instâncias de PCs
        t = Transaction(doc, __title__)
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
                tit = funda.LookupParameter("Titulo").AsString()
                new_pc.LookupParameter("Titulo").Set(tit)

        t.Commit()

    if r == op2:
        # Código da opção 2 - Preencher Cargas
        excel_file_path = forms.pick_file()
        if excel_file_path:
            exten = excel_file_path.split(".")[-1]
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
        excel_program = Excel.ApplicationClass()
        excel_file = excel_program.Workbooks.Open(excel_file_path)
        opts_planilhas = []
        for planilha in excel_file.Sheets:
            opts_planilhas.append(planilha)
        # Nesse método do Forms, pelo visto, ele já puxa o .Name das planilhas quando exibe na lista. Legal!
        sheet = forms.SelectFromList.show(opts_planilhas,
                                          title="Selecione a planilha onde está o Despil desejado",
                                          multiselect=False
                                          )
        for ro in range(1, sheet.UsedRange.Rows.Count + 1):
            for c in range(1, sheet.UsedRange.Columns.Count + 1):
                try:
                    cell_value = sheet.Cells(ro, c).Value2
                except:
                    cell_value = None

                if cell_value == "DESPIL":
                    despil_col = c
                    despil_row = ro
                    break
            if despil_col:
                break
        valores = []
        if despil_col:
            row = despil_row + 2  # começa duas linhas abaixo
            while True:
                titulo = sheet.Cells(row, despil_col).Value2
                carga = sheet.Cells(row, despil_col + 1).Value2
                if (
                        (titulo is None or str(titulo).strip() == "")
                        and
                        (carga is None or str(carga).strip() == "")
                ):
                    break
                valores.append((titulo, carga))
                row += 1
        for valor in valores:
            print(valor)
        excel_file.Close(False)
        excel_program.Quit()
