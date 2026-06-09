# A matemática que falta, agora no censo: SAEB 2023, Ensino Médio

> **Rascunho automático (v1).** Réplica do pipeline do artigo do ENEM aplicada ao SAEB 2023, matemática, 3ª/4ª série do Ensino Médio. Gerado de ponta a ponta a partir dos microdados do INEP. As decisões metodológicas tomadas de forma autônoma estão em [`DECISOES.md`](DECISOES.md). Separado do artigo do ENEM, para integração posterior.

O artigo do ENEM olhou a população que **se inscreve** para o vestibular: um corte já filtrado, e mesmo assim com déficit grande em matemática. Ficou a hipótese de que, para o resto da geração, o quadro seria pior. O SAEB responde isso de frente: ele é **censo**, aplicado a praticamente todos os concluintes do Ensino Médio. Aqui são **1.525.957 estudantes** de 2023 com prova de matemática válida.

A vantagem do SAEB sobre o ENEM para esta pergunta é dupla. A escala é **equalizada** (comparável entre anos por construção, sem a ressalva de calibração do ENEM), e cada item já vem rotulado com a **habilidade que mede** (o descritor da Matriz de Referência), então o eixo de habilidades sai do dado oficial, sem classificação manual nossa.

---

## Capítulo 1 — O nível: poucos chegam ao aprendizado adequado

A nota média de matemática do EM em 2023 é **262** na escala SAEB. Mais revelador que a média é a divisão da população por desempenho:

![Distribuição](outputs/figures/fig1_distribuicao.png)

- **Chute (22%)**: acerta a prova no nível do acaso (taxa de acerto abaixo de 0,20, o esperado chutando itens de 5 alternativas). Um em cada cinco concluintes do EM não distingue de zero o que sabe de matemática.
- **Baixo (37%)**: abaixo da proficiência 275.
- **Médio (36%)**: entre 275 e 350.
- **Alto (5,5%)**: proficiência ≥ 350, o limiar de **aprendizado adequado** definido para o EM. Só **um em cada dezoito** concluintes chega lá.

O número de 5,5% reproduz, no microdado bruto, a estatística que circula no debate público (os "~5% com aprendizado adequado em matemática"), e que tínhamos citado de segunda mão no artigo do ENEM. Aqui ela é recalculada do zero.

---

## Capítulo 2 — O que cada grupo realmente sabe, por habilidade

Escoreando as respostas item a item e agrupando cada item na sua habilidade, dá para ver **o que** cada estrato domina, não só quanto.

![Domínio por habilidade e estrato](outputs/figures/fig2_dominio_estrato.png)

A leitura é dura e tem a mesma assinatura do ENEM:

- **Leitura de Dados é a única habilidade com cobertura razoável** (56% de acerto na população). Ler um gráfico ou uma tabela é o que mais gente consegue fazer.
- **Todas as outras oito habilidades ficam abaixo de 40%** na população: Porcentagem 38%, Equações 34%, Números reais 33%, Geometria 31%, Funções 30%, Proporcionalidade 26%, Medida 24%, Estatística/probabilidade 21%.
- **Fora do estrato Alto, quase nada passa de 50%.** No estrato Médio, só Leitura de Dados (75%) e Porcentagem (55%) cruzam a metade. No Baixo, só Leitura de Dados (50%). No Chute, nenhuma habilidade chega a 30%.
- **Mesmo o estrato Alto tem buracos.** O topo acerta Leitura de Dados em 92%, mas Estatística/probabilidade em 45% e Medida em 58%. Os 5,5% que atingem o "adequado" ainda têm fragilidades específicas.

Em escala de país: cada uma dessas habilidades abaixo de 40% representa, na faixa de 1,5 milhão de concluintes avaliados, mais de **900 mil jovens** que terminam o EM sem acertar nem metade dos itens daquela habilidade.

---

## Capítulo 3 — O que diferencia um degrau do outro

Comparar estratos consecutivos mostra **qual habilidade** separa um grupo do seguinte.

![Transições](outputs/figures/fig3_transicoes.png)

- **Chute → Baixo:** o que mais avança é **Leitura de Dados (+22 pp)**. Sair do acaso é, antes de tudo, conseguir ler informação apresentada em gráfico ou tabela.
- **Baixo → Médio:** o motor é **Porcentagem (+25 pp)**, com a aritmética aplicada ganhando tração.
- **Médio → Alto:** o salto é **largo e geral** (+28 pp em média por habilidade, liderado por Proporcionalidade, +38 pp). Chegar ao aprendizado adequado não depende de uma habilidade, depende de fluência em quase todas ao mesmo tempo.

A mesma ordem aparece na emergência contínua por percentil de proficiência:

![Emergência por percentil](outputs/figures/fig4_emergencia.png)

Leitura de Dados "acorda" cedo e dispara; as demais só decolam no terço superior da distribuição, e várias (Medida, Estatística) ficam baixas até o topo.

---

## Capítulo 4 — As escolas e a sala de aula

O SAEB é censitário e já vem com escola e turma identificadas, então o mapa de escolas é nativo (no ENEM isso só foi possível em 2024).

![Escolas em seis segmentos](outputs/figures/fig5_escolas.png)

Das **19.811 escolas** com ao menos 10 alunos avaliados, **67% caem no segmento Baixa** (média < 275) e apenas **179 escolas (0,9%) são Alta** (média ≥ 350). O sistema, visto escola por escola, é majoritariamente de baixo desempenho.

Traduzindo para a sala de aula real (usando as turmas do próprio dado):

![Sala de aula por segmento](outputs/figures/fig6_sala.png)

A turma típica de uma escola Baixa é dominada por alunos no Chute e no Baixo. Mesmo nas escolas do segmento Alta, a turma é heterogênea, com presença relevante do Médio. O professor enfrenta, na mesma sala, níveis de partida muito distintos.

---

## Capítulo 5 — O gradiente socioeconômico

O SAEB traz o INSE (indicador de nível socioeconômico) pronto por aluno. Dividindo a população em quintos:

![Proficiência por quinto socioeconômico](outputs/figures/fig7_socio.png)

- O quinto mais pobre tem proficiência média **257** e só **2,7%** no nível adequado.
- O quinto mais rico tem **282** e **10,4%** no adequado.

O gradiente é claro (o aluno mais rico tem quase quatro vezes mais chance de atingir o adequado), e ao mesmo tempo modesto em termos absolutos: **mesmo no topo socioeconômico, 9 em cada 10 concluintes não atingem o aprendizado adequado em matemática.** O déficit é geral, não um problema só dos mais pobres.

---

## Síntese

No censo, a hipótese que ficou aberta no ENEM se confirma e piora: a maioria dos concluintes do Ensino Médio termina sem domínio sólido de matemática, **um em cada cinco no nível do acaso**, e só **5,5% no aprendizado adequado**. A única habilidade com alguma cobertura é leitura de dados; abstração (proporção, medida, estatística) fica para trás em toda a distribuição. O gradiente socioeconômico existe, mas o piso é baixo para todos.

Próximos passos previstos: incluir as demais edições (2017, 2019, 2021; amostral 2013/2015) para a série temporal equalizada e o drift de habilidade; e a frente separada de **confiabilidade do dado** (detecção de anomalia / manipulação), que usa o mesmo scorer.

---

*Fontes: Microdados SAEB 2023 (INEP). Pipeline em `saeb/scripts/`. Decisões metodológicas em `saeb/DECISOES.md`.*
