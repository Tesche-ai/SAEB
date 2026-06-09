"""Consolida SAEB 2023 — Ensino Fundamental (5º e 9º ano), Matemática.

Habilidade no nível de TEMA (4 áreas da Matriz de Referência), porque os
descritores do EF (5º: D1-D28; 9º: D1-D37) diferem dos do EM e não há texto
item-a-item para um de-para fino. Fronteiras de tema (padrão da matriz):
  5º: Espaço/Forma D1-D5 · Grandezas/Medidas D6-D12 · Números/Álgebra D13-D26 · Trat.Info D27-D28
  9º: Espaço/Forma D1-D12 · Grandezas/Medidas D13-D18 · Números/Álgebra D19-D35 · Trat.Info D36-D37
Códigos-âncora (5E*/9A*/...) mapeados pela letra (E->ESP, G/M->GM, N/A->NUM).

Saída: data/consolidated_saeb_2023_<5ef|9ef>_em.parquet (com per-tema, ctot, inse, ids).
"""
import sys
import zipfile
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZIP = ROOT / 'data' / 'microdados_saeb_2023.zip'
PRE = 'MICRODADOS_SAEB_2023/DADOS/'
TEMAS = ['ESP', 'GM', 'NUM', 'TI']
GRADE = {'5ef': dict(serie_item=5, serie_aluno='5', aluno=PRE + 'TS_ALUNO_5EF.csv'),
         '9ef': dict(serie_item=9, serie_aluno='9', aluno=PRE + 'TS_ALUNO_9EF.csv')}
ITEMCOL = dict(disc='TP_DISCIPLINA', serie='ID_SERIE', bloco='NU_BLOCO',
               pos='NU_POSICAO', desc='NU_DESCRITOR_HABILIDADE', gab='TX_GABARITO')
# limiares de aprendizado adequado (Todos pela Educação / INEP)
ADEQ = {'5ef': 225, '9ef': 300}


def tema_for(grade_n, desc):
    desc = str(desc).strip()
    if len(desc) > 1 and desc[0].isdigit() and desc[1] in 'EGMNA':
        return {'E': 'ESP', 'G': 'GM', 'M': 'GM', 'N': 'NUM', 'A': 'NUM'}[desc[1]]
    if desc.startswith('D'):
        try:
            n = int(desc[1:].split('.')[0])
        except ValueError:
            return 'OUTRO'
        if grade_n == 5:
            return 'ESP' if n <= 5 else 'GM' if n <= 12 else 'NUM' if n <= 26 else 'TI'
        return 'ESP' if n <= 12 else 'GM' if n <= 18 else 'NUM' if n <= 35 else 'TI'
    return 'OUTRO'


def run(gkey):
    g = GRADE[gkey]; grade_n = g['serie_item']
    zf = zipfile.ZipFile(ZIP)
    it = pd.read_csv(zf.open(PRE + 'TS_ITEM.csv'), sep=';', encoding='latin-1')
    it = it[(it[ITEMCOL['serie']] == grade_n) & (it[ITEMCOL['disc']] == 'MT')].copy()
    NPOS = int(pd.to_numeric(it[ITEMCOL['pos']]).max())
    GAB, TMAP, nomatch = {}, {}, set()
    for _, r in it.iterrows():
        b, p = int(r[ITEMCOL['bloco']]), int(r[ITEMCOL['pos']])
        GAB[(b, p)] = set(str(r[ITEMCOL['gab']]).strip().upper().split('/'))
        tm = tema_for(grade_n, r[ITEMCOL['desc']])
        TMAP[(b, p)] = tm
        if tm == 'OUTRO':
            nomatch.add(str(r[ITEMCOL['desc']]).strip())
    BLOCKS = sorted({b for (b, p) in GAB})
    print(f'[{gkey}] itens {len(GAB)} NPOS={NPOS} blocos={BLOCKS} sem-tema={sorted(nomatch)}')

    need = ['IN_PRESENCA_MT', 'ID_CADERNO_MT', 'ID_BLOCO_1_MT', 'ID_BLOCO_2_MT',
            'TX_RESP_BLOCO1_MT', 'TX_RESP_BLOCO2_MT', 'PROFICIENCIA_MT_SAEB',
            'ID_ESCOLA', 'ID_TURMA', 'ID_UF', 'ID_SERIE', 'INSE_ALUNO']
    df = pd.read_csv(zf.open(g['aluno']), sep=';', encoding='latin-1',
                     usecols=lambda x: x in need, dtype=str)
    df = df[df['IN_PRESENCA_MT'] == '1']
    df = df[df['ID_SERIE'] == g['serie_aluno']]
    for rc in ('TX_RESP_BLOCO1_MT', 'TX_RESP_BLOCO2_MT'):
        df[rc] = df[rc].fillna('').str.upper()
    df = df[(df['TX_RESP_BLOCO1_MT'].str.len() >= NPOS) & (df['TX_RESP_BLOCO2_MT'].str.len() >= NPOS)]
    prof = pd.to_numeric(df['PROFICIENCIA_MT_SAEB'].str.replace(',', '.'), errors='coerce')
    df = df[prof.notna()].copy(); df['prof'] = prof[prof.notna()].values
    N = len(df)
    print(f'[{gkey}] alunos: {N:,}')

    seen = {t: np.zeros(N, np.int16) for t in TEMAS}
    corr = {t: np.zeros(N, np.int16) for t in TEMAS}
    ntot = np.zeros(N, np.int16); ctot = np.zeros(N, np.int16)
    for slot in (1, 2):
        blk = pd.to_numeric(df[f'ID_BLOCO_{slot}_MT'], errors='coerce').to_numpy()
        resp = df[f'TX_RESP_BLOCO{slot}_MT']
        bmasks = {b: (blk == b) for b in BLOCKS}
        for p in range(1, NPOS + 1):
            ans = resp.str[p - 1].to_numpy()
            for b in BLOCKS:
                key = (b, p)
                if key not in GAB or not bmasks[b].any():
                    continue
                m = bmasks[b]; cor = m & np.isin(ans, list(GAB[key]))
                ntot[m] += 1; ctot[cor] += 1
                t = TMAP[key]
                if t in seen:
                    seen[t][m] += 1; corr[t][cor] += 1

    out = pd.DataFrame({
        'ID_ESCOLA': pd.to_numeric(df['ID_ESCOLA'], errors='coerce').values,
        'ID_TURMA': pd.to_numeric(df['ID_TURMA'], errors='coerce').values,
        'ID_UF': pd.to_numeric(df['ID_UF'], errors='coerce').values,
        'proficiencia': df['prof'].values,
        'inse': pd.to_numeric(df['INSE_ALUNO'].str.replace(',', '.'), errors='coerce').values,
        'ntot': ntot, 'ctot': ctot, 'grade': gkey,
    })
    out['taxa_acerto'] = out['ctot'] / out['ntot'].clip(lower=1)
    out['frac'] = out['taxa_acerto']
    for t in TEMAS:
        out[f'seen_{t}'] = seen[t]; out[f'corr_{t}'] = corr[t]
    out['adequado'] = (out['proficiencia'] >= ADEQ[gkey]).astype(int)
    outpath = ROOT / 'data' / f'consolidated_saeb_2023_{gkey}.parquet'
    out.to_parquet(outpath, index=False)
    corr_p = np.corrcoef(out['taxa_acerto'], out['proficiencia'])[0, 1]
    print(f'[{gkey}] OK -> {outpath.name} | prof média={out["proficiencia"].mean():.1f} '
          f'| %adequado(>={ADEQ[gkey]})={out["adequado"].mean()*100:.1f}% | corr(taxa,prof)={corr_p:.3f}')


if __name__ == '__main__':
    for gk in (sys.argv[1:] or ['5ef', '9ef']):
        run(gk)
