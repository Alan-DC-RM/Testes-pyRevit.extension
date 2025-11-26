# from System.Collections.Generic import List
# Inclui esse import no init do RPS, localizado em C:\Users\alan.cordio\AppData\Roaming\Autodesk\Revit\Addins\2023\RevitPythonShell\init.py

paredes = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
id_paredes = []
for parede in paredes:
    id_parede = parede.Id
    id_paredes.append(id_parede)

uidoc.Selection.SetElementIds(List[ElementId](id_paredes))
# print(id_paredes)

elementos_selecionados = GetSelectedElements(doc)
alert(f"{len(elementos_selecionados)} elementos foram selecionados")
