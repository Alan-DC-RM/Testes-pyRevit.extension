import ifcopenshell

def verif_ifc_file_str(name):
    if ".ifc" not in name:
        name = name + ".ifc"
    return name

diretorio_ifc = "C:/00. Alan Daré Cordio/01. Atividades/"
arquivo_ifc = "0413-P-EST-AP-RVT-R03"

classe_a_deletar = "IfcOpeningElement"

arquivo_ifc_corrig = verif_ifc_file_str(arquivo_ifc)

nome_novo = arquivo_ifc_corrig.split(".ifc")[0] + "_" + classe_a_deletar + "_REMOVED.ifc"

model = ifcopenshell.open(diretorio_ifc + arquivo_ifc_corrig)

openings = model.by_type(classe_a_deletar)

for opening in openings:
    if "TQS" in opening.Name:
        model.remove(opening)

model.write(diretorio_ifc + nome_novo)