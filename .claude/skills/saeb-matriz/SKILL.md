---
name: saeb-matriz
description: Referência da Matriz de Referência de Matemática do SAEB (Ensino Médio) e o de-para descritor -> T1-T10 usado neste projeto. Use ao classificar itens, interpretar habilidades ou ajustar o mapeamento.
---

# Matriz de Referência — Matemática, 3ª série EM (SAEB)

Cada item do SAEB mede **um** descritor (single-loading). 35 descritores em 4 temas.
Mapeamento para as 10 habilidades do ENEM (T1–T10) em `depara_descritor_t.csv`.

## I. Espaço e Forma  (-> GEO)
- D1 Identificar figuras semelhantes por relações de proporcionalidade
- D2 Relações métricas do triângulo retângulo em figuras planas/espaciais
- D3 Relacionar poliedros/corpos redondos com planificações ou vistas
- D4 Relação entre vértices, faces e arestas de poliedros
- D5 Razões trigonométricas no triângulo retângulo (sen, cos, tg)
- D6 Localização de pontos no plano cartesiano
- D7 Interpretar geometricamente os coeficientes da equação de uma reta
- D8 Equação de uma reta a partir de pontos/inclinação
- D9 Interseção de retas como sistema de equações
- D10 Reconhecer equações que representam circunferências

## II. Grandezas e Medidas  (-> MED)
- D11 Perímetro de figuras planas
- D12 Área de figuras planas
- D13 Área total e/ou volume de sólidos

## III. Números e Operações / Álgebra e Funções  (-> NR, PCT, PROP, EXP, FN, EST)
- D14 Localização de números reais na reta numérica  (NR)
- D15 Variação proporcional direta/inversa entre grandezas  (PROP)
- D16 Problema com porcentagem  (PCT)
- D17 Equação do 2º grau  (EXP)
- D18 Expressão algébrica de função a partir de tabela  (FN)
- D19 Função do 1º grau  (FN)
- D20 Crescimento/zeros de funções em gráficos  (FN)
- D21 Gráfico que representa situação descrita em texto  (FN)
- D22 Progressões aritméticas/geométricas (termo geral)  (FN)
- D23 Gráfico de função polinomial do 1º grau pelos coeficientes  (FN)
- D24 Representação algébrica de função do 1º grau dado o gráfico  (FN)
- D25 Máximo/mínimo de função polinomial do 2º grau  (FN)
- D26 Raízes de polinômio e decomposição em fatores  (EXP)
- D27 Representação algébrica/gráfica de função exponencial  (FN)
- D28 Função logarítmica como inversa da exponencial  (FN)
- D29 Problema com função exponencial  (FN)
- D30 Gráficos de funções trigonométricas  (FN)
- D31 Solução de sistema linear via matriz  (EXP)
- D32 Contagem / análise combinatória  (EST)
- D33 Probabilidade de um evento  (EST)

## IV. Tratamento da Informação  (-> LEI)
- D34 Problema com informações em tabelas e/ou gráficos
- D35 Associar listas/tabelas a gráficos e vice-versa

## Notas do de-para
- **NQ (frações)** não tem descritor próprio no EM -> 9 habilidades efetivas.
- Casos de fronteira (revisáveis): geometria analítica D7–D10 -> GEO; PA/PG D22 -> FN; sistemas/matrizes D31 -> EXP; combinatória D32 -> EST.
- Itens-âncora de 9º ano (códigos `9N*`, `9A*`) aparecem por equalização vertical; mapeados por prefixo (N->NR, A->FN).
- O código do descritor no microdado vem em `TS_ITEM.NU_DESCRITOR_HABILIDADE`. Em alguns anos pode vir como `D15` e em outros como `H..`; conferir por edição.
