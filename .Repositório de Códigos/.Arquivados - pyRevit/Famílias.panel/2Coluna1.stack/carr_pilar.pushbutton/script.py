# -*- coding: utf-8 -*-
__title__ = "Pilar Retangular TQS"

from Autodesk.Revit.DB import Document, Transaction
from System.IO import Path

# Caminho direto do arquivo da família desejada - Alterar aqui, caso mude!
fampath = r"N:\Engenharia\BIM\02-Familias\02-Biblioteca TQS\2022 (principal) - 2023 - 2024\Families\TQS - Pilar retangular.rfa"

doc = __revit__.ActiveUIDocument.Document  # type: UIDocument

t = Transaction(doc, __title__)
t.Start()
try:
    print("Carregando família: " + Path.GetFileName(fampath.split(".rfa")[0]))
    doc.LoadFamily(fampath)
    print("Família carregada com sucesso!")
except:
    print("Falha ao carregar a família.")
t.Commit()
