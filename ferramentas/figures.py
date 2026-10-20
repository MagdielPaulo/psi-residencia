"""Find questions that reference a figure and crop the figure region from the source PDF.

Writes site/img/<qid>.png and build/figs.json ({qid: "img/<qid>.png"}).
usage: python3 -I figures.py
"""
import json, os, re, pymupdf

B = "/home/claude/build"
PROVAS = "/home/claude/raw/zip/root/Provas"
SRC = {  # exam id -> pdf file (text-based PDFs only)
    "pe24h": "HOSPITALAR PSICOLOGIA 2024 (2).pdf", "pe24ab": "ATEN#U00c7#U00c3O B#U00c1SICA PSICOLOGIA 2024.pdf",
    "pe24sc": "SA#U00daDE COLETIVA PSICOLOGIA 2024.pdf", "pe23h": "57_221206_HOSPITALAR  PSICOLOGIA 2023 (1).pdf",
    "pe23ab": "77_221207_ATENCAO BASICA PSICOLOGIA 2023.pdf", "pe23sc": "91_221207_SAUDE COLETIVA PSICOLOGIA 2023.pdf",
    "pe21h": "residencia_hospitalar_psicologia(1).pdf", "pe21i": "residencia_interiorizacao_em_saude_psicologia.pdf",
    "pe17ab": "residencia_perfil_atencao_basica_multiprofissional_psicologia.pdf",
    "go23": "psicologia.pdf", "go20": "residencia_medica_psicologia.pdf",
    "eb25": "psicologo_psicologia_hospitalar(2).pdf", "eb23h": "psicologo_psicologia_hospitalar(1).pdf",
    "eb23o": "psicologo_psicologia_organizacional_e_do_trabalho.pdf", "rj22": "residencia_multiprofissional_psicologo.pdf",
    "sc_bv": "equipe_multidisciplinar_psiclogo.pdf",
}
for p, f in [(122, "psicologia_122_multiprofissional_em_saude_da_crianca_tipo_u.pdf"), (130, "psicologia_130_multiprofissional_em_saude_da_familia_tipo_u.pdf"),
             (138, "psicologia_138_multiprofissional_em_saude_do_adulto_e_do_idoso_tipo_u.pdf"), (148, "psicologia_148_multiprofissional_em_saude_mental_infanto_juvenil_tipo_u.pdf"),
             (160, "psicologia_160_multiprofissional_em_cuidados_paliativos_tipo_u.pdf"), (168, "psicologia_168_multiprofissional_em_terapia_intensiva_tipo_u.pdf")]:
    SRC[f"df24_{p}"] = f

FIG = re.compile(r"(?i)(observe|analise|veja|considere|conforme)\s+(a|o)\s+(imagem|figura|quadro|tabela|gráfico|charge|tirinha|ilustração|cartaz)|(imagem|figura|gráfico|charge|tirinha) (abaixo|a seguir|acima)|Fonte:|gravura|recortes de um filme|imagem que segue|observe a imagem")

d = json.load(open(f"{B}/questions.json"))
out = {}
os.makedirs("/home/claude/site/img", exist_ok=True)
docs = {}
for q in d["questions"]:
    ex = q["exam"]
    if ex == "df24c":
        ex = "df24_122"
    if ex not in SRC or not FIG.search(q["stem"]):
        continue
    doc = docs.get(ex) or docs.setdefault(ex, pymupdf.open(os.path.join(PROVAS, SRC[ex])))
    w = q["stem"].split()
    n = q["num"]
    probes = [f"{n:02d}. {w[0]} {w[1]}", f"{n}. {w[0]} {w[1]}", f"{n}) {w[0]} {w[1]}", f"QUESTÃO {n}", " ".join(w[:7]), " ".join(w[:4])]
    hit = None
    for probe in probes:
        for pno, page in enumerate(doc):
            r = page.search_for(probe)
            if r:
                hit = (pno, r[0])
                break
        if hit:
            break
    if not hit:
        print("NOT FOUND", q["id"], probe)
        continue
    pno, rect = hit
    page = doc[pno]
    # candidate figure rects: raster images and vector drawings below the stem start
    cands = []
    for img in page.get_images(full=True):
        for bb in page.get_image_rects(img[0]):
            if bb.y1 > rect.y0 and bb.width > 40 and bb.height > 30:
                cands.append(bb)
    if not cands:
        print("NO IMAGE", q["id"])
        continue
    # nearest image below the question start
    cands.sort(key=lambda b: (b.y0 < rect.y0 - 5, b.y0))
    bb = cands[0]
    # crop the figure plus its "Fonte:" caption if directly below
    clip = pymupdf.Rect(bb.x0 - 4, bb.y0 - 4, bb.x1 + 4, bb.y1 + 4)
    pix = page.get_pixmap(clip=clip, dpi=170)
    path = f"img/{q['id']}.png"
    pix.save(f"/home/claude/site/{path}")
    out[q["id"]] = path
    print("OK", q["id"], f"p{pno+1}", [round(x) for x in bb])
json.dump(out, open(f"{B}/figs.json", "w"), indent=0)
print(len(out), "figures")
