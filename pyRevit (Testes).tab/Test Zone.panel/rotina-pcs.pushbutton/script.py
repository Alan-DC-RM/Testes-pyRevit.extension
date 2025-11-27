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
        # connections apenas as cubetas. Isso pode ser um problema se tivermos Connections que não são cubetas, mas
        # precisaríamos tirar
        sconnections = (FilteredElementCollector(doc) \
                        .OfCategory(BuiltInCategory.OST_StructConnections) \
                        .WhereElementIsNotElementType() \
                        .ToElements())
        not_cubetas = []
        for s in sconnections:
            tipo = s.Symbol
            famname = tipo.FamilyName
            if not famname == "Cubeta":
                not_cubetas.append(s)

        # Então pegamos todos os pilares, filtramos pelos primeiros lances (chave -> //0)
        scolumns = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_StructuralColumns) \
            .WhereElementIsNotElementType() \
            .ToElements()

        dict_pilares = {}

        for p in scolumns:
            chave = p.LookupParameter("Chave").AsString()
            if "//0" in chave and chave:
                ponto = p.Location.Point
                x = ponto.X
                y = ponto.Y
                z = p.get_BoundingBox(None).Min.Z
                dict_pilares[p] = [x, y, z]
                # Eu usei esse dicionário para ter o pilar como chave e a chave é uma lista de três índices:
                # lista[0] = ponto X do pilar, do CG
                # lista[1] = ponto Y do pilar, do CG
                # lista[2] = ponto Z do pilar, menor ponto da geometria dele (BoundingBox). O CG ficaria no meio dele
                # No fim, essa lista representa o CG na face inferior do pilar

        # Então passamos para a etapa de filtrar os blocos/fundações que não tenham pilares imediatamente acima.
        # No Dynamo isso é feito por um Node só, aqui, fizemos a lógica do zero.
        # Basicamente fomos pela BoundingBox da fundação e verificamos se o ponto adquirido no dicionário na etapa
        # anterior está dentro dos limites de XY dela, além de estar na mesma altura (Z igual)
        fund_sem_pilar = []

        for fund in not_cubetas:
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
                x_pc = anot.Location.Point.X
                y_pc = anot.Location.Point.Y
                lista_xy_existente.append([x_pc, y_pc])

        t = Transaction(doc, __title__)
        t.Start()

        symbol_ids = ponto_de_carga.GetFamilySymbolIds()
        symbol_id_list = List[ElementId](symbol_ids)
        symbols = [doc.GetElement(id) for id in symbol_id_list]
        for funda in fund_sem_pilar:
            ponto_inser = funda.Location.Point
            ponto_inser_x = ponto_inser.X
            ponto_inser_y = ponto_inser.Y
            lista_inser = [ponto_inser_x, ponto_inser_y]
            if lista_inser not in lista_xy_existente:
                doc.Create.NewFamilyInstance(ponto_inser, symbols[0], vista_ativa)

        t.Commit()

    '''
    if r == op2:
        #Preencher as cargas a partir da tabela
        input_tabela = forms.ask_for_string(
            default="R00-EX-Cargas-21-10-2025",
            prompt="Nome da aba",
            title="Excel"
        )

        values = []

        
        excel = Excel.ApplicationClass()
        wb = excel.Workbooks.Open(excel_file)
        ws = wb.Sheets(1)

        values = []
        for row in range(41, ws.UsedRange.Rows.Count + 1):
            values.append(ws.Cells(row, 41).Value2)

        print(values)

        wb.Close(False)
        excel.Quit()
'''