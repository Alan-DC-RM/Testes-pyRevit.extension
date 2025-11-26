import clr
clr.AddReference('RevitServices')
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

conects = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructConnections).WhereElementIsNotElementType().ToElements()

TransactionManager.Instance.EnsureInTransaction(doc)
blocos_ajust = []

for conect in conects:
	type_name = conect.Name
	if "Fund Family" in type_name:
		p = conect.Location.Point
		move_vec = XYZ(-p.X, -p.Y, 0)
		id_bloc_polig = (conect.Id)
		ElementTransformUtils.MoveElement(doc,id_bloc_polig,move_vec)
		blocos_ajust.append(conect)
	else:
		pass

TransactionManager.Instance.TransactionTaskDone()

OUT = blocos_ajust