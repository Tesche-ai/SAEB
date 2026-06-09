# SAEB — Matemática no Ensino Médio, uma década

Projeto **independente** (separado do projeto ENEM). Replica a estrutura analítica do artigo do ENEM sobre o **censo SAEB**, matemática, Ensino Médio, nas edições bienais do INEP (2013–2023).

Por que SAEB, e não só ENEM: o SAEB é **censo** (todos os concluintes, não a população autosselecionada do ENEM) e usa uma escala **equalizada entre anos**, então a comparação temporal é legítima.

## Estrutura
```
data/                          microdados (zips INEP) + parquets (GITIGNORED)
depara_descritor_t.csv         descritores D1–D35 -> habilidades T1–T10
scripts/
  build_consolidated.py        scorer por ano -> parquet por aluno
  figuras.py                   figuras do artigo
  article_style.py             estilo Economist (vendorizado)
outputs/site/                  artigo (HTML) + figures/
CLAUDE.md / PROJECT.md / DECISOES.md
.claude/skills/saeb-matriz/    referência da Matriz de Referência
```

## Como rodar (por ano)
```
# baixar
curl -L -o data/microdados_saeb_2023.zip \
  https://download.inep.gov.br/microdados/microdados_saeb_2023.zip
# consolidar e gerar figuras
python3 scripts/build_consolidated.py 2023
python3 scripts/figuras.py
```

## Status
Baseline **2023** pronto (1,53M concluintes; Alto = 5,5% = aprendizado adequado).
Multi-ano (2013–2023) em construção. Ver `PROJECT.md` e `DECISOES.md`.
