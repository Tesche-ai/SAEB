"""Consolida SAEB por ano — Ensino Médio, Matemática. Generalizado por schema.

Uso: python3 scripts/build_consolidated.py <ANO> [<ANO> ...]   (2017, 2019, 2023)

Escoreia respostas item-a-item via gabarito, mapeia descritor -> T1..T10,
estratifica por proficiência e salva data/consolidated_saeb_<ANO>_em.parquet.

Schemas diferem por edição (nomes/ordem de coluna, separador, pasta-raiz no zip,
código de série EM no banco de itens). O dicionário SCHEMA abaixo absorve isso.
"""
import sys
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
T_LIST = ['NR', 'NQ', 'PCT', 'PROP', 'EXP', 'FN', 'GEO', 'MED', 'LEI', 'EST']
NPOS = 13

_COMMON_NEW = dict(  # 2019/2023: separador ; e nomes "_MT" novos
    presenca='IN_PRESENCA_MT', caderno='ID_CADERNO_MT',
    bloco1='ID_BLOCO_1_MT', bloco2='ID_BLOCO_2_MT',
    resp1='TX_RESP_BLOCO1_MT', resp2='TX_RESP_BLOCO2_MT',
    prof='PROFICIENCIA_MT_SAEB', escola='ID_ESCOLA', turma='ID_TURMA',
    uf='ID_UF', publica='IN_PUBLICA', serie='ID_SERIE', peso='PESO_ALUNO_MT')
_ITEMCOL_NEW = dict(disc='DISCIPLINA', serie='ID_SERIE', bloco='BLOCO',
                    pos='POSICAO', desc='NU_DESCRITOR_HABILIDADE', gab='GABARITO')
_ITEMCOL_2023 = dict(disc='TP_DISCIPLINA', serie='ID_SERIE', bloco='NU_BLOCO',
                     pos='NU_POSICAO', desc='NU_DESCRITOR_HABILIDADE', gab='TX_GABARITO')

SCHEMA = {
    2017: dict(
        aluno='DADOS/TS_ALUNO_3EM_ESC.csv', sep=',',
        item='DADOS/TS_ITEM.csv', item_sep=';', item_serie_em=12,
        col=dict(presenca='IN_PRESENCA_PROVA', caderno='ID_CADERNO',
                 bloco1='ID_BLOCO_1', bloco2='ID_BLOCO_2',
                 resp1='TX_RESP_BLOCO_1_MT', resp2='TX_RESP_BLOCO_2_MT',
                 prof='PROFICIENCIA_MT_SAEB', escola='ID_ESCOLA', turma='ID_TURMA',
                 uf='ID_UF', publica='IN_PUBLICA', serie='ID_SERIE', peso='PESO_ALUNO_MT'),
        item_col=_ITEMCOL_NEW, inse=None),
    2019: dict(
        aluno='DADOS/TS_ALUNO_34EM.csv', sep=';',
        item='DADOS/TS_ITEM.csv', item_sep=';', item_serie_em=12,
        col=_COMMON_NEW, item_col=_ITEMCOL_NEW, inse=None),
    2021: dict(
        aluno='DADOS/TS_ALUNO_34EM.csv', sep=';',
        item='DADOS/TS_ITEM.csv', item_sep=';', item_serie_em=12,
        col=_COMMON_NEW, item_col=_ITEMCOL_NEW, inse='INSE_ALUNO'),
    2023: dict(
        aluno='MICRODADOS_SAEB_2023/DADOS/TS_ALUNO_34EM.csv', sep=';',
        item='MICRODADOS_SAEB_2023/DADOS/TS_ITEM.csv', item_sep=';', item_serie_em=3,
        col=_COMMON_NEW, item_col=_ITEMCOL_2023, inse='INSE_ALUNO'),
}
ALUNO_SERIE_EM = ['12', '13']

dep = pd.read_csv(ROOT / 'depara_descritor_t.csv')
DESC2T = dict(zip(dep['descritor'].astype(str).str.strip(), dep['T']))


def run(year):
    cfg = SCHEMA[year]
    zf = zipfile.ZipFile(ROOT / 'data' / f'microdados_saeb_{year}.zip')

    it = pd.read_csv(zf.open(cfg['item']), sep=cfg['item_sep'], encoding='latin-1')
    ic = cfg['item_col']
    it = it[(it[ic['serie']] == cfg['item_serie_em']) & (it[ic['disc']] == 'MT')]
    GAB, TMAP, nomatch = {}, {}, set()
    for _, r in it.iterrows():
        b, p = int(r[ic['bloco']]), int(r[ic['pos']])
        GAB[(b, p)] = set(str(r[ic['gab']]).strip().upper().split('/'))
        d = str(r[ic['desc']]).strip()
        TMAP[(b, p)] = DESC2T.get(d, 'OUTRO')
        if d not in DESC2T:
            nomatch.add(d)
    BLOCKS = sorted({b for (b, p) in GAB})
    print(f'[{year}] itens MT EM: {len(GAB)} | blocos {BLOCKS} | sem de-para: {sorted(nomatch)}')

    c = cfg['col']
    need = [c[k] for k in ('presenca', 'caderno', 'bloco1', 'bloco2', 'resp1', 'resp2',
                           'prof', 'escola', 'turma', 'uf', 'publica', 'serie', 'peso')]
    if cfg['inse']:
        need.append(cfg['inse'])
    print(f'[{year}] lendo aluno ({cfg["aluno"]})...')
    df = pd.read_csv(zf.open(cfg['aluno']), sep=cfg['sep'], encoding='latin-1',
                     usecols=lambda x: x in need, dtype=str)
    df = df[df[c['presenca']] == '1']
    df = df[df[c['serie']].isin(ALUNO_SERIE_EM)]
    for rc in (c['resp1'], c['resp2']):
        df[rc] = df[rc].fillna('').str.upper()
    df = df[(df[c['resp1']].str.len() >= NPOS) & (df[c['resp2']].str.len() >= NPOS)]
    prof = pd.to_numeric(df[c['prof']].str.replace(',', '.'), errors='coerce')
    df = df[prof.notna()].copy()
    df['prof'] = prof[prof.notna()].values
    N = len(df)
    print(f'[{year}] alunos EM válidos: {N:,}')

    seen_T = {T: np.zeros(N, np.int16) for T in T_LIST}
    corr_T = {T: np.zeros(N, np.int16) for T in T_LIST}
    n_seen = np.zeros(N, np.int16); n_corr = np.zeros(N, np.int16)
    for slot in (1, 2):
        blk = pd.to_numeric(df[c[f'bloco{slot}']], errors='coerce').to_numpy()
        resp = df[c[f'resp{slot}']]
        bmasks = {b: (blk == b) for b in BLOCKS}
        for p in range(1, NPOS + 1):
            ans = resp.str[p - 1].to_numpy()
            for b in BLOCKS:
                key = (b, p)
                if key not in GAB or not bmasks[b].any():
                    continue
                m = bmasks[b]; T = TMAP[key]
                n_seen[m] += 1
                cor = m & np.isin(ans, list(GAB[key]))
                n_corr[cor] += 1
                if T in seen_T:
                    seen_T[T][m] += 1; corr_T[T][cor] += 1

    out = pd.DataFrame({
        'ID_ESCOLA': pd.to_numeric(df[c['escola']], errors='coerce').values,
        'ID_TURMA': pd.to_numeric(df[c['turma']], errors='coerce').values,
        'ID_UF': pd.to_numeric(df[c['uf']], errors='coerce').values,
        'IN_PUBLICA': pd.to_numeric(df[c['publica']], errors='coerce').values,
        'proficiencia': df['prof'].values,
        'peso': pd.to_numeric(df[c['peso']].str.replace(',', '.'), errors='coerce').values,
        'inse': (pd.to_numeric(df[cfg['inse']].str.replace(',', '.'), errors='coerce').values
                 if cfg['inse'] else np.nan),
        'n_seen': n_seen, 'n_corr': n_corr, 'ano': year,
    })
    out['taxa_acerto'] = out['n_corr'] / out['n_seen'].clip(lower=1)
    for T in T_LIST:
        out[f'seen_{T}'] = seen_T[T]; out[f'corr_{T}'] = corr_T[T]
    pr = out['proficiencia']
    out['estrato'] = np.where(out['taxa_acerto'] < 0.20, 'Chute',
                       np.where(pr < 275, 'Baixo', np.where(pr < 350, 'Médio', 'Alto')))

    outpath = ROOT / 'data' / f'consolidated_saeb_{year}_em.parquet'
    out.to_parquet(outpath, index=False)
    corr = np.corrcoef(out['taxa_acerto'], out['proficiencia'])[0, 1]
    print(f'[{year}] OK -> {outpath.name} | N={N:,} | taxa média {out["taxa_acerto"].mean():.3f} | '
          f'corr(taxa,prof)={corr:.3f}')
    print(f'[{year}] estratos %: '
          + (out['estrato'].value_counts(normalize=True) * 100).round(1).to_dict().__repr__())
    return corr


if __name__ == '__main__':
    years = [int(a) for a in sys.argv[1:]] or [2017, 2019, 2023]
    for y in years:
        run(y)
