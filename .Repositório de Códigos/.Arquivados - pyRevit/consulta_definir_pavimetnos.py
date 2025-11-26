# -*- coding: utf-8 -*-
__title__ = "Temp - Pavimentos"
from Autodesk.Revit.DB import *
from pyrevit import revit, forms
import sys

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument

pj_info = doc.ProjectInformation  # pegando projetcinfo para pegar info de Paredes Iguais (abaixo). Daria para pegar com o FilteredElement, ele é uma categoria e passar para .ToElements(), mas essa é uma opção melhor

try:
    par_iguais_json = pj_info.LookupParameter("DefinirPavimentos").AsString()  # Aqui eu tento pegar o valor do parâmetro
except:
    forms.alert(msg="Parâmetro 'DefinirPavimentos' não carregado no projeto",
                title="Atenção!")  # Se não tiver dou o aviso de que ele não está no projeto
    sys.exit()

false = False
true = True

dyc = {}
if par_iguais_json != "" and par_iguais_json:
    evaluated = eval(par_iguais_json)
    for block in evaluated:
        if block["Principalbool"]:
            lev = doc.GetElement(ElementId(block["PavimentoId"])).Name
            pref = block["PrefixoPavimento"]
            dyc[lev] = pref
else:
    forms.alert(msg="Pavimentos não foram definidos",
                title="Atenção!")
    sys.exit()
