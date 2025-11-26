# -*- coding: utf-8 -*-
__title__ = "Inserir PCs"

from Autodesk.Revit.DB import *
from pyrevit import forms
import clr
clr.AddReference('Microsoft.Office.Interop.Excel')
from Microsoft.Office.Interop import Excel
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument


op1 = "Inserir PCS em blocos sem pilares"
op2 = "Preencher cargas"

boxes = [
    op1,
    op2
]

result = forms.SelectFromList.show(boxes, "Selecione um", multiselect=True)
if not result:
    forms.alert("Seleção cancelada",
                sub_msg="Operação foi abortada",
                exitscript=True
                )

vista_ativa = doc.ActiveView
type_vista_ativa = doc.GetElement(vista_ativa.GetTypeId())
nome_tipo_vista = type_vista_ativa.LookupParameter("Type Name").AsString()
if "locação" not in nome_tipo_vista.lower():
    forms.alert(msg="Vista ativa não é uma planta de Locação",
                sub_msg="Ou pode ser que o nome do Tipo da Vista não tenha \'Locação\' escrito",
                exitscript=True
                )

if result:
    for r in result:
        if r == op1:
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


            t = Transaction(doc, __title__)
            t.Start()
            symbol_ids = ponto_de_carga.GetFamilySymbolIds()
            symbol_id_list = List[ElementId](symbol_ids)
            symbols = [doc.GetElement(id) for id in symbol_id_list]
            for funda in fund_sem_pilar:
                ponto_inser = funda.Location.Point
                doc.Create.NewFamilyInstance(ponto_inser, symbols[0], vista_ativa)
            t.Commit()

        # Ainda ta criando em cima do último, se rodar duas vezes

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