"""Figuras do artigo SAEB 2023 (EM, Matemática), espelhando os capítulos do ENEM.

Lê saeb/data/consolidated_saeb_2023_em.parquet e gera PNGs em saeb/outputs/figures/.
Estilo Economist (article_style.py do projeto ENEM) para consistência visual.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # article_style vendorizado
from article_style import apply_style, economist_style, PALETTE
apply_style()

OUT = ROOT / 'outputs' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_parquet(ROOT / 'data' / 'consolidated_saeb_2023_em.parquet')
print(f'{len(df):,} alunos')

STRATA = ['Chute', 'Baixo', 'Médio', 'Alto']
SCOL = {'Chute': '#6C757D', 'Baixo': '#FFB81C', 'Médio': '#00847E', 'Alto': '#5DADE2'}
# NQ (frações) não tem descritor no EM -> excluída
T_USE = ['NR', 'PCT', 'PROP', 'EXP', 'FN', 'GEO', 'MED', 'LEI', 'EST']
T_NOME = {'NR': 'Números reais', 'PCT': 'Porcentagem', 'PROP': 'Proporcionalidade',
          'EXP': 'Equações', 'FN': 'Funções', 'GEO': 'Geometria', 'MED': 'Medida',
          'LEI': 'Leitura de dados', 'EST': 'Estatística/prob.'}


def acerto_T(d):
    return {T: d[f'corr_{T}'].sum() / max(d[f'seen_{T}'].sum(), 1) for T in T_USE}


# ============================================================ 1. DISTRIBUIÇÃO
def fig_distribuicao():
    pct = (df['estrato'].value_counts(normalize=True) * 100).reindex(STRATA)
    fig, ax = plt.subplots(figsize=(11, 5.4))
    ax.hist(df['proficiencia'], bins=80, color=PALETTE['teal'], alpha=0.85, edgecolor='white', linewidth=0.3)
    for x, lab in [(275, 'Baixo|Médio'), (350, 'Médio|Alto (adequado)')]:
        ax.axvline(x, color=PALETTE['gray_mid'], ls='--', lw=1.2)
        ax.text(x + 2, ax.get_ylim()[1] * 0.92, lab, fontsize=9, color=PALETTE['gray_mid'])
    txt = (f"Chute {pct['Chute']:.0f}%  ·  Baixo {pct['Baixo']:.0f}%  ·  "
           f"Médio {pct['Médio']:.0f}%  ·  Alto {pct['Alto']:.1f}%")
    ax.set_xlabel('Proficiência em matemática (escala SAEB)')
    economist_style(ax, title='Distribuição da proficiência — 3ª série EM, 2023',
                    subtitle=txt)
    fig.savefig(OUT / 'fig1_distribuicao.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  fig1_distribuicao')


# ============================================================ 2. DOMÍNIO × ESTRATO
def fig_dominio_estrato():
    mat = {s: acerto_T(df[df['estrato'] == s]) for s in STRATA}
    pop = acerto_T(df)
    order = sorted(T_USE, key=lambda T: pop[T])   # piores embaixo
    fig, ax = plt.subplots(figsize=(11, 6.5))
    n_per = df['estrato'].value_counts()
    size = {s: 60 + n_per.get(s, 0) / n_per.max() * 240 for s in STRATA}
    for i, T in enumerate(order):
        vals = [mat[s][T] * 100 for s in STRATA]
        ax.plot([min(vals), max(vals)], [i, i], color=PALETTE['gray_light'], lw=1.5, zorder=1)
        for s in STRATA:
            ax.scatter(mat[s][T] * 100, i, s=size[s], color=SCOL[s], edgecolor='white',
                       linewidth=1.4, zorder=3)
        ax.text(102, i, f'{pop[T]*100:.0f}%', va='center', fontsize=10, fontweight=800,
                color=PALETTE['orange'])
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([T_NOME[T] for T in order], fontsize=11)
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 20, 40, 50, 60, 80, 100])
    ax.axvline(50, color='#ccc', ls=':', lw=1)
    handles = [plt.scatter([], [], s=size[s], color=SCOL[s], edgecolor='white', label=s) for s in STRATA]
    ax.legend(handles=handles, loc='lower right', ncol=4, frameon=False, fontsize=9.5,
              title='Estrato (tamanho = peso populacional) · laranja = % acerto da população')
    economist_style(ax, title='Taxa de acerto por habilidade e estrato — SAEB EM 2023',
                    subtitle='Cada ponto é a probabilidade de acertar um item da habilidade',
                    drop_yaxis=False, drop_xaxis=False)
    ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)
    fig.savefig(OUT / 'fig2_dominio_estrato.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  fig2_dominio_estrato')


# ============================================================ 3. TRANSIÇÕES
def fig_transicoes():
    mat = {s: acerto_T(df[df['estrato'] == s]) for s in STRATA}
    steps = [('Chute', 'Baixo'), ('Baixo', 'Médio'), ('Médio', 'Alto')]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6))
    for ax, (a, b) in zip(axes, steps):
        delta = {T: (mat[b][T] - mat[a][T]) * 100 for T in T_USE}
        s = sorted(delta.items(), key=lambda kv: kv[1])
        labels = [T_NOME[k] for k, _ in s]; vals = [v for _, v in s]
        mx = max(abs(v) for v in vals) or 1
        colors = [PALETTE['orange'] if abs(v) / mx > 0.66 else
                  (PALETTE['yellow'] if abs(v) / mx > 0.33 else PALETTE['gray_light']) for v in vals]
        ax.barh(range(len(s)), vals, color=colors, zorder=3, height=0.66)
        ax.set_yticks(range(len(s))); ax.set_yticklabels(labels, fontsize=9.5)
        for i, v in enumerate(vals):
            ax.text(v + (0.5 if v >= 0 else -0.5), i, f'{v:+.0f}', va='center',
                    ha='left' if v >= 0 else 'right', fontsize=9, fontweight=700, color=PALETTE['navy'])
        ax.axvline(0, color=PALETTE['gray_mid'], lw=0.8)
        ax.set_xlim(min(vals) - mx*0.25, max(vals) + mx*0.25)
        economist_style(ax, title=f'{a} → {b}', subtitle='Δ pontos percentuais de acerto',
                        drop_xaxis=True, drop_yaxis=False)
        ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)
    fig.savefig(OUT / 'fig3_transicoes.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  fig3_transicoes')


# ============================================================ 4. EMERGÊNCIA POR PERCENTIL
def fig_emergencia():
    d = df.copy()
    d['pct'] = pd.qcut(d['proficiencia'], 100, labels=False, duplicates='drop')
    rows = []
    for p, sub in d.groupby('pct'):
        a = acerto_T(sub)
        for T in T_USE:
            rows.append((p, T, a[T] * 100))
    g = pd.DataFrame(rows, columns=['pct', 'T', 'acerto']).pivot(index='pct', columns='T', values='acerto')
    fig, ax = plt.subplots(figsize=(11, 6))
    cmap = plt.cm.viridis(np.linspace(0, 0.92, len(T_USE)))
    for c, T in zip(cmap, T_USE):
        ax.plot(g.index + 1, g[T], color=c, lw=2, label=T_NOME[T])
    ax.axhline(50, color=PALETTE['gray_mid'], ls='--', lw=1)
    ax.set_xlabel('Percentil de proficiência'); ax.set_ylabel('% de acerto'); ax.set_ylim(0, 100)
    ax.legend(loc='upper left', ncol=2, frameon=False, fontsize=8.5)
    economist_style(ax, title='Em que ordem as habilidades "acordam" — SAEB EM 2023',
                    subtitle='Acerto por habilidade ao longo do percentil de proficiência', drop_yaxis=False)
    fig.savefig(OUT / 'fig4_emergencia.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  fig4_emergencia')


# ============================================================ 5. ESCOLAS — 6 SEGMENTOS
def seg_escola(media, sd, sd_cut):
    if media < 275:
        return 'Baixa'
    if media >= 350:
        return 'Alta'
    return 'Média·Coesa' if sd < sd_cut else 'Média·Mista'


def fig_escolas():
    g = df.groupby('ID_ESCOLA').agg(n=('proficiencia', 'size'),
                                    media=('proficiencia', 'mean'),
                                    sd=('proficiencia', 'std'),
                                    pub=('IN_PUBLICA', 'mean')).reset_index()
    g = g[g['n'] >= 10].dropna()
    sd_cut = round(g['sd'].median())
    g['seg'] = [seg_escola(m, s, sd_cut) for m, s in zip(g['media'], g['sd'])]
    print(f'  escolas N>=10: {len(g):,} | corte dispersão (mediana) = {sd_cut}')
    print('  ' + g['seg'].value_counts().to_string().replace('\n', ' | '))
    fig, ax = plt.subplots(figsize=(11, 6.3))
    for pub, color, lab in [(1, '#1F5582', 'Pública'), (0, PALETTE['orange'], 'Privada')]:
        s = g[(g['pub'] >= 0.5) == (pub == 1)]
        ax.scatter(s['media'], s['sd'], s=5, color=color, alpha=0.30, edgecolors='none', label=lab)
    for x in (275, 350):
        ax.axvline(x, color='#bbb', lw=0.8)
    ax.axhline(sd_cut, color='#bbb', lw=0.8)
    ax.set_xlabel('Proficiência média da escola'); ax.set_ylabel('Desvio-padrão interno')
    ax.legend(loc='upper right', frameon=False, markerscale=3)
    economist_style(ax, title='Escolas em seis segmentos — SAEB EM 2023',
                    subtitle=f'Cada ponto é uma escola (N≥10) · corte de dispersão = {sd_cut}', drop_yaxis=False)
    fig.savefig(OUT / 'fig5_escolas.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  fig5_escolas')
    return g, sd_cut


# ============================================================ 6. SALA DE AULA POR SEGMENTO
def fig_sala(g_esc, sd_cut):
    seg_by_esc = dict(zip(g_esc['ID_ESCOLA'], g_esc['seg']))
    d = df[df['ID_ESCOLA'].isin(seg_by_esc)].copy()
    d['seg'] = d['ID_ESCOLA'].map(seg_by_esc)
    SEGS = ['Baixa', 'Média·Coesa', 'Média·Mista', 'Alta']
    comp = (d.groupby('seg')['estrato'].value_counts(normalize=True).unstack()
            .reindex(index=SEGS, columns=STRATA).fillna(0) * 100)
    fig, ax = plt.subplots(figsize=(10, 5.4))
    bottom = np.zeros(len(SEGS))
    for s in STRATA:
        ax.bar(SEGS, comp[s].values, bottom=bottom, color=SCOL[s], label=s, edgecolor='white', width=0.6)
        for i, (v, b) in enumerate(zip(comp[s].values, bottom)):
            if v >= 6:
                ax.text(i, b + v / 2, f'{v:.0f}', ha='center', va='center', fontsize=9,
                        fontweight=700, color='white')
        bottom += comp[s].values
    ax.set_ylim(0, 100); ax.set_ylabel('% da turma')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.16), ncol=4, frameon=False)
    economist_style(ax, title='Como é a sala de aula em cada segmento de escola',
                    subtitle='Composição média por estrato do aluno · SAEB EM 2023')
    fig.savefig(OUT / 'fig6_sala.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  fig6_sala')


# ============================================================ 7. SOCIO (INSE)
def fig_socio():
    d = df.dropna(subset=['inse']).copy()
    d['inse_q'] = pd.qcut(d['inse'], 5, labels=['Q1 (+ pobre)', 'Q2', 'Q3', 'Q4', 'Q5 (+ rico)'], duplicates='drop')
    rows = []
    for q, sub in d.groupby('inse_q', observed=True):
        a = acerto_T(sub)
        rows.append((q, sub['proficiencia'].mean(), (sub['estrato'] == 'Alto').mean() * 100, a))
    fig, ax = plt.subplots(figsize=(10, 5.2))
    qs = [r[0] for r in rows]; prof = [r[1] for r in rows]; alto = [r[2] for r in rows]
    ax.bar(range(len(qs)), prof, color=PALETTE['teal'], width=0.6, zorder=3)
    for i, (p, a) in enumerate(zip(prof, alto)):
        ax.text(i, p + 2, f'{p:.0f}\n({a:.1f}% Alto)', ha='center', fontsize=9, fontweight=700, color=PALETTE['navy'])
    ax.set_xticks(range(len(qs))); ax.set_xticklabels(qs)
    ax.set_ylabel('Proficiência média'); ax.set_ylim(0, max(prof) * 1.2)
    economist_style(ax, title='Proficiência por quinto socioeconômico (INSE) — SAEB EM 2023',
                    subtitle='Entre parênteses, % no estrato Alto (aprendizado adequado)', drop_yaxis=False)
    fig.savefig(OUT / 'fig7_socio.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  fig7_socio')


if __name__ == '__main__':
    fig_distribuicao()
    fig_dominio_estrato()
    fig_transicoes()
    fig_emergencia()
    g_esc, sd_cut = fig_escolas()
    fig_sala(g_esc, sd_cut)
    fig_socio()
    print('Done.')
