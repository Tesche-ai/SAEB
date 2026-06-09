# CLAUDE.md

Projeto **independente** (separado do projeto ENEM). Análise do desempenho em **matemática no SAEB**, Ensino Médio (3ª/4ª série), ao longo de ~10 anos (edições bienais do INEP). Replica a estrutura analítica do artigo do ENEM, agora sobre o **censo** (todos os concluintes, não a população autosselecionada do ENEM) e numa escala **equalizada entre anos**.

Para estado atual e próximos passos, ver `PROJECT.md`. Decisões metodológicas autônomas em `DECISOES.md`.

## Idioma de trabalho
Português em tudo: respostas, comentários de código, nomes de arquivos, documentação.

## O núcleo metodológico (o que o SAEB permite, e o que não)

- **Censo, escala equalizada.** A proficiência SAEB (`PROFICIENCIA_MT_SAEB`) é comparável entre anos por construção. Comparação temporal é legítima (diferente do ENEM, que exigia within-regime).
- **Habilidades = descritores oficiais.** Cada item do SAEB já vem rotulado com **um** descritor da Matriz de Referência (`NU_DESCRITOR_HABILIDADE` em `TS_ITEM`). Mapeamos descritor → T1–T10 (as 10 habilidades do ENEM) via `depara_descritor_t.csv`. Single-loading (um descritor por item), sem o entrelaçamento multi-habilidade do ENEM.
- **Desenho BIB.** Cada aluno responde só ~26 de ~91 itens de matemática. Por isso **não há vetor de habilidade por aluno** (esparsidade). Toda análise de habilidade é **agregada** (por estrato/percentil/escola/socio), estimada direto pela taxa de acerto do grupo. Isso é o que todos os artefatos do artigo usam.
- **Estratos.** Chute (taxa de acerto < 0,20, acaso em 5 alternativas) + Baixo/Médio/Alto por cortes na proficiência (Alto ≥ 350 = aprendizado adequado). Ver `DECISOES.md`.
- **Frente futura: confiabilidade do dado.** O SAEB é aplicado na escola, com incentivo do IDEB, e há relatos de manipulação. O mesmo scorer (respostas item-a-item) alimenta detecção de anomalia (estilo Jacob-Levitt: erra-fácil/acerta-difícil, achatamento dificuldade↔acerto por turma/escola).

## Estrutura
```
data/                              microdados brutos (zips INEP) + parquets (GITIGNORED)
  microdados_saeb_YYYY.zip
  consolidated_saeb_YYYY_em.parquet
depara_descritor_t.csv             D1–D35 (+âncoras) -> T1–T10
scripts/
  build_consolidated.py            scorer por ano: respostas -> 0/1 -> habilidade -> parquet
  figuras.py                       figuras do artigo
outputs/site/                      o artigo (HTML) + figures/
DECISOES.md                        decisões metodológicas autônomas
.claude/skills/saeb-matriz/        referência da Matriz de Referência (descritores)
```

## Princípios não-negociáveis
- **Simplicidade defensável > sofisticação.** Métrica de habilidade = taxa de acerto agregada por grupo. Nada de instrumento por aluno (o BIB não sustenta).
- **Ancorar cortes em referência institucional** (≥350 = adequado), não em quantis ad hoc, sempre que possível.
- **Verificar a matemática do pipeline end-to-end** antes de propor refatorações.
- Edições com estrutura diferente (2013/2015, era Prova Brasil; EM amostral) podem não suportar todos os artefatos. Documentar por ano o que dá e o que não dá.

## Estilo de comunicação
- Direto, criticamente engajado. Sem flattery, sem hedging, sem preâmbulos.
- **Não usar "Não é X, é Y"** (cacoete de LLM). Afirmação direta.
- **Evitar travessões (—).** Vírgula, ponto, parênteses ou dois-pontos.
- **Não começar frase com "E" ou "Mas".** Juntar à anterior com vírgula ou reescrever.
- Discordar e apontar erros assim que identificados.
