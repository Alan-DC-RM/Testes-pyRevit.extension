import clr
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

def unwrap(item):
    if isinstance(item, list):
        return [UnwrapElement(i) for i in item]
    else:
        return UnwrapElement(item)

levels_lajes_input = IN[0]


doc = DocumentManager.Instance.CurrentDBDocument


levels = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_Levels) \
        .WhereElementIsNotElementType() \
        .ToElements()
levels_lajes = unwrap(levels_lajes_input)


levels_id = []
levels_lajes_id = []


for level in levels:
	levels_id.append(level.Id)
for level_lajes in levels_lajes:
	levels_lajes_id.append(level_lajes.Id)


levels_com_lajes = []
levels_sem_lajes = []


for id in levels_id:
	if id in levels_lajes_id:
		levels_com_lajes.append(id)
	else:
		levels_sem_lajes.append(id)

OUT = levels_com_lajes, levels_sem_lajes
