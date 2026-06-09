"""Consolida SAEB 2023 — Ensino Médio, Matemática.

Espelha o pipeline do ENEM: escoreia as respostas item-a-item via gabarito,
mapeia cada item à habilidade (descritor -> T1..T10), estratifica por
proficiência e produz um parquet por aluno com:
  - proficiência (escala SAEB equalizada), peso, INSE, escola, turma, UF
  - taxa de acerto (26 itens), estrato (Chute/Baixo/Médio/Alto)
  - por habilidade T: itens vistos e acertos (para agregação por grupo)

Estratos (decisão documentada em saeb/DECISOES.md):
  Chute: taxa de acerto < 0,20 (acaso em 5 alternativas)
  Baixo: prof < 275 | Médio: 275–350 | Alto: >= 350 (aprendizado adequado)

Saída: saeb/data/consolidated_saeb_2023_em.parquet
"""
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent          # .../saeb
ZIP = ROOT / 'data' / 'microdados_saeb_2023.zip'
ITEM_CSV = ROOT / 'data' / 'MICRODADOS_SAEB_2023' / 'DADOS' / 'TS_ITEM.csv'
ALUNO_MEMBER = 'MICRODADOS_SAEB_2023/DADOS/TS_ALUNO_34EM.csv'
OUT = ROOT / 'data' / 'consolidated_saeb_2023_em.parquet'

T_LIST = ['NR', 'NQ', 'PCT', 'PROP', 'EXP', 'FN', 'GEO', 'MED', 'LEI', 'EST']
NPOS = 13   # itens por bloco (serie EM, MT)

# ---- de-para descritor -> T -------------------------------------------------
dep = pd.read_csv(ROOT / 'depara_descritor_t.csv')
DESC2T = dict(zip(dep['descritor'].astype(str).str.strip(), dep['T']))

# ---- banco de itens: (bloco, posicao) -> gabarito / T -----------------------
it = pd.read_csv(ITEM_CSV, sep=';', encoding='latin-1')
it = it[(it['ID_SERIE'] == 3) & (it['TP_DISCIPLINA'] == 'MT')].copy()
GAB, TMAP = {}, {}
for _, r in it.iterrows():
    b, p = int(r['NU_BLOCO']), int(r['NU_POSICAO'])
    GAB[(b, p)] = set(str(r['TX_GABARITO']).strip().upper().split('/'))
    TMAP[(b, p)] = DESC2T.get(str(r['NU_DESCRITOR_HABILIDADE']).strip(), 'OUTRO')
BLOCKS = sorted({b for (b, p) in GAB})
print(f'Itens MT EM: {len(GAB)} | blocos {BLOCKS} | descritores->T sem match: '
      f'{sum(1 for v in TMAP.values() if v == "OUTRO")}')

# ---- base de aluno (lê do zip, só colunas necessárias) ----------------------
USECOLS = ['ID_UF', 'ID_ESCOLA', 'IN_PUBLICA', 'ID_TURMA', 'ID_SERIE', 'ID_ALUNO',
           'IN_PRESENCA_MT', 'ID_BLOCO_1_MT', 'ID_BLOCO_2_MT',
           'TX_RESP_BLOCO1_MT', 'TX_RESP_BLOCO2_MT',
           'PROFICIENCIA_MT_SAEB', 'PESO_ALUNO_MT', 'INSE_ALUNO']
print('Lendo TS_ALUNO_34EM (do zip)...')
with zipfile.ZipFile(ZIP) as zf:
    df = pd.read_csv(zf.open(ALUNO_MEMBER), sep=';', encoding='latin-1',
                     usecols=USECOLS, dtype=str)
print(f'  linhas brutas: {len(df):,}')

# filtros: presente em MT, EM (série 12/13), strings de resposta válidas
df = df[df['IN_PRESENCA_MT'] == '1']
df = df[df['ID_SERIE'].isin(['12', '13'])]
for c in ['TX_RESP_BLOCO1_MT', 'TX_RESP_BLOCO2_MT']:
    df[c] = df[c].fillna('').str.upper()
df = df[(df['TX_RESP_BLOCO1_MT'].str.len() >= NPOS) &
        (df['TX_RESP_BLOCO2_MT'].str.len() >= NPOS)]
prof = pd.to_numeric(df['PROFICIENCIA_MT_SAEB'].str.replace(',', '.'), errors='coerce')
df = df[prof.notna()].copy()
df['prof'] = prof[prof.notna()].values
N = len(df)
print(f'  alunos EM presentes em MT com resposta e proficiência: {N:,}')

# ---- escoreamento vetorizado ------------------------------------------------
seen_T = {T: np.zeros(N, dtype=np.int16) for T in T_LIST}
corr_T = {T: np.zeros(N, dtype=np.int16) for T in T_LIST}
n_seen = np.zeros(N, dtype=np.int16)
n_corr = np.zeros(N, dtype=np.int16)

for slot in (1, 2):
    blk = pd.to_numeric(df[f'ID_BLOCO_{slot}_MT'], errors='coerce').to_numpy()
    resp = df[f'TX_RESP_BLOCO{slot}_MT']
    bmasks = {b: (blk == b) for b in BLOCKS}
    for p in range(1, NPOS + 1):
        ans = resp.str[p - 1].to_numpy()
        for b in BLOCKS:
            key = (b, p)
            if key not in GAB:
                continue
            m = bmasks[b]
            if not m.any():
                continue
            T = TMAP[key]
            n_seen[m] += 1
            corr = m & np.isin(ans, list(GAB[key]))
            n_corr[corr] += 1
            if T in seen_T:
                seen_T[T][m] += 1
                corr_T[T][corr] += 1

# ---- monta saída ------------------------------------------------------------
out = pd.DataFrame({
    'ID_ALUNO': df['ID_ALUNO'].values,
    'ID_ESCOLA': pd.to_numeric(df['ID_ESCOLA'], errors='coerce').values,
    'ID_TURMA': pd.to_numeric(df['ID_TURMA'], errors='coerce').values,
    'ID_UF': pd.to_numeric(df['ID_UF'], errors='coerce').values,
    'IN_PUBLICA': pd.to_numeric(df['IN_PUBLICA'], errors='coerce').values,
    'proficiencia': df['prof'].values,
    'peso': pd.to_numeric(df['PESO_ALUNO_MT'].str.replace(',', '.'), errors='coerce').values,
    'inse': pd.to_numeric(df['INSE_ALUNO'].str.replace(',', '.'), errors='coerce').values,
    'n_seen': n_seen, 'n_corr': n_corr,
})
out['taxa_acerto'] = out['n_corr'] / out['n_seen'].clip(lower=1)
for T in T_LIST:
    out[f'seen_{T}'] = seen_T[T]
    out[f'corr_{T}'] = corr_T[T]

p = out['proficiencia']
out['estrato'] = np.where(out['taxa_acerto'] < 0.20, 'Chute',
                   np.where(p < 275, 'Baixo',
                     np.where(p < 350, 'Médio', 'Alto')))

OUT.parent.mkdir(parents=True, exist_ok=True)
out.to_parquet(OUT, index=False)
print(f'\nOK -> {OUT}  ({len(out):,} alunos)')
print('Distribuição de estrato:')
print((out['estrato'].value_counts(normalize=True) * 100).round(1).to_string())
print(f"\nTaxa de acerto média: {out['taxa_acerto'].mean():.3f} | "
      f"itens vistos médio: {out['n_seen'].mean():.1f}")
