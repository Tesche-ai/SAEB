# SAEB — decisões metodológicas (tomadas de forma autônoma)

Réplica do pipeline do artigo do ENEM sobre o SAEB, matemática, Ensino Médio.
Tudo aqui é reversível e está parametrizado nos scripts em `scripts/`. Pontos
marcados com ⚠️ são escolhas que valem revisão.

## 0. Escopo de edições
- Edições usadas: **2017, 2019, 2021, 2023** (4 censos EM, mesma metodologia).
- **Excluídas 2013/2015** (era Prova Brasil, EM amostral, estrutura incompatível). 2021 estava com nome próprio no host (`microdados_saeb_2021_ensino_fundamental_e_medio.zip`).
- Schemas diferem entre anos (separador `,` em 2017 vs `;`; nomes "Prova Brasil" em 2017; código de série EM no banco de itens = 12 em 2017/2019/2021 e 3 em 2023; INSE em 2021 e 2023, ausente em 2017/2019). Absorvido pelo dicionário `SCHEMA` em `scripts/build_consolidated.py`.
- **Validação**: correlação acerto×proficiência = 0,93 (2017), 0,95 (2019), 0,95 (2021), 0,88 (2023), confirmando o escoreamento e o mapeamento de blocos em todos os schemas.
- ⚠️ Descritores `D36`/`D37` (e um `X` de item anulado) aparecem em 2017/2019 e não estão no de-para (vão para OUTRO, ~2 itens/ano fora da agregação por T; contam na taxa). Estender o de-para se quiser.

## ⚠️ Comparabilidade temporal (importante)
- A **proficiência é equalizada** entre anos -> o eixo temporal (média, % adequado, faixas) é comparável.
- A **taxa de acerto bruta e o estrato "Chute"** dependem da dificuldade da prova de cada ano -> **não comparáveis** entre anos.
- O **acerto por habilidade entre anos** é confundido pela composição de itens de cada prova (mesmo a proficiência fixa não isola, porque os itens por habilidade mudam). Por isso: dimensão temporal = proficiência equalizada; perfil de habilidade = lido **dentro de cada ano** (a forma do perfil é estável entre anos).

## 1. População e filtros
- Etapa: **Ensino Médio**, `ID_SERIE` ∈ {12 (3ª série), 13 (4ª série)}. A 4ª série
  (cursos de 4 anos) é minoria; ⚠️ pode-se restringir a 12 se quiser só 3ª série.
- Filtros: presente em matemática (`IN_PRESENCA_MT==1`), strings de resposta dos 2
  blocos com ≥13 caracteres, e proficiência não-nula.
- Resultado: **1.525.957** de 2.091.337 alunos EM (os descartados são ausentes,
  prova em branco ou sem proficiência).
- Só **matemática** (a pedido). Língua Portuguesa não foi analisada.

## 2. Escoreamento (0/1)
- Cada aluno responde **2 blocos de 13 itens = 26 itens** (desenho BIB).
- Acerto = resposta do aluno ∈ conjunto do gabarito (`TX_GABARITO`; trata "A/B" como
  conjunto). Resposta em branco/inválida = **errada, mas contada no denominador**.
- Ligação resposta→item: posição *p* do bloco *b* na string ⟷ `TS_ITEM`
  (ID_SERIE=3, MT, NU_BLOCO=*b*, NU_POSICAO=*p*). 91 itens, 7 blocos, 0 sem match.

## 3. Habilidades (descritor → T1–T10)
- Mapa em `saeb/depara_descritor_t.csv`. O SAEB rotula **um descritor por item**
  (single-loading), então não há os pesos fracionários/entrelaçamento do ENEM.
- ⚠️ Decisões de classificação: geometria analítica (D7–D10) → **GEO**; PA/PG (D22)
  → **FN**; sistemas/matrizes (D31) → **EXP**; contagem/combinatória (D32) → **EST**;
  itens-âncora de 9º ano (`9N*`,`9A*`) mapeados por prefixo (N→NR, A→FN).
- **NQ (frações) não tem descritor no EM** → 9 habilidades efetivas (sem NQ).

## 4. Estratos
- **Chute**: taxa de acerto < 0,20 (acaso em itens de 5 alternativas).
- **Baixo**: proficiência < 275 · **Médio**: 275–350 · **Alto**: ≥ 350.
- ⚠️ O corte **350 = "aprendizado adequado"** do EM (anchor de política; rende ~5,5%,
  consistente com a estatística pública e com p95≈347 do dado). O corte **275** é um
  piso "básico" arredondado; pode ser refinado pelos níveis oficiais da escala
  (PDF na pasta "Escalas de Proficiência" do zip, não parseado por falta de
  `pdftotext` na máquina). Resultado: Chute 21,8% · Baixo 36,6% · Médio 36,1% · Alto 5,5%.

## 5. Métrica de habilidade (agregada)
- Por grupo (estrato/percentil/escola/socio) × habilidade: **taxa de acerto** =
  Σ acertos / Σ itens vistos do grupo. Não há vetor por aluno (esparsidade do BIB),
  só agregado, que é o que todos os artefatos do artigo usam.
- **Não-ponderado** (censo; `peso`/`PESO_ALUNO_MT` disponível, ~1, irrelevante em
  2023). ⚠️ Para anos amostrais (2013/2015), aplicar peso.
- Usada a proficiência pontual `PROFICIENCIA_MT_SAEB`, não os plausible values
  (suficiente para estratos descritivos).

## 6. Escolas (seis segmentos)
- Agregação por `ID_ESCOLA`, **N ≥ 10** alunos. Bandas de média (275/350) ×
  dispersão interna: **Coesa** se DP < mediana das escolas (=41), senão **Mista**.
  Baixa e Alta colapsam a dispersão (como no ENEM). 19.811 escolas; 67% Baixa,
  0,9% Alta.

## 7. Sala de aula
- Turmas reais (`ID_TURMA`); composição por estrato, média por segmento de escola.

## 8. Não reproduzido (vs ENEM), e por quê
- **Vetor de habilidade por aluno / Naive Bayes**: inviável pelo BIB (26 de 91 itens
  por aluno). Substituído por agregado direto.
- **Q-Matrix multi-loading / entrelaçamento**: SAEB é single-descritor por item.
- **Série temporal**: só 2023 nesta v1. Próximo: 2017/2019/2021 (+amostral 2013/2015).

## 9. Pendências / a revisar
- ⚠️ Refinar cortes de estrato pelos níveis oficiais da escala SAEB.
- ⚠️ Revisar o de-para nos casos de fronteira (geom. analítica, PA/PG, sistemas).
- Legenda do dotplot (fig2) encosta na última linha; ajuste cosmético.
- Frente separada: **confiabilidade/anomalia** (mesmo scorer, + Censo Escolar para fluxo).
