# -*- coding: utf-8 -*-
__title__ = "Pilares"

from operator import truediv

'''
Esse código serve para carregar as famílias de blocos de alvenaria no Revit.
'''

from System.IO import Directory, SearchOption, Path
from Autodesk.Revit.DB import *
import os

# Lista de diretórios para buscar as famílias
dirs = [
    r"N:\Engenharia\BIM\02-Familias\01-Biblioteca RM\Documentação\Tags\Tags de Pilares"
]

# Configurações
searchstring = "*.rfa"
foundfiles = []
apoio = []

for d in dirs:
    d = d.strip()  # evita espaço acidental no fim
    if Directory.Exists(d):
        dirfiles = Directory.GetFiles(d, searchstring, SearchOption.TopDirectoryOnly)
        print("OK:", d, "->", len(dirfiles), "arquivos .rfa")
        foundfiles.extend(dirfiles)
    else:
        print("não encontrei:", d)

for f in foundfiles:
    apoio.append(f)

print("total encontrados:", len(foundfiles))
doc = __revit__.ActiveUIDocument.Document  # type: UIDocument
fampaths = foundfiles
booleans = []

t = Transaction(doc, __title__)
t.Start()
for fampath in fampaths:
    try:
        print("Carregando:", Path.GetFileName(fampath))
        ok = doc.LoadFamily(fampath)  # retorna bool
        booleans.append(bool(ok))
    except:
        print("Falhou:", Path.GetFileName(fampath))
        booleans.append(False)
t.Commit()
