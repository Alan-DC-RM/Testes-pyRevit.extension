# -*- coding: utf-8 -*-
__title__ = "Ajuste Esp Média Lajes"
__doc__ = """Version = 1.0
Date    = 17.06.2025
_____________________________________________________________________
Description:
Este é um Template para scripts do pyRevit
_____________________________________________________________________
Como usar a ferramenta:
-> 
_____________________________________________________________________
Últimos updates:
- [DD.MM.YYYY] - 1.1 UPDATE - Novas Features
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
from collections import defaultdict


# __________________________________________________________________________________________________________________________________________
#
# ╦  ╦╔═╗╦═╗╦╔═╗╦  ╦╔═╗╦╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╚╗╔╝║╣ ║╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩ ╚╝ ╚═╝╩╚═╝
#
# __________________________________________________________________________________________________________________________________________

doc             = __revit__.ActiveUIDocument.Document   #type: UIDocument
uidoc           = __revit__.ActiveUIDocument            #type: Document
selection       = uidoc.Selection                       #type: Selection
app             = __revit__.Application                 #type: UIApplication
rvt_year        = int(app.VersionNumber)
active_view     = doc.ActiveView
#active_level   = active_view.GenLevel
PATH_SCRIPT     = os.path.dirname(__file__)

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

    floors_types = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_Floors) \
        .WhereElementIsNotElementType() \
        .ToElements()

    floors = []
    types_floors = []
    for elem in floors_types:
        id_do_type = elem.GetTypeId()
        type_floor = doc.GetElement(id_do_type)
        valor_espessura = (


           # Parei aqui


            type_bloco.LookupParameter("Tipo de Elemento").AsString())
        if valor_tipo_elemento == "BLC":
            blocos.append(elem)
            types_blocos.append(type_bloco)

    levels_blocos = []

    for bloco in blocos:
        id_level = bloco.LevelId
        level_bloco = doc.GetElement(id_level)
        nome_level_bloco = (level_bloco.Name)
        levels_blocos.append(nome_level_bloco)

    levels_unicos = set(levels_blocos)
    level_name_input = forms.SelectFromList.show(
        levels_unicos,
        title="Selecione o Nível",
        button_name="Selecionar",
        multiselect=False
    )

    blocos_input = []

    for bloco in blocos:
        id_level = bloco.LevelId
        level_bloco = doc.GetElement(id_level)
        nome_level_bloco = (level_bloco.Name)
        if nome_level_bloco == level_name_input:
            blocos_input.append(bloco)

    paredes = []

    for bloco_input in blocos_input:
        parede_bloco = bloco_input.LookupParameter("Parede").AsString()
        paredes.append(parede_bloco)

    paredes_unicas = set(paredes)

    t = Transaction(doc,__title__)
    t.Start()

    t.Commit()

# __________________________________________________________________________________________________________________________________________
    print('-' * 50)
    print(paredes_unicas)