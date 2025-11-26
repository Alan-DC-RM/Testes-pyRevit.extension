# -*- coding: utf-8 -*-
__title__ = "Inserir PCs"

from Autodesk.Revit.DB import *
from pyrevit import forms
from System.Collections.Generic import List
import math
import clr
clr.AddReference('Microsoft.Office.Interop.Excel')
from Microsoft.Office.Interop import Excel

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument

blocos = []
blocos = None
from pyrevit import forms

op1 = "Inserir PCS em blocos sem pilares"
op2 = "Preencher cargas"

boxes = [
    op1,
    op2
]

result = forms.SelectFromList.show(boxes, "Selecione um", multiselect = True)
if result:
    for r in result:
        if r == op1:
            #Código para inserir PCs em blocos sem pilares
            fams = FilteredElementCollector(doc) \
                .OfClass(Family) \
                .ToElements()
            achou = False
            for fam in fams:
                if fam.Name == "Ponto de Carga":
                    achou = True
                    break
            if not achou:
                forms.alert("Família de Ponto de Carga não carregada no modelo ou com nome alterado",
                                title="Alerta!", exitscript=True)
            sconnections = FilteredElementCollector(doc) \
                .OfCategory(BuiltInCategory.OST_StructConnections)\
                .WhereElementIsNotElementType().ToElements()
            not_cubetas = []
            for s in sconnections:
                tipo = s.Symbol
                famname = tipo.FamilyName
                if not famname == "Cubeta":
                    not_cubetas.append(s)
            scolumns = FilteredElementCollector(doc) \
                .OfCategory(BuiltInCategory.OST_StructuralColumns)\
                .WhereElementIsNotElementType().ToElements()
            pilares_primeiro_lance = []
            geo_pilares = []

            for p in scolumns:
                chave = p.LookupParameter("Chave").AsString()
                if "//0" in chave and chave:
                    pilares_primeiro_lance.append(p)
            for l in pilares_primeiro_lance:
                opt = Options()
                geom = l.get_Geometry() #teoricamente precisa ser um sólido
                if isinstance(l, Solid):
                    geo_pilares.append(l)
                elif isinstance(l, GeometryInstance):
                    inst_geom = l.GetInstanceGeometry()
                    for sub in inst_geom:
                        if isinstance(sub, Solid):
                            geo_pilares.append(sub)
                            '''
            opt = Options()
            opt.IncludeNonVisibleObjects = False
            associacoes = {}
            for pilar in pilares_primeiro_lance:
                ps = get_solid(pilar, opt)
                if ps is None:
                    continue
                pbbox = ps.GetBoundingBox()
                melhor_bloco = None
                melhor_dz = float("inf")
                for bloco in blocos:
                    bs = get_solid(bloco, opt)
                    if bs is None:
                        continue
                    bbbox = bs.GetBoundingBox()
                    if not bbox_intersect(pbbox, bbbox):
                        continue
                    try:
                        inters = BooleanOperationsUtils.ExecuteBooleanOperation(
                            ps, bs, BooleanOperationsType.Intersect
                        )
'''
        if r == op2:
            #Preencher as cargas a partir da tabela
            input_tabela = forms.ask_for_string(
                default="R00-EX-Cargas-21-10-2025",
                prompt="Nome da aba",
                title="Excel"
            )

            values = []

            '''
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