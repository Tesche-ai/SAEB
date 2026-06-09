# PROJECT.md

## O que é
Projeto independente sobre **matemática no SAEB, Ensino Médio, ~10 anos**. Replica os 5 eixos do artigo do ENEM sobre o censo SAEB, numa escala equalizada entre anos. Saída: artigo (site) independente.

## Edições (bienais, EM matemática)
| Ano | Tipo EM | Microdado | Status |
|---|---|---|---|
| 2013 | amostral | baixando | a inspecionar (era Prova Brasil; estrutura pode diferir) |
| 2015 | amostral | baixando | a inspecionar |
| 2017 | censo | baixando | a inspecionar |
| 2019 | censo | baixando | a inspecionar |
| 2021 | censo | **não achado** no host padrão | resolver URL |
| 2023 | censo | OK | **consolidado (baseline)** |

URLs: `https://download.inep.gov.br/microdados/microdados_saeb_YYYY.zip` (2013/2015/2017/2019/2023 confirmadas; 2021 pendente).

## Pipeline (espelha o ENEM)
1. **Scorer** (`scripts/build_consolidated.py`): liga resposta item-a-item ao banco de itens (gabarito + descritor + parâmetros TRI), escoreia 0/1, mapeia descritor → T1–T10, estratifica, salva `data/consolidated_saeb_YYYY_em.parquet` por aluno.
2. **Figuras** (`scripts/figuras.py`): distribuição, domínio por habilidade × estrato, transições, emergência por percentil, escolas (6 segmentos), sala de aula, socio (INSE).
3. **Artigo** em `outputs/site/`.

## Onde estamos
- **2023 consolidado** (1.525.957 concluintes): Chute 22% · Baixo 37% · Médio 36% · **Alto 5,5%** (≥350 adequado). Leitura de Dados é a única habilidade >40%; fora do Alto quase nada passa de 50%; 67% das escolas no segmento Baixa.
- Baseline migrado do trabalho feito no repo ENEM (subpasta `saeb/`, agora aposentada).

## A seguir
1. Baixar e **inspecionar o schema de cada edição** (2013/2015 da era Prova Brasil podem ter estrutura bem diferente; descritor-por-item e respostas-por-bloco podem variar).
2. **Generalizar o scorer** com adaptadores por ano; consolidar 2017/2019 (censo, próximos de 2023) e, se a estrutura permitir, 2013/2015.
3. Resolver a URL do **2021**.
4. **Análises multi-ano**: evolução da proficiência e da distribuição; drift de habilidade na escala equalizada; transições e escolas ao longo do tempo.
5. **Artigo multi-capítulo** (site) com a dimensão temporal no centro.

## Frente paralela (futura)
**Confiabilidade do dado** (detecção de anomalia/manipulação, IDEB): mesmo scorer + Censo Escolar para fluxo. Ver discussão no histórico.

## Restrições
- Sem vetor de habilidade por aluno (BIB). Tudo agregado.
- Single-loading (um descritor por item); sem entrelaçamento.
- Edições antigas amostrais (peso amostral relevante; 2023 é censo, peso ~1).
