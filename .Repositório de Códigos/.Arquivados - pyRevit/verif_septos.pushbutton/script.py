# -*- coding: utf-8 -*-
__title__ = "Verificação Septos e Geometria de Blocos"

from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument


blocos = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
opt = Options()
erros = False
list_erros = []

t = Transaction(doc, __title__)
t.Start()

for b in blocos:
    og = b.GetOriginalGeometry(opt)
    for solid in og:
        if solid.GraphicsStyleId != ElementId.InvalidElementId:
            subcat = doc.GetElement(solid.GraphicsStyleId).Name
            faces = solid.Faces
            for f in faces:
                mat = doc.GetElement(f.MaterialElementId).Name
                break
            if mat.strip().upper() == "SEPTO" and subcat != "Bloco - Septo":
                b.LookupParameter("Comments").Set("Erro no septo")
                erros = True
                list_erros.append("Septo do Bloco - " + b.Name)
            if subcat == "Bloco - Septo" and mat.strip().upper() != "SEPTO":
                b.LookupParameter("Comments").Set("Erro no septo")
                erros = True
                list_erros.append("Septo do Bloco - " + b.Name)
            if mat.strip().upper() in ["BLOCO DE CONCRETO", "BLOCO ACÚSTICO", "BLOCO CERÂMICO"] and subcat != "Bloco - Geometria":
                b.LookupParameter("Chave").Set("Erro na geometria")
                erros = True
                list_erros.append("Geometria do Bloco - " + b.Name)
            if subcat == "Bloco - Geometria" and mat.strip().upper() not in ["BLOCO DE CONCRETO", "BLOCO ACÚSTICO", "BLOCO CERÂMICO"]:
                b.LookupParameter("Chave").Set("Erro na geometria")
                erros = True
                list_erros.append("Geometria do Bloco - " + b.Name)
t.Commit()

if erros:
    print("Houve erros")
    print(list_erros)
else:
    print("Tudo OK")
