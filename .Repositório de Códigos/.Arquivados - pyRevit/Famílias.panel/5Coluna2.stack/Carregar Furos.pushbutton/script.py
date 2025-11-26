# -*- coding: utf-8 -*-
__title__ = "Furos"

from operator import truediv

'''
Esse código serve para carregar as famílias de blocos de alvenaria no Revit.
'''

from System.IO import Directory, SearchOption
from Autodesk.Revit.DB import *
import os

# Lista de diretórios para buscar as famílias
dirs = [r"N:\Engenharia\BIM\02-Familias\01-Biblioteca RM\Furos"]

# Configurações
searchstring = "*.rfa"
foundfiles = []
apoio = []

for d in dirs:
    if Directory.Exists(d):
        dirfiles = Directory.GetFiles(d, searchstring, SearchOption.TopDirectoryOnly)
        foundfiles.extend(dirfiles)
    else:
        print("não encontrei")
for f in foundfiles:
    apoio.append(f)
print("encontrei")
doc = __revit__.ActiveUIDocument.Document  #type: UIDocument
fampaths = foundfiles
elementlist = []
booleans = []
print(foundfiles)

t = Transaction(doc, __title__)                                                                                         # Começando uma nova transaction agora com o título do script
t.Start()
for fampath in fampaths:
    try:
        print("ok")
        doc.LoadFamily(fampath)
        booleans.append(True)
    except:
        booleans.append(False)
t.Commit()
#print(foundfiles)
