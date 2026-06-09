"""Exploratório — detecção de anomalia (manipulação) no SAEB. Ciente de etapa.

Testes:
  #1 achatamento dificuldade<->acerto por escola (acc_fácil - acc_difícil)
  #2 person-fit aberrante por turma (acerta difícil / erra fácil)
  #4 excesso de quase-perfeitos por turma
  #5 similaridade de respostas no mesmo caderno+turma (strings idênticas)
  #6 salto-e-reversão entre edições (painel de escola)  [usa os parquets]

Uso: python3 scripts/anomalia.py <ANO> <ETAPA>   ETAPA in EM | 9EF | 5EF (default EM)
     python3 scripts/anomalia.py painel
"""
import sys
import zipfile
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_consolidated import SCHEMA

# série do aluno e do item por etapa
ETAPA = {
    'EM':  dict(fname={2017: 'TS_ALUNO_3EM_ESC.csv'}, default_fname='TS_ALUNO_34EM.csv',
               aluno_serie=['12', '13'], item_serie=lambda y: SCHEMA[y]['item_serie_em']),
    '9EF': dict(fname={}, default_fname='TS_ALUNO_9EF.csv', aluno_serie=['9'], item_serie=lambda y: 9),
    '5EF': dict(fname={}, default_fname='TS_ALUNO_5EF.csv', aluno_serie=['5'], item_serie=lambda y: 5),
}


def cfg_etapa(year, etapa):
    base = dict(SCHEMA[year]); e = ETAPA[etapa]
    prefix = base['aluno'].split('TS_ALUNO')[0]   # 'MICRODADOS_SAEB_2023/DADOS/' ou 'DADOS/'
    base['aluno'] = prefix + e['fname'].get(year, e['default_fname'])
    base['aluno_serie'] = e['aluno_serie']
    base['item_serie_em'] = e['item_serie'](year)
    return base


def carrega(year, etapa):
    cfg = cfg_etapa(year, etapa); ic = cfg['item_col']; c = cfg['col']
    zf = zipfile.ZipFile(ROOT / 'data' / f'microdados_saeb_{year}.zip')
    it = pd.read_csv(zf.open(cfg['item']), sep=cfg['item_sep'], encoding='latin-1')
    it = it[(it[ic['serie']] == cfg['item_serie_em']) & (it[ic['disc']] == 'MT')].copy()
    it['b'] = pd.to_numeric(it['B'].astype(str).str.replace(',', '.'), errors='coerce')
    NPOS = int(pd.to_numeric(it[ic['pos']]).max())     # detecta itens/bloco da etapa
    q1, q2 = it['b'].quantile([1/3, 2/3])
    GAB, DIFF = {}, {}
    for _, r in it.iterrows():
        b, p = int(r[ic['bloco']]), int(r[ic['pos']])
        GAB[(b, p)] = set(str(r[ic['gab']]).strip().upper().split('/'))
        DIFF[(b, p)] = 'easy' if r['b'] <= q1 else ('hard' if r['b'] >= q2 else 'mid')
    BLOCKS = sorted({b for (b, p) in GAB})

    need = [c[k] for k in ('presenca', 'caderno', 'bloco1', 'bloco2', 'resp1', 'resp2',
                           'prof', 'escola', 'turma')]
    df = pd.read_csv(zf.open(cfg['aluno']), sep=cfg['sep'], encoding='latin-1',
                     usecols=lambda x: x in need, dtype=str)
    df = df[df[c['presenca']] == '1']
    df = df[df[c['serie']].isin(cfg['aluno_serie'])] if c['serie'] in df.columns else df
    for rc in (c['resp1'], c['resp2']):
        df[rc] = df[rc].fillna('').str.upper()
    df = df[(df[c['resp1']].str.len() >= NPOS) & (df[c['resp2']].str.len() >= NPOS)]
    prof = pd.to_numeric(df[c['prof']].str.replace(',', '.'), errors='coerce')
    df = df[prof.notna()].copy(); df['prof'] = prof[prof.notna()].values
    N = len(df)

    es = {'easy': np.zeros(N, np.int16), 'hard': np.zeros(N, np.int16)}
    co = {'easy': np.zeros(N, np.int16), 'hard': np.zeros(N, np.int16)}
    ntot = np.zeros(N, np.int16); ctot = np.zeros(N, np.int16)
    for slot in (1, 2):
        blk = pd.to_numeric(df[c[f'bloco{slot}']], errors='coerce').to_numpy()
        resp = df[c[f'resp{slot}']]
        bmasks = {b: (blk == b) for b in BLOCKS}
        for pos in range(1, NPOS + 1):
            ans = resp.str[pos - 1].to_numpy()
            for b in BLOCKS:
                key = (b, pos)
                if key not in GAB or not bmasks[b].any():
                    continue
                m = bmasks[b]; cor = m & np.isin(ans, list(GAB[key]))
                ntot[m] += 1; ctot[cor] += 1
                d = DIFF[key]
                if d != 'mid':
                    es[d][m] += 1; co[d][cor] += 1

    out = pd.DataFrame({
        'escola': pd.to_numeric(df[c['escola']], errors='coerce').values,
        'turma': pd.to_numeric(df[c['turma']], errors='coerce').values,
        'caderno': pd.to_numeric(df[c['caderno']], errors='coerce').values,
        'prof': df['prof'].values, 'ntot': ntot, 'ctot': ctot,
        'es_e': es['easy'], 'co_e': co['easy'], 'es_h': es['hard'], 'co_h': co['hard'],
        'respstr': (df[c['resp1']].str[:NPOS] + df[c['resp2']].str[:NPOS]).values,
    })
    out['frac'] = out['ctot'] / out['ntot'].clip(lower=1)
    return out, NPOS


def run(year, etapa):
    d, NPOS = carrega(year, etapa)
    L = 2 * NPOS
    print(f'[{year} {etapa}] alunos: {len(d):,} | itens/aluno={L}')
    d['acc_e'] = d['co_e'] / d['es_e'].clip(lower=1)
    d['acc_h'] = d['co_h'] / d['es_h'].clip(lower=1)
    valid = (d['es_e'] > 0) & (d['es_h'] > 0)

    g = d.groupby('escola').agg(n=('prof', 'size'), co_e=('co_e', 'sum'), es_e=('es_e', 'sum'),
                                co_h=('co_h', 'sum'), es_h=('es_h', 'sum')).reset_index()
    g = g[g['n'] >= 30]
    g['gap'] = g['co_e'] / g['es_e'] - g['co_h'] / g['es_h']
    print(f'#1 ACHATAMENTO (escola N>=30: {len(g):,}): gap médio={g["gap"].mean():.3f} '
          f'min={g["gap"].min():.3f} | escolas gap<=0: {(g["gap"]<=0).sum()}')

    d['aberr'] = (valid & (d['acc_h'] > d['acc_e'])).astype(int)
    d['nperf'] = (d['frac'] >= 0.90).astype(int)        # quase-perfeito = >=90% de acerto
    t = d.groupby('turma').agg(n=('prof', 'size'), aberr=('aberr', 'mean'),
                               nperf=('nperf', 'mean')).reset_index()
    t = t[t['n'] >= 15]
    print(f'#2 ABERRÂNCIA (turma N>=15: {len(t):,}): média={t["aberr"].mean()*100:.1f}% '
          f'p99={t["aberr"].quantile(.99)*100:.0f}% | turmas >40% aberrantes: {(t["aberr"]>0.40).sum()}')
    print(f'#4 QUASE-PERFEITOS (>=90% acerto): base={d["nperf"].mean()*100:.2f}% | '
          f'turmas >30% quase-perf: {(t["nperf"]>0.30).sum()} (>50%: {(t["nperf"]>0.50).sum()})')

    thr = int(0.8 * L)
    eng = d[d['respstr'].str.count(r'[A-E]') >= thr].copy()
    grp = eng.groupby(['turma', 'caderno', 'respstr']).size().reset_index(name='k')
    maxid = grp.groupby(['turma', 'caderno'])['k'].max().reset_index(name='maxid')
    nstu = eng.groupby(['turma', 'caderno']).size().reset_index(name='nstu')
    maxid = maxid.merge(nstu, on=['turma', 'caderno']); maxid = maxid[maxid['nstu'] >= 5]
    print(f'#5 STRINGS IDÊNTICAS (grupos turma+caderno c/ >=5 engajados: {len(maxid):,}): '
          f'max bloco idêntico={maxid["maxid"].max() if len(maxid) else 0} | '
          + ' '.join(f'>={k}:{(maxid["maxid"]>=k).sum()}' for k in (3, 4, 5)))


def painel():
    anos = [2017, 2019, 2021, 2023]; piv = None
    for y in anos:
        dd = pd.read_parquet(ROOT / 'data' / f'consolidated_saeb_{y}_em.parquet')
        s = dd.groupby('ID_ESCOLA').agg(p=('proficiencia', 'mean'), n=('proficiencia', 'size'))
        s = s[s['n'] >= 20][['p']].rename(columns={'p': y})
        piv = s if piv is None else piv.join(s, how='inner')
    print(f'#6 PAINEL (EM) — escolas em todos os anos N>=20: {len(piv):,}')
    for y, prev, nxt in [(2019, 2017, 2021), (2021, 2019, 2023)]:
        spike = piv[y] - piv[[prev, nxt]].max(axis=1)
        print(f'   {y} vs vizinhos: média={spike.mean():+.1f} p99={spike.quantile(.99):+.1f} '
              f'max={spike.max():+.1f} | escolas spike>30 e reversão: {(spike>30).sum()}')


if __name__ == '__main__':
    a = sys.argv[1:] or ['2023', 'EM']
    if a[0] == 'painel':
        painel()
    else:
        run(int(a[0]), a[1] if len(a) > 1 else 'EM')
