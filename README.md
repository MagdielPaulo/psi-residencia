# Psi Residência

Quiz de estudo para provas de **residência multiprofissional em Psicologia**, feito para funcionar offline, no navegador, em celular, tablet e computador.

## Como usar

**Online:** https://magdielpaulo.github.io/psi-residencia/ (abre no celular, tablet ou computador).

**Offline:** abra o `index.html` no navegador (Chrome, Edge ou Firefox). Não precisa de servidor nem de internet. As pastas `dados`, `img` e `fontes` precisam ficar junto do `index.html`.

O progresso fica salvo no próprio navegador (`localStorage`). Em **Ajustes › Cópia de segurança** dá para baixar e importar um `.json` com tudo.

## O que tem

- **1.015 questões** em 6 blocos, todas com gabarito oficial, dica, explicação e fonte:

  | Bloco | Questões |
  |---|---|
  | SES-PE (UPE/IAUPE, 2017–2025) | 530 |
  | SES-DF (IADES, 2024) | 200 |
  | Goiás (UFG / SES-GO) | 100 |
  | EBSERH (FGV 2025, IBFC 2023) | 105 |
  | Rio de Janeiro (SMS-Rio / Pinel) | 60 |
  | Santa Catarina (Barra Velha) | 20 |

- Modos estudo e simulado cronometrado, treino misto, por tema e por assunto.
- **Explicações em partes:** ponto-chave, análise, por que não as outras, aviso de comando invertido (INCORRETA/EXCETO), palavras-chave e fundamento.
- **Caderno de erros** com o motivo do erro e **revisão espaçada** (1, 3, 7, 16 e 35 dias).
- **Resumos:**
  - mapas mentais de 15 temas;
  - flashcards com revisão espaçada (126 prontos, mais os das questões erradas e os cards próprios);
  - ranking do que mais cai.
- Anotações, favoritas, XP, níveis, conquistas e sequência de dias.
- **Ajustes e acessibilidade:**
  - temas claro, sépia e escuro, e alto contraste;
  - fontes Inter, Atkinson Hyperlegible e Literata;
  - tamanho do texto, espaçamento e largura da coluna;
  - reduzir animações, modo foco e atalhos de teclado;
  - apagar dados com opção de desfazer.

## Estrutura

```
index.html            app completo (HTML + CSS + JS, sem dependências)
dados/questoes.js     banco de questões (window.PSI_QUESTOES)
dados/explicacoes.js  dicas e explicações (window.PSI_EXPLICACOES)
dados/resumos.js      mapas mentais, flashcards e termos do ranking
img/                  figuras recortadas das provas
fontes/               fontes woff2 (SIL Open Font License) + licenças
ferramentas/          scripts que geraram os dados a partir dos PDFs
  parse.py            extrai questões e gabaritos dos textos das provas
  make_data.py        junta questões + explicações e gera dados/*.js
  figures.py          recorta as figuras das provas
  extract.py          texto dos PDFs com leitura em colunas
  manual.json         correções revisadas à mão
  explicacoes/*.json  explicações por caderno (fonte das explicações)
```

## Avisos sobre os gabaritos

- **EBSERH 2025 (FGV) e Barra Velha/SC:** o gabarito usado é o **preliminar**.
- **SES-PE 2025 e SES-PE 2023 (Atenção Básica e Saúde Coletiva):** gabaritos definitivos do site da UPE.
- **EBSERH HU-UNIFAP 2022:** ficou de fora por falta de gabarito.
- **Gabaritos discutíveis ou provas com erro de impressão:** aparecem marcados na explicação de cada questão.

## Uso

Projeto de estudo pessoal, sem fins comerciais. As questões, gabaritos e figuras pertencem às respectivas bancas organizadoras.
