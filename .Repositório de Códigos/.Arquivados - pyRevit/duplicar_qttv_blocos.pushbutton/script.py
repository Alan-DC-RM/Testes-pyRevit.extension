# -*- coding: utf-8 -*-
__title__ = "Duplicar\nQuantitativo Blocos"
from Autodesk.Revit.DB import *
from pyrevit import revit, forms
import sys

doc = __revit__.ActiveUIDocument.Document   #type: UIDocument

# --------------------------------------------------------------------------------------
# Listas a serem populadas, variável de filtro da Schedule, todas as Schedules, Levels e Generic Models para servirem de input da UI na seleção de elementos de listas

blocos = []
paredes = []
schedules_filtradas = []
nomes_schedules_filtradas = []
level_names = []

str_filtro_schedules = "bloco"                                                                                          # Alterar String altera oque vai "filtrar" a lista de Schedules

schedules = FilteredElementCollector(doc) \
    .OfClass(ViewSchedule) \
    .ToElements()
levels = FilteredElementCollector(doc) \
    .OfCategory(BuiltInCategory.OST_Levels) \
    .WhereElementIsNotElementType() \
    .ToElements()
gen_models = FilteredElementCollector(doc) \
    .OfCategory(BuiltInCategory.OST_GenericModel) \
    .WhereElementIsNotElementType() \
    .ToElements()

# --------------------------------------------------------------------------------------
# Seleção de uma schedule para ser duplicada

for schedule in schedules:
    if str_filtro_schedules in schedule.Name.lower():
        nomes_schedules_filtradas.append(schedule.Name)                                                                 # Preciso dos nomes para uma apresentação na UI
        schedules_filtradas.append(schedule)
sel_schedule = forms.SelectFromList.show(
    nomes_schedules_filtradas,
    multiselect=False,
    title="Selecione a schedule originária que será duplicada"
    )                                                                                                  # Tem a função de seleção de Schedules, mas é muito demorada. Talvez dê para eliminar isso e buscar já a Schedule padrão de quantititivo de blocos
indice_schedule_selecionada = nomes_schedules_filtradas.index(sel_schedule)
schedule_selecionada = schedules_filtradas[indice_schedule_selecionada]                                                 # Como o usuário seleciona um Name, eu faço uma correspondência de índice para pegar o Element da classe ViewSchedule

# --------------------------------------------------------------------------------------
# Seleção de um Level para servir de Filtro da seleção de paredes
# Só vamos exibir na UI Paredes presentes no level selecionado

for level in levels:
    level_names.append(level.Name)

sel_level_name = forms.SelectFromList.show(
    level_names,
    multiselect=False,
    width=650,
    title="Selecione o pavimento da(s) parede(s) que servirá de filtro e nome da nova tabela"
)
ind_sel_lev = level_names.index(sel_level_name)
sel_level = levels[ind_sel_lev]

# --------------------------------------------------------------------------------------
# Pegando Definir Pavimentos para criar o dicionário para nomear a Schedule duplicada
# O dicionário terá o Level Name como key e o sufixo como value

pj_info = doc.ProjectInformation

try:
    par_iguais_json = pj_info.LookupParameter("DefinirPavimentos").AsString()                                           # Aqui eu tento pegar o valor do parâmetro
except:
    forms.alert(msg="Parâmetro 'DefinirPavimentos' não carregado no projeto",
                title="Atenção!")                                                                                       # Se não tiver dou o aviso de que ele não está no projeto
    sys.exit()

false = False                                                                                                           # Como o C# escreve os booleanos com letra minúscula inicial ("true" e "false") e armazena eles assim no JSON, o evaluate abaixo vai tratar eles como variáveis no Python, porque True e False em Python têm letra inicial maiúscula
true = True                                                                                                             # Por isso eu declarei as variáveis antes do evaluate, dando o valor equivalente para elas

dyc = {}

if par_iguais_json != "" and par_iguais_json:                                                                           # breve verificação para ver se o parâmetro possui valor, ou seja, se foram definidos pavimentos
    evaluated = eval(par_iguais_json)
    for block in evaluated:                                                                                             # O JSON desse é mais simples que o de Paredes iguais, só tem 1 bloco para cada Level do projeto
        if block["Principalbool"]:                                                                                      # Esse parâmetro só é True para pavimentos principais
            lev = doc.GetElement(ElementId(block["PavimentoId"])).Name
            suf = block["PrefixoPavimento"]                                                                             # Na verdade é sufixo, porque vem depois né, mas de boas, no JSON ta assim
            dyc[lev] = suf                                                                                              # Populando o dicionário para cada Name de Level principal com seu respectivo sufixo
else:
    forms.alert(msg="Pavimentos não foram definidos",
                title="Atenção!")
    sys.exit()
suf = dyc[sel_level_name]                                                                                               # Com o Level inputado na etapa anterior, eu consigo


# --------------------------------------------------------------------------------------
# Seleção de Paredes com base nos blocos presentes no pavimento selecionado

for gen in gen_models:
    gen_type = doc.GetElement(gen.GetTypeId())
    if "BLC" == gen_type.LookupParameter("Tipo de Elemento").AsString():
        blocos.append(gen)
for bloco in blocos:
    if doc.GetElement(bloco.LevelId).Name == sel_level_name:
        paredes.append(bloco.LookupParameter("Parede").AsString())

sel_paredes = forms.SelectFromList.show(
set(paredes),                                                                                                           # Set é o Unique Itens do Python, evitando de ter um item para cada bloco da parede
    multiselect=True,
    width=750,                                                                                                          # Aumentei a largura para caber o texto completo na janela. Fiz isso em cima também
    title="Selecione as paredes do(a) " +
          sel_level_name +
          " as quais você quer criar um novo quantitativo de blocos"
)

# --------------------------------------------------------------------------------------
# Verificando se os Fields Parede e Level estão na tabela originária

fields_ids_o = schedule_selecionada.Definition.GetFieldOrder()
for id in fields_ids_o:
    field_name_o = schedule_selecionada.Definition.GetField(id).GetName()
    if field_name_o == "Level":                                                                                         # Com base na lista de ids de Fields, eu pego o Nome de cada um (que é o nome do Parâmetro), com o método específico GetName da Classe.
        field_level_o = id                                                                                              # Essa abordagem é melhor porque independe da ordem dos Fields
    elif field_name_o == "Parede":
        field_parede_o = id
if not field_level_o:
    forms.alert("Parâmetro 'Level' não existe na tabela originária")
    sys.exit()                                                                                                          # Se não tem os Fields dos parâmetros na tabela, eu nem continuo a rodar o código
elif not field_parede_o:
    forms.alert("Parâmetro 'Parede' não existe na tabela originária")
    sys.exit()

# --------------------------------------------------------------------------------------
# Efetivamente duplicar as tabelas, em uma Transaction do modelo

t = Transaction(doc, "Duplicar Tabelas de Blocos")                                                                      # Alterei aqui porque o __title__ tem um paragrafo, ai fica cortado
t.Start()

schedules_ja_existentes = []                                                                                            # Listas criadas fora do Loop para popularmos no Loop
schedules_criadas = []

for parede in sel_paredes:
    nome_novo = "Padrão Quantitativo de Blocos - " + parede + "." + suf                                                 # Com base nos inputs, eu já crio o nome novo, um para cada parede selecionada, considerando o sufixo do pavimento selecionado também, com base no que está no Definir pavimento, feito em uma etapa mais acima
    if nome_novo not in nomes_schedules_filtradas:                                                                      # Se o nome criado já existe, eu não duplico, evitando erro de ter vistas com mesmo nome
        id_schedule_duplicada = schedule_selecionada.Duplicate(0)                                                       # Duplicate método de ViewSchedule
        schedule_duplicada = doc.GetElement(id_schedule_duplicada)
        fields_ids = schedule_duplicada.Definition.GetFieldOrder()                                                      # Necessariamente tenho que acessar a Schedule Definition, subclasse da classe ViewSchedule
        for i in fields_ids:                                                                                            # Talvez essa parte seja redundante, porque os Fields da duplicada são os mesmos da originária, mas eu mantive assim
            field_name = schedule_duplicada.Definition.GetField(i).GetName()
            if field_name == "Level":
                field_level = i
            elif field_name == "Parede":
                field_parede = i
        filter_level = ScheduleFilter(field_level, ScheduleFilterType.Equal, sel_level.Id)                              # Usando o contrutor Schedule Filter para criar o Filtro de Level. Aqui TEMOS QUE PASSAR O LEVEL ID, para uma regra que seja de Level. Isso não tem escrito no API Docs
        filter_parede = ScheduleFilter(field_parede, ScheduleFilterType.Equal, parede)                                  # Mesma coisa, mas para o filtro da parede
        qtde_filtros_schedule = schedule_duplicada.Definition.GetFilterCount()                                          # Aqui eu faço uma contagem dos filtros da tabela, porque o método SetFilter() pode retornar um erro quando o index que passamos não é válido
        if qtde_filtros_schedule == 3:                                                                                  # SetFilter() altera um filtro já existente.
            schedule_duplicada.Definition.SetFilter(1, filter_level)
            schedule_duplicada.Definition.SetFilter(2, filter_parede)
        elif qtde_filtros_schedule == 2:
            schedule_duplicada.Definition.SetFilter(1, filter_level)
            schedule_duplicada.Definition.AddFilter(filter_parede)                                                      # AddFilter() adiciona. Eu tentei prever os casos que podemos ter um filtro apenas, e idepende da ordem.
        elif qtde_filtros_schedule < 2:
            schedule_duplicada.Definition.AddFilter(filter_level)
            schedule_duplicada.Definition.AddFilter(filter_parede)                                                      # Talvez teremos que revisitar essa rotina se modificarmos a QUANTIDADE de filtros na tabela de blocos, uma solicitação que está aberta da FCB pede isso, para desconsiderar grampos
        schedule_duplicada.Name = nome_novo
        schedules_criadas.append(nome_novo)                                                                             # Populo a lista do Output para entregar ao usuário o que foi criado
    else:
        schedules_ja_existentes.append(nome_novo)                                                                       # E das que não foram criadas porque já existem também

t.Commit()

msg = ""

if schedules_criadas and not schedules_ja_existentes:
    msg = (
            "As seguintes tabelas foram criadas\n" +
            "\n".join(schedules_criadas)+
            "\n\nTodas foram criadas com sucesso, nenhuma delas já constava no projeto"
    )
elif not schedules_criadas and schedules_ja_existentes:
    msg = ("Nenhuma tabela foi criada" +
           "\n\nTodas elas já constavam no modelo.\nApague as seguintes tabelas e rode a ferramenta novamente:\n" +
           "\n".join(schedules_ja_existentes)
           )
elif schedules_criadas and schedules_ja_existentes:
    msg = ("As seguintes tabelas foram criadas\n" +
           "\n".join(schedules_criadas) +
           "\n\nE as seguintes tabelas já existem no projeto e não foram recriadas:\n" +
           "\n".join(schedules_ja_existentes)
           )
else:
    msg = "Erro na ferramenta, chame a equipe BIM"

forms.alert(msg)