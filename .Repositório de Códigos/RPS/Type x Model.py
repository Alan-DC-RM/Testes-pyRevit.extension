from Autodesk.Revit.DB import *

tipos_telas = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_FabricReinforcement).WhereElementIsElementType().ToElements()

models = []
type_names = []
telas_erradas = []

for tela in tipos_telas:
	type_name = tela.Name
	if "." not in type_name:
		model = tela.LookupParameter("Model").AsString()
		if type_name != model:
			telas_erradas.append(type_name)

print(telas_erradas)

