# -*- coding: utf-8 -*-
__title__ = "Vigas de Contenção"
from Autodesk.Revit.DB import *
from pyrevit import revit, forms

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument

if __name__ == '__main__':

    vigas = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_StructuralFraming) \
        .WhereElementIsNotElementType() \
        .ToElements()

    vigs_cort = []
    vigs_par = []

    t = Transaction(doc, __title__)
    t.Start()

    for viga in vigas:
        tit = viga.LookupParameter("Titulo").AsString().upper()
        if ("CORT" in tit) or ("CONT" in tit):
            viga.LookupParameter("Contenção").Set(True)
            vigs_cort.append(tit)
        elif "PAR" in tit:
            vigs_par.append(tit)
        else:
            viga.LookupParameter("Contenção").Set(False)
    t.Commit()

    forms.alert("As seguintes vigas foram setadas como Conteções: \n" + "\n".join(vig for vig in vigs_cort) + "\n\nE as seguintes vigas não foram alteradas: \n" +"\n".join(vig for vig in vigs_par) + "\n\nO restande das vigas foram setas como NÃO contenções.")