"""Parse exam texts + answer keys into a single questions JSON.

usage: python3 -I parse.py <raw_dir> <out_json>
raw_dir must contain clean/ (exam text), txt/Gabaritos/ (answer keys), txt/Provas/*.ocr.txt
"""
import json, re, sys, os, unicodedata

RAW = sys.argv[1]
OUT = sys.argv[2]

# ---------------------------------------------------------------- answer keys

def key_section(path, start_re, stop_re=None, nth=1):
    txt = open(path, encoding="utf-8", errors="replace").read()
    ms = list(re.finditer(start_re, txt, re.M))
    m = ms[nth - 1]
    rest = txt[m.end():]
    if stop_re:
        s = re.search(stop_re, rest, re.M)
        if s:
            rest = rest[: s.start()]
    return rest


ANS = r"(?:NULA|ANULADA|[A-E]|#|X|\*[A-E])"


def parse_key(text):
    """Return {num: letter|None}. Handles 'NN X' pair rows and grid (numbers row / letters row)."""
    key = {}
    lines = [l for l in text.splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        l = lines[i]
        toks = l.split()
        pairs = re.findall(r"\b(\d{1,3})\s*-?\s+(" + ANS + r")(?=\s|$)", l)
        numtoks = [t for t in toks if re.fullmatch(r"\d{1,3}", t)]
        nums_only = len(numtoks) >= 3 and all(re.fullmatch(r"\d{1,3}", t) or re.fullmatch(r"[A-ZÀ-Ú]{4,}", t) for t in toks)
        if nums_only:
            toks = numtoks
        if nums_only and i + 1 < len(lines):
            nxt = [t for t in lines[i + 1].split() if re.fullmatch(ANS, t)]
            if len(nxt) == len(toks):
                for n, a in zip(toks, nxt):
                    key[int(n)] = norm_ans(a)
                i += 2
                continue
            # FGV/IBFC grids sometimes carry a label on the letters row
            nxt_all = re.findall(r"(?<![A-Za-zÀ-ú])(" + ANS + r")(?![A-Za-zÀ-ú])", lines[i + 1])
            if len(nxt_all) == len(toks):
                for n, a in zip(toks, nxt_all):
                    key[int(n)] = norm_ans(a)
                i += 2
                continue
        if pairs:
            for n, a in pairs:
                key[int(n)] = norm_ans(a)
        i += 1
    return key


def norm_ans(a):
    a = a.strip("*")
    if a in ("NULA", "ANULADA", "#", "X"):
        return None
    return a


def inline_key(s):
    out = {}
    for n, a in re.findall(r"(\d+)\s+(NULA|[A-E])", s):
        out[int(n)] = None if a == "NULA" else a
    return out

# ---------------------------------------------------------------- exams

G = os.path.join(RAW, "txt", "Gabaritos")
C = os.path.join(RAW, "clean")
O = os.path.join(RAW, "txt", "Provas")

SUSPE_Q = r"^\s*(\d{2})\s*[\.\)]\s+"
SUSPE_OPT = r"(?:(?<=\s)|^)([A-Ea-e])\)\s?"
IADES_Q = r"^\s*▬?\s*QUEST[ÃA]O\s+(\d{1,3})\b[\s_▬]*"
PAREN_OPT = r"(?:(?<=\s)|^)\(([A-E])\)\s"
IBFC_Q = r"^\s*(\d{1,2})\)\s+"
IBFC_OPT = r"(?:(?<=\s)|^)([a-e])\)\s"
BARE_Q = r"^\s*(\d{1,2})\s*$"

HDR_COMMON = [r"^\s*\d{1,2}\s*$", r"^<<<PAGE", r"^HOSPITALAR / PSICOLOGIA", r"^ATENÇÃO BÁSICA / PSICOLOGIA",
              r"^SAÚDE COLETIVA", r"CADERNO \d+", r"^PROCESSO SELETIVO$", r"^RP-1/SES-DF", r"^IBFC_\d+",
              r"^EMPRESA BRASILEIRA DE SERVIÇOS", r"^UFG/CS", r"^Tipo “U”", r"PSICOLOGIA– TIPO", r"^\s*Página \d+",
              r"^PERFIL SAÚDE DA FAMÍLIA", r"^PERFIL SAÚDE COLETIVA – PSICOLOGIA$", r"^\(PSICOLOGIA\)$", r"^INTERIORIZAÇÃO", r"^www\.", r"^Psicólogo\s*$"]

EXAMS = [
    # ---------------- SES-PE (UPE / IAUPE) ----------------
    dict(id="pe25h", block="pe", title="Perfil Hospitalar · Caderno 57", year=2025, banca="UPENET/IAUPE",
         src=os.path.join(O, "residencia_hospitalar_psicologia.ocr.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         key=inline_key("01 A 02 E 03 E 04 C 05 C 06 A 07 D 08 B 09 B 10 D 11 B 12 E 13 B 14 E 15 D 16 E 17 B 18 C 19 E 20 B 21 C 22 A 23 D 24 E 25 E 26 E 27 D 28 B 29 B 30 C 31 A 32 B 33 D 34 B 35 C 36 D 37 A 38 B 39 A 40 D 41 B 42 E 43 E 44 A 45 C 46 D 47 C 48 A 49 E 50 D"),
         keysrc="Gabarito definitivo 2025 (upenet.com.br)", sus=(1, 20)),
    dict(id="pe25ab", block="pe", title="Perfil Atenção Básica · Caderno 77", year=2025, banca="UPENET/IAUPE",
         src=os.path.join(O, "residencia_atencao_basica_psicologia.ocr.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         key=inline_key("01 E 02 NULA 03 E 04 C 05 E 06 C 07 C 08 D 09 B 10 B 11 A 12 B 13 D 14 E 15 E 16 E 17 B 18 A 19 E 20 E 21 C 22 A 23 B 24 A 25 D 26 B 27 C 28 C 29 E 30 A 31 B 32 E 33 B 34 A 35 C 36 A 37 E 38 B 39 E 40 C 41 A 42 D 43 B 44 A 45 D 46 C 47 C 48 E 49 E 50 C"),
         keysrc="Gabarito definitivo 2025 (upenet.com.br)", sus=(1, 30)),
    dict(id="pe24h", block="pe", title="Perfil Hospitalar · Caderno 57", year=2024, banca="UPENET/IAUPE",
         src=os.path.join(C, "HOSPITALAR PSICOLOGIA 2024 (2).txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         keyfile=("GABARITO  DEFINITIVO RESID#U00caNCIA MULTIPROFISSIONAL DE SA#U00daDE PERFIL HOSPITALAR 2024 (2).txt", r"CADERNO 57\s*\n\s*PSICOLOGIA", r"CADERNO \d+"),
         keysrc="Gabarito definitivo 2024 (pasta Gabaritos)", sus=(1, 20)),
    dict(id="pe24ab", block="pe", title="Perfil Atenção Básica · Caderno 77", year=2024, banca="UPENET/IAUPE",
         src=os.path.join(C, "ATEN#U00c7#U00c3O B#U00c1SICA PSICOLOGIA 2024.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         keyfile=("31012024 GABARITO DEFINITIVO REPUBLICADO SA#U00daDE PERFIL ATEN#U00c7#U00c3O B#U00c1SICA EDUCA#U00c7#U00c3O F#U00cdSICA e outros 2024 republicado.txt", r"CADERNO 77\s*\n\s*PSICOLOGIA", r"CADERNO \d+"),
         keysrc="Gabarito definitivo republicado 2024 (pasta Gabaritos)", sus=(1, 30)),
    dict(id="pe24sc", block="pe", title="Perfil Saúde Coletiva · Caderno 91", year=2024, banca="UPENET/IAUPE",
         src=os.path.join(C, "SA#U00daDE COLETIVA PSICOLOGIA 2024.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         keyfile=("31012024 GABARITO DEFINITIVO REUPUBLICADO SA#U00daDE COLETIVA  - CATEGORIAS PROFISSIONAIS  EDUCA#U00c7#U00c3O F#U00cdSICA e outros 2023.txt", r"CADERNO 91\s*\n\s*SAÚDE COLETIVA / PSICOLOGIA", r"CADERNO \d+"),
         keysrc="Gabarito definitivo republicado 2024 (pasta Gabaritos)", sus=(1, 30)),
    dict(id="pe23h", block="pe", title="Perfil Hospitalar · Caderno 57", year=2023, banca="UPENET/IAUPE",
         src=os.path.join(C, "57_221206_HOSPITALAR  PSICOLOGIA 2023 (1).txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         keyfile=("230119_GABARITO  DEFINITIVO RESID_MULTI SAuDE PERFIL HOSPITALAR 04 12 2023.txt", r"CADERNO 57\s*\n\s*PSICOLOGIA", r"CADERNO \d+"),
         keysrc="Gabarito definitivo 2023 (pasta Gabaritos)", sus=(1, 20)),
    dict(id="pe23ab", block="pe", title="Perfil Atenção Básica · Caderno 77", year=2023, banca="UPENET/IAUPE",
         src=os.path.join(C, "77_221207_ATENCAO BASICA PSICOLOGIA 2023.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         key=inline_key("01 D 02 B 03 A 04 C 05 E 06 D 07 B 08 E 09 C 10 A 11 C 12 C 13 D 14 B 15 E 16 E 17 A 18 C 19 C 20 E 21 B 22 NULA 23 B 24 A 25 C 26 B 27 A 28 D 29 A 30 C 31 E 32 A 33 E 34 NULA 35 B 36 C 37 E 38 D 39 B 40 D 41 D 42 A 43 B 44 C 45 A 46 D 47 B 48 B 49 C 50 E"),
         keysrc="Gabarito definitivo 2023 (upenet.com.br)", sus=(1, 30)),
    dict(id="pe23sc", block="pe", title="Perfil Saúde Coletiva · Caderno 91", year=2023, banca="UPENET/IAUPE",
         src=os.path.join(C, "91_221207_SAUDE COLETIVA PSICOLOGIA 2023.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         key=inline_key("01 A 02 D 03 D 04 A 05 A 06 B 07 D 08 NULA 09 A 10 C 11 A 12 B 13 C 14 B 15 E 16 D 17 A 18 C 19 E 20 A 21 E 22 A 23 B 24 D 25 E 26 B 27 A 28 NULA 29 E 30 B 31 E 32 A 33 E 34 NULA 35 B 36 C 37 E 38 D 39 B 40 D 41 D 42 A 43 B 44 C 45 A 46 D 47 B 48 B 49 C 50 E"),
         keysrc="Gabarito definitivo 2023 (upenet.com.br)", sus=(1, 30)),
    dict(id="pe21h", block="pe", title="Perfil Hospitalar · Caderno 55", year=2021, banca="UPENET/IAUPE",
         src=os.path.join(C, "residencia_hospitalar_psicologia(1).txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=40,
         keyfile=("gabarito_oficial(1).txt", r"CADERNO 55\s*\n\s*PSICOLOGIA", r"CADERNO \d+"),
         keysrc="Gabarito definitivo 2021 (pasta Gabaritos)", sus=(1, 10)),
    dict(id="pe21i", block="pe", title="Saúde da Família – Interiorização · Caderno 96", year=2021, banca="UPENET/IAUPE",
         src=os.path.join(C, "residencia_interiorizacao_em_saude_psicologia.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=40,
         keyfile=("gabarito_oficial(1).txt", r"CADERNO 96\s*\n\s*PSICOLOGIA", r"CADERNO \d+"),
         keysrc="Gabarito definitivo 2021 (pasta Gabaritos)", sus=(1, 20)),
    dict(id="pe17ab", block="pe", title="Perfil Atenção Básica · Caderno 73", year=2017, banca="UPENET/IAUPE",
         src=os.path.join(C, "residencia_perfil_atencao_basica_multiprofissional_psicologia.txt"), qre=SUSPE_Q, ore=SUSPE_OPT, nopt=5, n=50,
         keyfile=("gabarito_definitivo.txt", r"CADERNO 73\s*\n\s*PSICOLOGIA", r"CADERNO \d+"),
         keysrc="Gabarito definitivo (pasta Gabaritos)", sus=(1, 25)),
    # ---------------- SES-DF (IADES) ----------------
] + [
    dict(id=f"df24_{p}", block="df", title=f"Programa {p} · {name}", year=2024, banca="IADES",
         src=os.path.join(C, f), qre=IADES_Q, ore=PAREN_OPT, nopt=4, n=100,
         keyfile=("gabarito_oficial(3).txt", rf"{p} - Multiprofissional[^\n]*Psicologia", r"^\s{2,}\d{3} - Multiprofissional|Instituto Americano"),
         keysrc="Gabarito definitivo RP-1/SES-DF/2024 (pasta Gabaritos)", shared=(1, 80), program=name)
    for p, name, f in [
        (122, "Saúde da Criança", "psicologia_122_multiprofissional_em_saude_da_crianca_tipo_u.txt"),
        (130, "Saúde da Família", "psicologia_130_multiprofissional_em_saude_da_familia_tipo_u.txt"),
        (138, "Saúde do Adulto e do Idoso", "psicologia_138_multiprofissional_em_saude_do_adulto_e_do_idoso_tipo_u.txt"),
        (148, "Saúde Mental Infantojuvenil", "psicologia_148_multiprofissional_em_saude_mental_infanto_juvenil_tipo_u.txt"),
        (160, "Cuidados Paliativos", "psicologia_160_multiprofissional_em_cuidados_paliativos_tipo_u.txt"),
        (168, "Terapia Intensiva", "psicologia_168_multiprofissional_em_terapia_intensiva_tipo_u.txt"),
    ]
] + [
    # ---------------- Goiás ----------------
    dict(id="go23", block="go", title="HC/UFG · Residência Multiprofissional", year=2023, banca="UFG/CS",
         src=os.path.join(C, "psicologia.txt"), qre=IADES_Q, ore=PAREN_OPT, nopt=4, n=50,
         keyfile=("gabarito_oficial(10).txt", r"^\s*PSICOLOGIA\s*$", r"QUESTÃO ANULADA|COMISSÃO"),
         keysrc="Gabarito final COREMU/UFG (pasta Gabaritos)", sus=(1, 20)),
    dict(id="go20", block="go", title="COREMU/SES-GO · Residência Multiprofissional", year=2020, banca="UFG/CS",
         src=os.path.join(C, "residencia_medica_psicologia.txt"), qre=IADES_Q, ore=PAREN_OPT, nopt=4, n=50,
         keyfile=("gabaritos_finais.txt", r"^\s*PSICOLOGIA\s*$", r"^Questão \d+:|RESIDÊNCIA MULTIPROFISSIONAL"),
         keysrc="Gabarito oficial COREMU/SES-GO (pasta Gabaritos)", sus=(1, 15)),
    # ---------------- EBSERH ----------------
    dict(id="eb25", block="eb", title="Grupo Psicologia (Hospitalar / Organizacional / Neuro)", year=2025, banca="FGV",
         src=os.path.join(C, "psicologo_psicologia_hospitalar(2).txt"), qre=BARE_Q, ore=PAREN_OPT, nopt=5, n=60,
         keyfile=("gabarito(1).txt", r"PSICOLOGIA - PROVA TIPO 1", r"PROVA TIPO 2"),
         keysrc="Gabarito PRELIMINAR – Edital 03/2024 (pasta Gabaritos)", keep=(16, 60), susr=(16, 30)),
    dict(id="eb23h", block="eb", title="Psicólogo – Psicologia Hospitalar", year=2023, banca="IBFC",
         src=os.path.join(C, "psicologo_psicologia_hospitalar(1).txt"), qre=IBFC_Q, ore=IBFC_OPT, nopt=5, n=60,
         keyfile=("gabarito.txt", r"IBFC_177 - PSICÓLOGO", r"IBFC_\d+ -"),
         keysrc="Gabarito oficial – Concurso 01/2023, Edital 3 (pasta Gabaritos)", keep=(21, 30), keep2=(41, 60), susr=(21, 30)),
    dict(id="eb23o", block="eb", title="Psicólogo – Organizacional e do Trabalho", year=2023, banca="IBFC",
         src=os.path.join(C, "psicologo_psicologia_organizacional_e_do_trabalho.txt"), qre=IBFC_Q, ore=IBFC_OPT, nopt=5, n=60,
         keyfile=("gabarito.txt", r"IBFC_178 - PSICÓLOGO", r"IBFC_\d+ -"),
         keysrc="Gabarito oficial – Concurso 01/2023, Edital 3 (pasta Gabaritos)", keep=(21, 30), keep2=(41, 60), susr=(21, 30)),
    # ---------------- Rio de Janeiro ----------------
    dict(id="rj22", block="rj", title="Residência em Saúde Mental · Instituto Philippe Pinel", year=2022, banca="SMS-Rio",
         src=os.path.join(C, "residencia_multiprofissional_psicologo.txt"), qre=SUSPE_Q.replace(r"(\d{2})", r"(\d{1,2})"), ore=PAREN_OPT, nopt=4, n=60,
         keyfile=("gabarito(4).txt", r"CATEGORIA PROFISSIONAL - PSICÓLOGO", r"CATEGORIA PROFISSIONAL - TERAPEUTA"),
         keysrc="Gabarito oficial – D.O. Rio (pasta Gabaritos)", sus=(1, 10), start=r"^POLÍTICAS PÚBLICAS DO SUS"),
    # ---------------- Santa Catarina ----------------
    dict(id="sc_bv", block="sc", title="Barra Velha/SC · Equipe Multidisciplinar – Psicólogo", year=None, banca="Concurso municipal",
         src=os.path.join(C, "equipe_multidisciplinar_psiclogo.txt"), qre=BARE_Q, ore=SUSPE_OPT, nopt=5, n=40,
         keyfile=("gabaritos_preliminares_concurso_publico.txt", r"EQUIPE MULTIDISCIPLINAR – PSICÓLOGO", r"CARGO:"),
         keysrc="Gabarito PRELIMINAR (pasta Gabaritos)", keep=(11, 30), sus=(11, 20)),
]

BLOCKS = {
    "pe": dict(name="SES-PE · UPE/IAUPE", region="Pernambuco", desc="Residências em Área Profissional de Saúde da Secretaria Estadual de Saúde de Pernambuco (banca UPENET/IAUPE) — o processo seletivo que ela vai prestar."),
    "df": dict(name="SES-DF · IADES", region="Distrito Federal", desc="Residência Multiprofissional RP-1/SES-DF/2024. As questões 1–80 são comuns a todos os programas; 81–100 são específicas de cada programa."),
    "go": dict(name="Goiás · UFG / SES-GO", region="Goiás", desc="Residências multiprofissionais do HC/UFG e da COREMU/SES-GO (banca Centro de Seleção/UFG)."),
    "eb": dict(name="EBSERH", region="Nacional", desc="Concursos da Empresa Brasileira de Serviços Hospitalares para psicólogo (IBFC e FGV). Só entram as questões de SUS e de conhecimentos específicos."),
    "rj": dict(name="Rio de Janeiro · SMS-Rio", region="Rio de Janeiro", desc="Residência Multiprofissional em Saúde Mental do Instituto Municipal Philippe Pinel."),
    "sc": dict(name="Santa Catarina · Barra Velha", region="Santa Catarina", desc="Concurso municipal para psicólogo de equipe multidisciplinar."),
}

DROP_LINE = [re.compile(p) for p in HDR_COMMON]

FIXES = {
    "pe25ab": [
        ("A) apenas I. B) apenas I e II. C) apenas I, le IV. D) apenas II e III. E) 1, H, Ie IV.", "A) apenas I. B) apenas I e III. C) apenas I, III e IV. D) apenas II e III. E) I, II, III e IV."),
        ("IH. Hepatite A", "II. Hepatite A"), ("IH. Participação social", "II. Participação social"), ("IH. Escolaridade", "II. Escolaridade"),
        ("IV. —Intersetorialidade", "IV. Intersetorialidade"), ("IV. — fluxos de acesso", "IV. fluxos de acesso"),
        ("A) Apenas I, Il e II. B) Apenas II, Il e IV. C) Apenas II e II. D) Apenas Ie III. E) LI, He IV.", "A) Apenas I, II e III. B) Apenas II, III e IV. C) Apenas II e III. D) Apenas I e III. E) I, II, III e IV."),
        ("os cuidados sem (o) a do idoso", "______ os cuidados sem (o) a ______ do idoso"),
        ("D parece não escutar", "I) parece não escutar"), ("usar a (0) sugerida(o)", "usar a(o) ______ sugerida(o)"),
        ("HI. 'Receio", "III. Receio"), ("\n9\n", "\n"), ("D é o integrante", "I) é o integrante"),
        ("e e) a relação com", "e c) a relação com"), ("A)Iº B)3º c)4 D) 5º E) 7º", "A) 1ª B) 3ª C) 4ª D) 5ª E) 7ª"),
        ("A)8 B) 9º C) 10º D) 11º E) 12º", "A) 8ª B) 9ª C) 10ª D) 11ª E) 12ª"),
    ],
    "pe23sc": [("B) não é contemplada no campo", "C) não é contemplada no campo")],
    "pe21i": [("\n20 Sobre o Coeficiente", "\n20. Sobre o Coeficiente")],
    "pe17ab": [("D Apenas 2 itens estão corretos.", "D) Apenas 2 itens estão corretos.")],
}


def clean_lines(text):
    out = []
    for l in text.splitlines():
        s = l.strip()
        if not s:
            continue
        if any(p.search(s) for p in DROP_LINE) and not re.match(r"^\d{1,2}\s*$", s):
            continue
        # IADES layout: "(B) x" / "texto de C" / "(C)"  -> marker printed after its text
        m = re.match(r"^\(([A-E])\)$", s)
        if m and out and not re.match(r"^\(?[A-Ea-e]\)", out[-1]) and len(out) >= 2 and re.match(r"^\(?[A-Ea-e]\)", out[-2]):
            out[-1] = f"({m.group(1)}) " + out[-1]
            continue
        out.append(s)
    return out


PASSAGE = re.compile(r"(?i)^(texto|leia|consider|com base|utilize|caso cl[íi]nico|caso|observe).{0,200}quest(ões|ão|oes)\s*(?:de\s*)?(\d{1,3})(?:\s*(?:a|e|até|-)\s*(\d{1,3}))?")


def split_questions(lines, qre, bare=False, n=None):
    qs = {}
    passages = []  # (from, to, text lines)
    cur = None
    cur_pass = None
    expected = 1
    for s in lines:
        pm = PASSAGE.match(s)
        if pm and int(pm.group(3)) >= expected:
            a = int(pm.group(3)); b = int(pm.group(4) or a)
            cur_pass = [a, b, [s]]
            passages.append(cur_pass)
            cur = None
            continue
        m = re.match(qre, s)
        if m:
            num = int(m.group(1))
            if bare:
                ok = num == expected
            else:
                ok = num == expected or (num > expected and num <= expected + 2)
            if ok and (n is None or num <= n):
                cur = num
                qs[cur] = [s[m.end():]] if s[m.end():].strip() else []
                expected = num + 1
                cur_pass = None
                continue
        if cur_pass is not None and cur is None:
            cur_pass[2].append(s)
        elif cur is not None:
            qs[cur].append(s)
    return qs, passages


def split_options(body_lines, ore, nopt):
    body = "\n".join(body_lines)
    # find option markers
    ms = list(re.finditer(ore, body, re.M))
    # keep the last run A..E in order
    letters = "ABCDE"[:nopt]
    chosen = {}
    # pick earliest occurrence of 'A' after which all letters appear
    starts = [m for m in ms if m.group(1).upper() == "A"]
    for st in reversed(starts):
        after = [m for m in ms if m.start() >= st.start()]
        found = {}
        for m in after:
            L = m.group(1).upper()
            if L in letters and L not in found:
                found[L] = m
        if len(found) == nopt:
            chosen = found
            break
    if not chosen:
        return body.strip(), None
    order = sorted(chosen.values(), key=lambda m: m.start())
    stem = body[: chosen["A"].start()].strip()
    opts = {}
    for i, m in enumerate(order):
        end = order[i + 1].start() if i + 1 < len(order) else len(body)
        opts[m.group(1).upper()] = " ".join(body[m.end():end].split())
    # stray trailing text (e.g. next passage) is left on the last option; trim obvious footer junk
    return stem, [opts[L] for L in letters]


def tidy(s):
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+CONHECIMENTOS ESPEC[ÍI]FICOS\s*$", "", s)
    s = re.sub(r"(\s+\d{1,2})?\s+PERFIL SAÚDE COLETIVA – PSICOLOGIA.*$", "", s)
    s = re.sub(r"\s+(POLÍTICAS DE SAÚDE|VIGILÂNCIA À SAÚDE|EPIDEMIOLOGIA|SAÚDE MENTAL)\s*$", "", s)
    s = re.sub(r"\s+CONHECIMENTOS GERAIS.*$", "", s)
    s = re.sub(r"\s+ATENÇÃO\s+\S?\s*Abra este Caderno.*$", "", s, flags=re.S)
    s = re.sub(r"\s+-\s*SAÚDE DA FAMÍLIA - INTERIORIZAÇÃO EM SAÚDE –\s*$", "", s)
    s = re.sub(r"\s+-\s*PSICOLOGIA\s*-\s*$", "", s)
    s = re.sub(r"(?<=[.;:!?)])\s+\d{1,2}(\s+\d{1,2}\s*-\s*PSICOLOGIA\s*-\s*\d{1,2})?\s*$", "", s)
    s = re.sub(r"\s*\b\d{3} - MULTIPROFISSIONAL[^\n]*?PÁGINA \d+/\d+", "", s)
    s = re.sub(r"\s*Área livre\b", "", s)
    s = re.sub(r"\s*ATENÇÃO Aguarde a autorização.*$", "", s, flags=re.S)
    s = re.sub(r"\s*(Saúde Pública|Psicologia)?\s*COREMU-UFG/\d{4}(\s*PROCESSO SELETIVO)?", "", s)
    s = re.sub(r"\s*(PROCESSO SELETIVO\s*)?IV/UFG\b", "", s)
    s = re.sub(r"\s*conhecimentos_(comuns|específicos)_\S+", "", s)
    s = re.sub(r"\s*▬+ ?RASCUNHO ?▬+", "", s)
    s = re.sub(r"\s*TIPO BRANCA – PÁGINA \d+( Realização)?", "", s)
    s = re.sub(r"\s*GRUPO PSICOLOGIA – MANHÃ FGV CONHECIMENTO", "", s)
    s = re.sub(r"\s*LEGISLAÇÃO - (EBSERH|SUS)\s*$", "", s)
    s = re.sub(r"\s*EQUIPE MULTIDISCIPLINAR – PSICÓLOGO \(23-M\) - \d+ - CONCURSO PÚBLICO – MUNICÍPIO DE BARRA VELHA/SC", "", s)
    s = re.sub(r"(?<=[.])\s+Psicologia$", "", s)
    s = re.sub(r"-\n(?=[a-zà-ú])", "", s)          # hyphenated line breaks
    s = re.sub(r"\n(?=[a-zà-ú,;:)])", " ", s)          # soft wraps
    return s.strip()


def main():
    out = {"blocks": BLOCKS, "exams": [], "questions": []}
    seen_shared = {}
    report = []
    for ex in EXAMS:
        txt = open(ex["src"], encoding="utf-8", errors="replace").read()
        txt = txt.replace("€", "").replace("©", "").replace("|", "")
        for a, b in FIXES.get(ex["id"], []):
            if a not in txt:
                print("FIX NOT FOUND", ex["id"], a[:40])
            txt = txt.replace(a, b)
        if ex["id"] in ("go20", "rj22"):   # justified PDFs: "financiamen- to" -> "financiamento"
            KEEP = r"(?:se|me|te|lhe|lhes|lo|la|los|las|nos|vos|humorado|estar|doença)\b"
            txt = re.sub(r"([a-zà-ú])-[ \n]+(?=" + KEEP + ")", r"\1-", txt)
            txt = re.sub(r"([a-zà-ú])-[ \n]+([a-zà-ú])", r"\1\2", txt)
        if ex["id"] == "rj22":   # passage intros span several lines; drop running headers
            txt = re.sub(r"(?m)^(Processo Seletivo|Secretaria Municipal de Saúde|RESIDÊNCIA EM SAÚDE MENTAL|PSICÓLOGO|Prefeitura da Cidade do Rio de Janeiro|2021|CLÍNICA AMPLIADA|SAÚDE MENTAL NA ATENÇÃO BÁSICA|REFORMA PSIQUIÁTRICA|ESPECÍFICO DA CATEGORIA PROFISSIONAL)\s*$\n?", "", txt)
            txt = re.sub(r"(?ms)^(Considerar (?:o texto|as Referências).*?questões\s+\d+\s+(?:a|e)\s+\d+\.)",
                         lambda m: m.group(1).replace("\n", " "), txt)
        # song lyrics quoted in an exam: keep only a reference to the song
        txt = re.sub(r"“Eu não caibo mais.*?Titãs - Não vou me adaptar", "[A prova cita aqui um trecho da canção “Não vou me adaptar”, dos Titãs, sobre o envelhecimento.]", txt, flags=re.S)
        if ex["src"].endswith(".ocr.txt"):
            txt = re.sub(r"(?m)^(HI|NI|IH|Hl|IN|TI|Il)\.", "III.", txt)
            txt = re.sub(r"(?m)^(H|Il|ll|1I|I1)\.", "II.", txt)
            txt = re.sub(r"(?m)^(TV|1V|lV)\.", "IV.", txt)
        if "start" in ex:
            m = re.search(ex["start"], txt, re.M)
            txt = txt[m.start():]
        txt = re.sub(r"\s*6!\s*-\s*PSICOLOGIA\s*-\s*\d+", "", txt)
        lines = clean_lines(txt)
        if ex["qre"] != BARE_Q:
            lines = [l for l in lines if not re.fullmatch(r"\d{1,2}", l)]
        qs, passages = split_questions(lines, ex["qre"], bare=ex["qre"] == BARE_Q, n=ex["n"])
        if "key" in ex:
            key = ex["key"]
        else:
            f, a, b = ex["keyfile"]
            key = parse_key(key_section(os.path.join(G, f), a, b))
        missing = [i for i in range(1, ex["n"] + 1) if i not in qs]
        kmiss = [i for i in range(1, ex["n"] + 1) if i not in key]
        problems = []
        exq = []
        for num in range(1, ex["n"] + 1):
            if num not in qs:
                continue
            keep = True
            if "keep" in ex:
                k1 = ex["keep"]; k2 = ex.get("keep2", (0, -1))
                keep = k1[0] <= num <= k1[1] or k2[0] <= num <= k2[1]
            if not keep:
                continue
            stem, opts = split_options(qs[num], ex["ore"], ex["nopt"])
            if opts is None:
                problems.append(num)
                continue
            ctx = None
            for a, b, pl in passages:
                if a <= num <= b:
                    ctx = tidy("\n".join(pl))
            area = "psi"
            if "sus" in ex and ex["sus"][0] <= num <= ex["sus"][1]:
                area = "sus"
            if "susr" in ex and ex["susr"][0] <= num <= ex["susr"][1]:
                area = "sus"
            qid = f"{ex['id']}-{num:03d}"
            if "shared" in ex and ex["shared"][0] <= num <= ex["shared"][1]:
                qid = f"df24-{num:03d}"
                if qid in seen_shared:
                    seen_shared[qid]["programs"].append(ex["program"])
                    continue
            q = dict(id=qid, exam=ex["id"] if not qid.startswith("df24-") else "df24c", num=num, area=area,
                     stem=tidy(stem), options=[tidy(o) for o in opts], answer=key.get(num, "?") if num in key else "?",
                     context=ctx)
            if q["answer"] is None:
                q["answer"] = "NULA"
            if qid.startswith("df24-"):
                q["programs"] = [ex["program"]]
                seen_shared[qid] = q
            out["questions"].append(q)
            exq.append(num)
        exmeta = {k: ex[k] for k in ("id", "block", "title", "year", "banca", "keysrc") if k in ex}
        out["exams"].append(exmeta)
        report.append(f"{ex['id']:8s} parsed={len(qs):3d} kept={len(exq):3d} keyN={len(key):3d} missingQ={missing[:12]} keyMissing={kmiss[:8]} optProblems={problems}")
    # manual (proof-read) questions replace or fill parsed ones
    man = json.load(open(os.path.join(os.path.dirname(OUT), "manual.json")))
    byid = {q["id"]: i for i, q in enumerate(out["questions"])}
    for mq in man:
        base = dict(context=None)
        if mq["id"] in byid:
            out["questions"][byid[mq["id"]]].update(mq)
        else:
            out["questions"].append({**base, **mq})
    order = {e["id"]: i for i, e in enumerate(EXAMS)}
    out["questions"].sort(key=lambda q: (order.get(q["exam"], -1), q["num"]))
    # shared SES-DF exam meta
    out["exams"].append(dict(id="df24c", block="df", title="Questões comuns (1–80) · todos os programas de Psicologia", year=2024, banca="IADES",
                             keysrc="Gabarito definitivo RP-1/SES-DF/2024 (pasta Gabaritos)"))
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print("\n".join(report))
    print("TOTAL", len(out["questions"]))


main()
