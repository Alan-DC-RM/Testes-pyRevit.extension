# -*- coding: utf-8 -*-
__title__ = "Ajuste de Blocos Poligonais"
from Autodesk.Revit.DB import *
from pyrevit import revit, forms

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument

if __name__ == '__main__':

    conects = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_StructConnections) \
        .WhereElementIsNotElementType() \
        .ToElements()

    blocos_ajust = []

    t = Transaction(doc, __title__)
    t.Start()
    for conect in conects:
        type_name = conect.Name
        if "Fund Family" in type_name:
            p = conect.Location.Point
            if (p.X != 0) and (p.Y != 0):
                move_vec = XYZ(-p.X, -p.Y, 0)
                id_bloc_polig = (conect.Id)
                ElementTransformUtils.MoveElement(doc, id_bloc_polig, move_vec)
                blocos_ajust.append(conect)
        else:
            pass
    t.Commit()

    if blocos_ajust:
        msg = "Os seguintes blocos foram ajustados:\n" + "\n".join(bloco.LookupParameter("Titulo").AsString() for bloco in blocos_ajust)
    else:
        msg = "Nenhum bloco foi ajustado."

    forms.alert(msg)