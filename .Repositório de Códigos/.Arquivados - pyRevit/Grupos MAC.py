# -*- coding: utf-8 -*-
__title__ = "Agrupamento Fiadas MAC"

import sys

from Autodesk.Revit.DB import *
from pyrevit import forms
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument

generic_models = FilteredElementCollector(doc) \
    .OfCategory(BuiltInCategory.OST_GenericModel) \
    .WhereElementIsNotElementType() \
    .ToElements()

levels_raw = FilteredElementCollector(doc) \
    .OfCategory(BuiltInCategory.OST_Levels) \
    .WhereElementIsNotElementType() \
    .ToElements()

levels_sorted = sorted(levels_raw, key=lambda lv: lv.Elevation, reverse=True)

blocos = []
#types_blocos = []

for elem in generic_models:
    id_do_type = elem.GetTypeId()
    type_bloco = doc.GetElement(id_do_type)
    valor_tipo_elemento = type_bloco.LookupParameter("Tipo de Elemento").AsString()
    if valor_tipo_elemento == "BLC":
        blocos.append(elem)
        #types_blocos.append(type_bloco)

level_names = []

for level in levels_sorted:
    level_names.append(level.Name)

level_name_input = forms.SelectFromList.show(
    level_names,
    title="Selecione o Nível",
    button_name="Selecionar",
    multiselect=False
)

levels_blocos = []
blocos_input = []

for bloco in blocos:
    id_level = bloco.LevelId
    level_bloco = doc.GetElement(id_level)
    nome_level_bloco = level_bloco.Name
    levels_blocos.append(nome_level_bloco)
    if nome_level_bloco == level_name_input:
        blocos_input.append(bloco)

dic_1a_fiada = {}
dic_2a_fiada = {}

for bloco_input in blocos_input:
    elev_bloco = bloco_input.LookupParameter("Elevation from Level").AsDouble()
    elev_bloco_cm = round(elev_bloco * 30.48, 2)

    if elev_bloco_cm != 1 and elev_bloco_cm != 21:
        continue

    parede_bloco = bloco_input.LookupParameter("Parede").AsString()

    if not parede_bloco:
        forms.alert("É necessário definir as paredes para agrupá-las!\n\nInclusive Vedação!!")
        sys.exit()

    if elev_bloco_cm == 1:
        if parede_bloco not in dic_1a_fiada.keys():
            dic_1a_fiada[parede_bloco] = {}
        nome_grupo = level_name_input + " - 1a fiada - " + parede_bloco
        if nome_grupo not in dic_1a_fiada[parede_bloco]:
            dic_1a_fiada[parede_bloco][nome_grupo] = List[ElementId]()
        dic_1a_fiada[parede_bloco][nome_grupo].Add(bloco_input.Id)

    elif elev_bloco_cm == 21:
        if parede_bloco not in dic_2a_fiada.keys():
            dic_2a_fiada[parede_bloco] = {}
        nome_grupo = level_name_input + " - 2a fiada - " + parede_bloco
        if nome_grupo not in dic_2a_fiada[parede_bloco]:
            dic_2a_fiada[parede_bloco][nome_grupo] = List[ElementId]()
        dic_2a_fiada[parede_bloco][nome_grupo].Add(bloco_input.Id)

t = Transaction(doc, __title__)
t.Start()
rodou = False
for parede in dic_1a_fiada:
    for nome in dic_1a_fiada[parede]:
        ids = dic_1a_fiada[parede][nome]
        grupo = doc.Create.NewGroup(ids)
        grupo.GroupType.Name = nome
        rodou = True
for parede in dic_2a_fiada:
    for nome in dic_2a_fiada[parede]:
        ids = dic_2a_fiada[parede][nome]
        grupo = doc.Create.NewGroup(ids)
        grupo.GroupType.Name = nome
        rodou = True
if rodou:
    forms.alert("Sucesso!",
                sub_msg="Aviso importante!\nEssa rotina considera apenas Generic Models do Tipo BLC que têm Elevation from Level de 1cm ou 21cm.\n\nQualquer valor fora disso não foi considerado!",
                ok=True)
else:
    forms.alert("Aviso!",
                sub_msg="Nada foi feito!",
                ok=True)
t.Commit()
