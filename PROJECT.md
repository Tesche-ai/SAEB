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
- **Ensino Fundamental (2023)** consolidado: 5º e 9º ano (`build_ef.py` → `consolidated_saeb_2023_{5ef,9ef}.parquet`), habilidade no nível de **área** (4 temas), não as 10 finas do EM. Funil: **44% (5º) → 17% (9º) → 5,5% (EM)** adequado. Tema: 5º lidera Trat.Info (74%), Grandezas/Medidas mais fraco (43%); 9º comprime tudo em 44–54% quando entra a álgebra.
- **Confiabilidade/anomalia (2023, EM+9EF+5EF)** explorada (`anomalia.py`, `figuras_ef.py`): sinais grosseiros limpos (achatamento, strings idênticas); achado central = **turmas quase-perfeitas concentradas nas escolas pobres do 9º ano (56% no Q1 de INSE vs 20% base)**, bandeira vermelha consistente com manipulação induzida pelo IDEB.
- **Site multi-página** em `outputs/site/`: `index.html` (EM, 5 caps), `ef.html` (EF, funil + áreas), `confiabilidade.html` (anomalia). CSS compartilhado `style.css` + nav. 14 figuras.

## A seguir
2. Estender o de-para EM para **D36/D37**; refinar fronteiras de tema do EF nos casos de borda.
3. Refinar cortes de estrato pelos níveis oficiais da escala.
4. **Anomalia**: corrigir o painel #6 (junção de ID de escola entre anos falhou → 0 escolas); rodar série temporal dos testes; cruzar com Censo Escolar para fluxo.
5. Investigar caso a caso as turmas quase-perfeitas em escolas pobres do 9º ano (lista de `ID_TURMA`).
6. Polir o site (interatividade estilo ENEM, se desejado).

## Restrições
- Sem vetor de habilidade por aluno (BIB). Tudo agregado.
- Single-loading (um descritor por item); sem entrelaçamento.
- Edições antigas amostrais (peso amostral relevante; 2023 é censo, peso ~1).
