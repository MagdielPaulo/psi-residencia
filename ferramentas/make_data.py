"""Build site/questions.json + site/explicacoes.json from parsed questions and expl/*.json."""
import json, glob, os, re, unicodedata

B = "/home/claude/build"
d = json.load(open(f"{B}/questions.json"))

SHORT = {"pe": ("SES-PE", 7), "df": ("SES-DF", 13), "go": ("Goiás", 29), "eb": ("EBSERH", 5), "rj": ("Rio", 17), "sc": ("SC", 23)}
for k, (s, seed) in SHORT.items():
    d["blocks"][k]["short"] = s
    d["blocks"][k]["seed"] = seed

def short(e):
    t = e["title"]
    for a, b in [("Perfil Hospitalar", "Hospitalar"), ("Perfil Atenção Básica", "Atenção Básica"), ("Perfil Saúde Coletiva", "Saúde Coletiva"),
                 ("Saúde da Família – Interiorização", "Interiorização"), ("HC/UFG", "HC/UFG"), ("COREMU/SES-GO", "SES-GO"),
                 ("Grupo Psicologia", "Grupo Psicologia"), ("Psicólogo – Psicologia Hospitalar", "Hospitalar"),
                 ("Psicólogo – Organizacional", "Organizacional"), ("Residência em Saúde Mental", "Saúde Mental (Pinel)"),
                 ("Barra Velha", "Barra Velha"), ("Questões comuns", "Comuns 1–80")]:
        if t.startswith(a):
            return b
    m = re.match(r"Programa (\d+) · (.*)", t)
    if m:
        return m.group(2)
    return t

for e in d["exams"]:
    e["short"] = short(e)
    e["prelim"] = "PRELIMINAR" in e.get("keysrc", "")

def norm(s):
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()

RULES = [
    ("etica", r"codigo de etica|resolucao cfp|cfp n|laudo|parecer|declaracao|atestado|relatorio psicolog|documentos escritos|sigilo|prontuario|conselho federal de psicologia|registro documental"),
    ("palia", r"paliativ|luto|morte|morrer|terminal|kubler|tanatolog|enlutad|eutanasia|ortotanasia|distanasia|mistanasia"),
    ("psican", r"freud|lacan|psicanal|edipo|recalque|inconsciente|pulsao|transferencia|winnicott|melanie klein|bion|mecanismo de defesa|id,|superego|ego "),
    ("smental", r"caps|reforma psiquiatrica|raps|10\.216|saude mental|manicom|reducao de danos|alcool e outras drogas|residencia terapeutica|desinstitucionaliz|crise"),
    ("psicopat", r"dsm|cid-1|transtorno|delirio|alucinac|esquizofren|psicopatolog|sintoma|depress|ansiedade generalizada|bipolar|tept|panico|toc|autis|tdah"),
    ("hosp", r"hospital|uti|internac|paciente|equipe de saude|adoecimento|cirurg|psicologia da saude|oncolog|doenca cronica"),
    ("aval", r"psicodiagnost|avaliacao psicolog|teste|satepsi|entrevista|anamnese|psicometr|wisc|wais|rorschach"),
    ("teorias", r"rogers|gestalt|cognitivo|comportamental|skinner|beck|terapia|psicoterapia|behavior|sistemic|jung|psicodrama|humanist|fenomenolog|existencial"),
    ("desenv", r"piaget|vygotsk|erikson|desenvolvimento|infancia|adolescen|idoso|envelhec|apego|bowlby"),
    ("infancia", r"eca|estatuto da crianca|crianca|familia|maus-tratos|abuso sexual"),
    ("org", r"organizac|trabalho|lideranc|motivac|recrutamento|selecao de pessoal|clima|gestao de pessoas|herzberg|maslow|burnout|treinamento"),
    ("social", r"grupo|comunidade|psicologia social|pichon|bleger|representac|preconceito|territorio"),
    ("neuro", r"neuropsic|memoria|atencao|funcoes executivas|lesao|demencia|cognic"),
    ("multi", r"interdisciplin|multiprofission|transdisciplin|equipe"),
    ("basic", r"historia da psicologia|wundt|titchener|funcionalis|estruturalis|kant|percepc|emoc|personalidade|aprendizagem"),
]
SUS_RULES = [
    ("epi", r"epidemiolog|incidencia|prevalencia|indicador|mortalidade|notificac|vigilancia|coeficiente|taxa|estudo de coorte|caso-controle|letalidade|sinan|sim |sinasc|morbidade"),
    ("sus-leg", r"8\.080|8080|8\.142|7\.508|constituicao|lei complementar|lei n|decreto|portaria|conselho de saude|conferencia de saude|comissao intergestor|financiamento"),
    ("sus-pol", r"pnab|atencao basica|humaniza|redes de atencao|politica nacional|estrategia saude da familia|nasf|e-multi|regulac|educacao permanente|equidade|promocao da saude"),
]

def guess(q):
    txt = norm(q["stem"] + " " + " ".join(q["options"]))
    if q["area"] == "sus":
        for t, rx in SUS_RULES:
            if re.search(rx, txt):
                return t
        return "sus-leg"
    for t, rx in RULES:
        if re.search(rx, txt):
            return t
    return "outros"

expl = {}
for f in sorted(glob.glob(f"{B}/expl/*.json")):
    expl.update(json.load(open(f)))

# share explanations between identical questions that appear in more than one exam
def sig(q):
    return re.sub(r"\W+", "", (q["stem"][:160] + "|".join(q["options"])).lower()) + q["answer"]
bysig = {}
for q in d["questions"]:
    if q["id"] in expl:
        bysig.setdefault(sig(q), q["id"])
shared = 0
for q in d["questions"]:
    if q["id"] not in expl and sig(q) in bysig:
        expl[q["id"]] = expl[bysig[sig(q)]]; shared += 1
print("shared explanations:", shared)
figs = json.load(open(f"{B}/figs.json")) if os.path.exists(f"{B}/figs.json") else {}
for q in d["questions"]:
    q["topic"] = guess(q)
    if q["id"] in figs and not q.get("img"):
        q["img"] = figs[q["id"]]
    x = expl.get(q["id"])
    if x and x.get("area"):
        q["area"] = x["area"]

os.makedirs("/home/claude/site", exist_ok=True)
json.dump(d, open("/home/claude/site/questions.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump(expl, open("/home/claude/site/explicacoes.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(d["questions"]), "questions;", len(expl), "explanations;",
      os.path.getsize("/home/claude/site/questions.json") // 1024, "KB +", os.path.getsize("/home/claude/site/explicacoes.json") // 1024, "KB")

# standalone package: data as JS globals so index.html works when opened as a local file
os.makedirs("/home/claude/site/dados", exist_ok=True)
with open("/home/claude/site/dados/questoes.js", "w") as fh:
    fh.write("window.PSI_QUESTOES = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n")
with open("/home/claude/site/dados/explicacoes.js", "w") as fh:
    fh.write("window.PSI_EXPLICACOES = " + json.dumps(expl, ensure_ascii=False, separators=(",", ":")) + ";\n")
