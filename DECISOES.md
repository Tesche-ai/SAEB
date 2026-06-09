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

## 10. Ensino Fundamental (5º e 9º ano, 2023)
- `scripts/build_ef.py`. Habilidade no nível de **área** (4 temas da Matriz: ESP,
  GM, NUM, TI), não os 10 descritores finos do EM, porque os descritores do EF
  seguem matriz própria (5º: D1–D28; 9º: D1–D37) organizada por área.
- Fronteiras de tema (padrão da matriz): 5º — ESP D1-5, GM D6-12, NUM D13-26,
  TI D27-28; 9º — ESP D1-12, GM D13-18, NUM D19-35, TI D36-37. Códigos-âncora
  por letra (E→ESP, G/M→GM, N/A→NUM).
- Adequado: prof ≥ **225** (5º), ≥ **300** (9º), na escala equalizada.
- NPOS detectado dinamicamente (max NU_POSICAO): 5º=11 itens/bloco, 9º=13.
- **Funil**: 44,3% (5º) → 17,3% (9º) → 5,5% (EM) adequado. Corr taxa×prof > 0,9.

## 11. Confiabilidade / detecção de anomalia (exploratório)
- `scripts/anomalia.py` (ciente de etapa), `figuras_ef.py` (teste 4×INSE).
- Testes: #1 achatamento dificuldade↔acerto (escola); #2 aberrância (turma);
  #4 excesso de turmas quase-perfeitas (≥90% acerto); #5 strings idênticas;
  #4×INSE distribuição das turmas suspeitas pelos quintos de INSE da escola.
- **Limpos**: #1 (gap sempre positivo, 0,30–0,40) e #5 (zero grupos com ≥3
  strings idênticas; BIB espirala cadernos e neutraliza cópia literal).
- **Achado**: turmas com >30% quase-perfeitos concentram-se nas escolas pobres
  no 9º ano (Q1=56% vs base 20%; Q5=18%). 5º bimodal (Q1=33%, Q5=40%). EM quase
  sem turmas quase-perfeitas (24 no país). Gradiente acompanha o incentivo do
  IDEB (forte nos anos finais do EF municipal). **Não prova fraude**; sinaliza.
- **Geografia** (UF do 1% mais suspeito EM): removida do site por ser anedótica.
- ⚠️ Painel #6 (salto-e-reversão entre edições) retornou 0 escolas: junção de
  ID de escola entre anos falhou. Pendente.

## 12. Site multi-página
- `outputs/site/`: `index.html` (EM), `ef.html` (EF), `confiabilidade.html`
  (anomalia). CSS extraído para `style.css` compartilhado + nav sticky 3-links.
- Variante `.flag` do `.punch` (borda laranja) para bandeiras vermelhas de fraude.
