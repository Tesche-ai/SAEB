"""Figuras do EF (5º e 9º ano) + o teste de fraude #4 x INSE.

Saída em outputs/site/figures/ (entram no site).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from article_style import apply_style, economist_style, PALETTE
apply_style()

OUT = ROOT / 'outputs' / 'site' / 'figures'
TEMAS = ['ESP', 'GM', 'NUM', 'TI']
TNOME = {'ESP': 'Espaço e Forma', 'GM': 'Grandezas e Medidas',
         'NUM': 'Números e Álgebra', 'TI': 'Tratamento da Info'}
G5 = pd.read_parquet(ROOT / 'data' / 'consolidated_saeb_2023_5ef.parquet')
G9 = pd.read_parquet(ROOT / 'data' / 'consolidated_saeb_2023_9ef.parquet')
EM = pd.read_parquet(ROOT / 'data' / 'consolidated_saeb_2023_em.parquet')


def acerto_tema(d):
    return {t: d[f'corr_{t}'].sum() / max(d[f'seen_{t}'].sum(), 1) * 100 for t in TEMAS}


# 1. FUNIL — % adequado por etapa
def fig_funil():
    et = ['5º ano\n(≥225)', '9º ano\n(≥300)', '3ª EM\n(≥350)']
    val = [G5['adequado'].mean() * 100, G9['adequado'].mean() * 100, (EM['proficiencia'] >= 350).mean() * 100]
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    bars = ax.bar(et, val, color=[PALETTE['teal'], '#3E8E7E', PALETTE['orange']], width=0.6, zorder=3)
    for b, v in zip(bars, val):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.8, f'{v:.0f}%', ha='center', fontsize=14, fontweight=800, color=PALETTE['navy'])
    ax.set_ylim(0, max(val) * 1.18); ax.set_ylabel('% com aprendizado adequado')
    economist_style(ax, title='O funil da matemática ao longo da escolaridade',
                    subtitle='% com aprendizado adequado · SAEB 2023, censo', drop_yaxis=False)
    fig.savefig(OUT / 'ef_funil.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
    print('  ef_funil', [round(v, 1) for v in val])


# 2. PERFIL POR TEMA, por tercil de proficiência (cada etapa)
def fig_tema(d, gkey, titulo):
    d = d.copy(); d['terc'] = pd.qcut(d['proficiencia'], 3, labels=['Inferior', 'Médio', 'Superior'])
    pop = acerto_tema(d)
    order = sorted(TEMAS, key=lambda t: pop[t])
    cols = {'Inferior': '#FFB81C', 'Médio': '#00847E', 'Superior': '#5DADE2'}
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    for i, t in enumerate(order):
        vals = {terc: acerto_tema(sub)[t] for terc, sub in d.groupby('terc', observed=True)}
        ax.plot([min(vals.values()), max(vals.values())], [i, i], color=PALETTE['gray_light'], lw=1.5, zorder=1)
        for terc, v in vals.items():
            ax.scatter(v, i, s=150, color=cols[terc], edgecolor='white', linewidth=1.4, zorder=3)
        ax.text(102, i, f'{pop[t]:.0f}%', va='center', fontsize=10, fontweight=800, color=PALETTE['orange'])
    ax.set_yticks(range(len(order))); ax.set_yticklabels([TNOME[t] for t in order], fontsize=11)
    ax.set_xlim(0, 110); ax.axvline(50, color='#ccc', ls=':', lw=1)
    handles = [plt.scatter([], [], s=120, color=c, edgecolor='white', label=l) for l, c in cols.items()]
    ax.legend(handles=handles, loc='lower right', ncol=3, frameon=False, fontsize=9,
              title='Tercil de proficiência · laranja=acerto da população')
    economist_style(ax, title=titulo, subtitle='Taxa de acerto por área da matemática · SAEB 2023',
                    drop_yaxis=False, drop_xaxis=False)
    ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)
    fig.savefig(OUT / f'ef_tema_{gkey}.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
    print(f'  ef_tema_{gkey}')


# 4. TESTE DE FRAUDE: turmas quase-perfeitas x INSE da escola
def fig_inse_fraude(d, gkey, titulo):
    d = d.copy(); d['nperf'] = (d['frac'] >= 0.90).astype(int)
    esc_inse = d.groupby('ID_ESCOLA')['inse'].mean()
    t = d.groupby('ID_TURMA').agg(n=('frac', 'size'), nperf=('nperf', 'mean'),
                                  escola=('ID_ESCOLA', 'first')).reset_index()
    t = t[t['n'] >= 15]
    t['inse_esc'] = t['escola'].map(esc_inse)
    t = t.dropna(subset=['inse_esc'])
    # quintis de INSE da escola
    t['q'] = pd.qcut(t['inse_esc'], 5, labels=['Q1\n(+pobre)', 'Q2', 'Q3', 'Q4', 'Q5\n(+rico)'], duplicates='drop')
    susp = t['nperf'] > 0.30   # turma "suspeita": >30% quase-perfeitos
    base = t['q'].value_counts(normalize=True).reindex(t['q'].cat.categories) * 100
    sus = t.loc[susp, 'q'].value_counts(normalize=True).reindex(t['q'].cat.categories) * 100
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(base)); w = 0.4
    ax.bar(x - w/2, base.values, width=w, color=PALETTE['gray_light'], label='Todas as turmas', zorder=3)
    ax.bar(x + w/2, sus.values, width=w, color=PALETTE['orange'], label='Turmas com >30% quase-perfeitos', zorder=3)
    ax.set_xticks(x); ax.set_xticklabels(base.index)
    ax.set_ylabel('% das turmas'); ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2)
    economist_style(ax, title=titulo,
                    subtitle='Se as turmas suspeitas se concentram nas escolas pobres (Q1), é bandeira vermelha', drop_yaxis=False)
    fig.savefig(OUT / f'ef_fraude_inse_{gkey}.png', dpi=150, bbox_inches='tight', facecolor='white'); plt.close(fig)
    n_susp = int(susp.sum())
    print(f'  ef_fraude_inse_{gkey} | turmas suspeitas={n_susp} | INSE-quintil das suspeitas: '
          + sus.round(0).to_dict().__repr__())
    return base, sus


if __name__ == '__main__':
    fig_funil()
    fig_tema(G5, '5ef', 'Perfil por área — 5º ano')
    fig_tema(G9, '9ef', 'Perfil por área — 9º ano')
    fig_inse_fraude(G5, '5ef', 'Turmas quase-perfeitas por nível socioeconômico — 5º ano')
    fig_inse_fraude(G9, '9ef', 'Turmas quase-perfeitas por nível socioeconômico — 9º ano')
    print('Done.')
