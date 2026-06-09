# PROJECT.md

## O que é
Projeto independente sobre **matemática no SAEB, Ensino Médio, ~10 anos**. Replica os 5 eixos do artigo do ENEM sobre o censo SAEB, numa escala equalizada entre anos. Saída: artigo (site) independente.

## Edições (bienais, EM matemática)
| Ano | Tipo EM | Status |
|---|---|---|
| 2013 / 2015 | amostral (Prova Brasil) | **fora** (estrutura incompatível) |
| 2017 | censo | **consolidado** (N=1.456.325, corr taxa×prof 0,93) |
| 2019 | censo | **consolidado** (N=1.514.938, corr 0,95) |
| 2021 | censo | **consolidado** (N=1.399.839, corr 0,95) |
| 2023 | censo | **consolidado** (N=1.525.957, corr 0,88) |

URL: `https://download.inep.gov.br/microdados/microdados_saeb_YYYY.zip`.

## Pipeline (espelha o ENEM)
1. **Scorer** (`scripts/build_consolidated.py`): liga resposta item-a-item ao banco de itens (gabarito + descritor + parâmetros TRI), escoreia 0/1, mapeia descritor → T1–T10, estratifica, salva `data/consolidated_saeb_YYYY_em.parquet` por aluno.
2. **Figuras** (`scripts/figuras.py`): distribuição, domínio por habilidade × estrato, transições, emergência por percentil, escolas (6 segmentos), sala de aula, socio (INSE).
3. **Artigo** em `outputs/site/`.

## Onde estamos
- **4 censos consolidados (2017, 2019, 2021, 2023)**, scorer generalizado por schema, validado (corr 0,88–0,95).
- **Evolução (proficiência equalizada)**: média 266 → 273 → 267 → 268; adequado (≥350) 6,6% → 7,4% → 5,2% → **5,5%**. Pico em 2019, fundo da pandemia em 2021, sem recuperação real. Estagnação na década.
- **Cross-section 2023**: Leitura de Dados única habilidade >40%; fora do Alto quase nada passa de 50%; 67% das escolas no segmento Baixa; gradiente socio presente, piso baixo para todos.
- **Artigo v1** em `outputs/site/index.html` (5 capítulos, dimensão temporal no Cap 1). 9 figuras.

## A seguir
2. Estender o de-para para **D36/D37**.
3. Refinar cortes de estrato pelos níveis oficiais da escala.
4. Frente paralela: **confiabilidade do dado** (detecção de anomalia), mesmo scorer + Censo Escolar.
5. Polir o site (interatividade estilo ENEM, se desejado).

## Frente paralela (futura)
**Confiabilidade do dado** (detecção de anomalia/manipulação, IDEB): mesmo scorer + Censo Escolar para fluxo. Ver discussão no histórico.

## Restrições
- Sem vetor de habilidade por aluno (BIB). Tudo agregado.
- Single-loading (um descritor por item); sem entrelaçamento.
- Edições antigas amostrais (peso amostral relevante; 2023 é censo, peso ~1).
