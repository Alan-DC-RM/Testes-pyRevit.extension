# -*- coding: utf-8 -*-
__title__ = "Ocultar portas de Vedação"
__doc__ = """Version = 1.0
Date    = 19.03.2025
_____________________________________________________________________
Description:
Oculta portas (Doors) hospedadas em elementos de parede (Walls) de vedação, para não serem exibidas em vistas plantas de armação
_____________________________________________________________________
Como usar a ferramenta:
-> Clicar no botão
-> Mudança vai acontecer no seu proejto

_____________________________________________________________________
Últimos updates:
- [DD.MM.YYYY] - 1.0 RELEASE
_____________________________________________________________________
To-Do:
- 
_____________________________________________________________________
Author: Equipe Sirius"""

# __________________________________________________________________________________________________________________________________________
#
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝ IMPORTS
#
# __________________________________________________________________________________________________________________________________________

import os, sys, math, datetime, time
from Autodesk.Revit.DB import *
#from Autodesk.Revit.UI import *
#from Autodesk.Revit.DB.Structure import *
#from Autodesk.Revit.DB.Architecture import *

from pyrevit import revit, forms

import clr
clr.AddReference("System")
from System.Collections.Generic import List

# Custom Imports



# __________________________________________________________________________________________________________________________________________
#
# ╦  ╦╔═╗╦═╗╦╔═╗╦  ╦╔═╗╦╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╚╗╔╝║╣ ║╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩ ╚╝ ╚═╝╩╚═╝
#
# __________________________________________________________________________________________________________________________________________

doc       = __revit__.ActiveUIDocument.Document   #type: UIDocument
uidoc     = __revit__.ActiveUIDocument            #type: Document
selection = uidoc.Selection                       #type: Selection
app       = __revit__.Application                 #type: UIApplication
rvt_year  = int(app.VersionNumber)
active_view  = doc.ActiveView
#active_level = active_view.GenLevel
PATH_SCRIPT  = os.path.dirname(__file__)

# VARIÁVEIS GLOBAIS



# __________________________________________________________________________________________________________________________________________
#
# ╔═╗╦ ╦╔╗╔╔═╗╔═╗╔═╗╔═╗
# ╠╣ ║ ║║║║║  ║ ║║╣ ╚═╗
# ╚  ╚═╝╝╚╝╚═╝╚═╝╚═╝╚═╝ FUNÇÕES
#
# __________________________________________________________________________________________________________________________________________



# __________________________________________________________________________________________________________________________________________
#
# ╔═╗╦  ╔═╗╔═╗╔═╗╔═╗╔═╗
# ║  ║  ╠═╣╚═╗╚═╗║╣ ╚═╗
# ╚═╝╩═╝╩ ╩╚═╝╚═╝╚═╝╚═╝ CLASSES

#
# __________________________________________________________________________________________________________________________________________



# __________________________________________________________________________________________________________________________________________
#
# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝ MAIN
#
# __________________________________________________________________________________________________________________________________________

if __name__ == '__main__':

    # Pegar as portas do projeto na vista ativa
    doors = FilteredElementCollector(doc, active_view.Id).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

    # Lista de IDs das portas que serão ocultadas
    doors_to_hide = List[ElementId]()

    for door in doors:
        host = door.Host
        if isinstance(host, Wall):
            walltype = doc.GetElement(host.GetTypeId())
            structural_param = walltype.get_Parameter(BuiltInParameter.WALL_STRUCTURAL_SIGNIFICANT)
            structural = structural_param.AsInteger() if structural_param else 0
            walltype_name = walltype.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString()

            if structural == 0 and "Vedação" in walltype_name:
                doors_to_hide.Add(door.Id)

    if doors_to_hide.Count > 0:
        with Transaction(doc, __title__) as t:
            t.Start()
            active_view.HideElements(doors_to_hide)
            t.Commit()

# __________________________________________________________________________________________________________________________________________
    print('-' * 50)
    print('Portas ocultas somente nesta vista, use -Tirar EH da vista- para revelá-las novamente ou Ctrl Z')