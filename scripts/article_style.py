"""Estilo visual unificado para todas as figuras do artigo."""
import matplotlib as mpl
import matplotlib.pyplot as plt

# ============================================================================
# PALETA — usada em CSS e nas figuras
# ============================================================================
PALETTE = {
    'navy':      '#1a3a4a',   # primary dark — títulos, eixos
    'teal':      '#00847E',   # primary accent — linhas principais, destaque positivo
    'orange':    '#DC4E28',   # secondary accent — privada, alertas, downs
    'yellow':    '#FFB81C',   # highlights, punchlines
    'blue':      '#1F5582',   # pública, secondary blue
    'gray_text': '#2a2a2a',
    'gray_mid':  '#6C757D',
    'gray_light':'#bbbbbb',
    'bg':        '#fafafa',
    'white':     '#ffffff',
}

# Privada/Pública (consistente em todo o artigo)
COLOR_PUBLICA = PALETTE['blue']
COLOR_PRIVADA = PALETTE['orange']

# Skills — 10 categorias, paleta categórica color-blind-friendly
SKILL_COLORS = {
    'NR':   '#1f77b4',  # azul
    'NQ':   '#d62728',  # vermelho
    'PCT':  '#ff7f0e',  # laranja
    'PROP': '#9467bd',  # roxo
    'EXP':  '#8c564b',  # marrom
    'FN':   '#2ca02c',  # verde
    'GEO':  '#e377c2',  # rosa
    'MED':  '#7f7f7f',  # cinza
    'LEI':  '#17becf',  # ciano
    'EST':  '#bcbd22',  # oliva
}

# Estratos
STRATUM_COLORS = {
    'G': '#9E9E9E',
    'L': '#FFB81C',
    'M': '#00847E',
    'H': '#1a3a4a',
}

# ============================================================================
# CONFIG GLOBAL DO MATPLOTLIB
# ============================================================================
def apply_style():
    """Aplica configuração global de estilo do matplotlib."""
    mpl.rcParams.update({
        'figure.dpi': 150,
        'savefig.dpi': 150,
        'savefig.bbox': 'tight',
        'savefig.facecolor': 'white',

        # Tipografia
        'font.family': ['Helvetica Neue', 'Arial', 'DejaVu Sans', 'sans-serif'],
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.titlepad': 16,
        'axes.labelsize': 12,
        'axes.labelweight': 'normal',
        'axes.labelpad': 8,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10.5,
        'legend.frameon': False,
        'legend.handletextpad': 0.6,

        # Cores
        'axes.facecolor': '#ffffff',
        'figure.facecolor': '#ffffff',
        'axes.edgecolor': PALETTE['gray_mid'],
        'axes.labelcolor': PALETTE['gray_text'],
        'xtick.color': PALETTE['gray_text'],
        'ytick.color': PALETTE['gray_text'],
        'text.color': PALETTE['gray_text'],

        # Grid sutil
        'axes.grid': True,
        'axes.grid.axis': 'y',
        'grid.color': '#e0e0e0',
        'grid.linewidth': 0.8,
        'grid.alpha': 0.6,

        # Spines minimalistas
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.linewidth': 1.2,
    })


# ============================================================================
# TAMANHOS PADRONIZADOS
# ============================================================================
SIZES = {
    'hero':       (12, 6),       # gráfico principal por parte
    'wide':       (12, 5),       # trajetória, distribuição
    'square':     (8, 7),        # heatmap, scatter quadrado
    'tall_pair':  (14, 6),       # par lado a lado
    'multi':      (14, 5),       # small multiples
}


# ============================================================================
# ECONOMIST STYLE — eixo Y removido, variável no título, data labels
# ============================================================================
def economist_style(ax, title=None, subtitle=None,
                    drop_yaxis=True, drop_xaxis=False,
                    ygrid=False, xgrid=False,
                    title_color=None):
    """Aplica estilo Economist ao Axes.

    Padrão: remove eixo Y (apenas título carrega a variável),
    remove spines top/right/left, mantém eixo X com categorias.
    Use data labels para mostrar valores.

    Parâmetros:
      - drop_yaxis: oculta tick labels, ticks e spine esquerdo. Default True.
      - drop_xaxis: idem para eixo X. Default False.
      - ygrid: grid horizontal (útil quando drop_yaxis=True).
      - xgrid: grid vertical (raro).
      - title: título principal (carrega o nome da variável).
      - subtitle: linha em cinza abaixo do título.
    """
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if drop_yaxis:
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', length=0, labelleft=False, pad=0)
        ax.set_ylabel('')
    if drop_xaxis:
        ax.spines['bottom'].set_visible(False)
        ax.tick_params(axis='x', length=0, labelbottom=False, pad=0)
        ax.set_xlabel('')
    if ygrid:
        ax.yaxis.grid(True, color='#d8d3c4', linewidth=0.6, alpha=0.85, zorder=0)
        ax.set_axisbelow(True)
    if xgrid:
        ax.xaxis.grid(True, color='#d8d3c4', linewidth=0.6, alpha=0.85, zorder=0)
        ax.set_axisbelow(True)

    # Título com pesos típicos de The Economist
    if title:
        ax.set_title(
            title,
            loc='left', x=-0.02,
            pad=24 if subtitle else 16,
            fontsize=15, fontweight='bold',
            color=title_color or PALETTE['navy'],
        )
    if subtitle:
        ax.text(
            -0.02, 1.02, subtitle, transform=ax.transAxes,
            ha='left', va='bottom',
            fontsize=11, color=PALETTE['gray_mid'], style='italic',
        )


def add_value_labels(ax, values, positions, offset_y=0.5, fmt='{:.0f}',
                     color=None, fontsize=10, fontweight=700,
                     ha='center', va='bottom'):
    """Helper para data labels acima de barras / dots."""
    if color is None:
        color = PALETTE['navy']
    for x, v in zip(positions, values):
        ax.text(x, v + offset_y, fmt.format(v),
                ha=ha, va=va, color=color, fontsize=fontsize,
                fontweight=fontweight)


# ============================================================================
# Bg / spines clarity helper
# ============================================================================
def set_transparent_bg(fig, ax):
    """Salva com fundo transparente — pra a página cream do site puxar atrás
    via mix-blend-mode: multiply ou simplesmente fluir."""
    fig.patch.set_alpha(0)
    ax.set_facecolor((1, 1, 1, 0))
