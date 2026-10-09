import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import FuncFormatter
TH = FuncFormatter(lambda v, p: f"{v:,.0f}".replace(",", "."))

R = json.load(open("/home/user/Regula-o-da-gua/artigo/analise/resultados_modelo.json"))
OUT = "/home/user/Regula-o-da-gua/artigo/figuras/"
rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.spines.top": False,
                 "axes.spines.right": False, "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b",
                 "xtick.color": "#52514e", "ytick.color": "#52514e", "figure.dpi": 200,
                 "axes.grid": True, "grid.color": "#e3e2dd", "grid.linewidth": 0.6, "axes.axisbelow": True})
BLUE, ORANGE, AQUA, GREY, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#4a3aa7", "#e34948"
def br(v, d=1):
    t = f"{v:,.{d}f}"
    return t.replace(",", "X").replace(".", ",").replace("X", ".")

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# ---------- Figura 1: capacidade hidrelétrica 2015 -> atual ----------
anos = [2015, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
mw = [91650, 96925, 104139, 109058, 109271, 109350, 109807, 109922, 109922]
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.8), gridspec_kw={"width_ratios": [1.35, 1]})
a = ax[0]
bars = a.bar([str(y) for y in anos], [m / 1000 for m in mw], color=BLUE, width=0.65)
for b, m in zip(bars, mw):
    a.text(b.get_x() + b.get_width() / 2, m / 1000 + 1.2, br(m/1000), ha="center", fontsize=8, color="#0b0b0b")
a.set_ylabel("Capacidade instalada hidrelétrica (GW)")
a.set_title("(a) Evolução 2015–2024", loc="left", fontsize=10, fontweight="bold")
a.text(0.0, -0.2, "2017 sem dado verificado nesta pesquisa", transform=a.transAxes, fontsize=7.5, color="#52514e")
a.set_ylim(0, 140)
a.text(-0.4, 128, "+18,3 GW (+20%) entre 2015 e 2024", fontsize=8.5, color=ORANGE, ha="left")
b = ax[1]
h15, t15 = 91.7, 140.9
h26, t26 = 111.2, 215.9
x = np.arange(2)
hid = [h15, h26]; oth = [t15 - h15, t26 - h26]
b.bar(x, hid, color=BLUE, width=0.55, label="Hidrelétricas (UHE+PCH+CGH)")
b.bar(x, oth, bottom=hid, color="#c3c2b7", width=0.55, label="Demais fontes")
b.set_xticks(x); b.set_xticklabels(["Dez/2015", "Jan/2026"])
for i in range(2):
    b.text(i, hid[i] / 2, f"{br(hid[i])} GW\n({br(hid[i]/(hid[i]+oth[i])*100)}%)", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    b.text(i, hid[i] + oth[i] + 3, f"{br(hid[i]+oth[i])} GW", ha="center", fontsize=8.5)
b.set_ylim(0, 245); b.set_ylabel("Capacidade instalada total (GW)")
b.set_title("(b) Participação da fonte hídrica", loc="left", fontsize=10, fontweight="bold")
b.legend(loc="upper left", fontsize=7.5, frameon=False)
fig.tight_layout(); fig.savefig(OUT + "fig01_capacidade_hidreletrica_2015_atual.png"); plt.close(fig)

# ---------- Figura 2: armazenamento x capacidade ----------
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.8))
a = ax[0]
ear15 = 205.002 + 19.873 + 51.860
ear21 = 203.567 + 19.897 + 51.602
idx = {"Capacidade hidrelétrica (GW)": (100, 109350 / 91650 * 100), "EARmáx SE/CO+S+NE (GWmês)": (100, ear21 / ear15 * 100)}
cols = [BLUE, ORANGE]
for (lab, (v0, v1)), c in zip(idx.items(), cols):
    a.plot([2015, 2021], [v0, v1], marker="o", color=c, lw=2.2, ms=7)
    a.text(2021.07, v1, br(v1), color="#0b0b0b", va="center", fontsize=9)
a.text(2015.05, 118, "Capacidade hidrelétrica (GW)", color=BLUE, fontsize=8.5, fontweight="bold")
a.text(2015.05, 94.5, "Energia armazenável máxima (EARmáx)\nSE/CO + S + NE", color=ORANGE, fontsize=8.5, fontweight="bold")
a.set_xlim(2014.8, 2021.8); a.set_ylim(88, 126); a.set_xticks([2015, 2021])
a.set_ylabel("Índice (2015 = 100)")
a.set_title("(a) Capacidade cresce; armazenamento não", loc="left", fontsize=10, fontweight="bold")
b = ax[1]
yrs = [2002, 2021, 2025]; gr = [6.5, 5.8, 5.3]
b.plot(yrs, gr, color=VIOLET, lw=2.2, marker="o", ms=7)
for xv, yv in zip(yrs, gr):
    b.text(xv, yv + 0.12, br(yv), ha="center", fontsize=9)
b.set_ylim(4.6, 7.0); b.set_xlim(1999, 2028); b.set_xticks(yrs)
b.set_xticklabels(["2002", "2021", "2025*"])
b.text(1999.5, 4.68, "* projeção do PEN 2021", fontsize=7.5, color="#52514e")
b.set_ylabel("Grau de regularização do SIN (meses)")
b.set_title("(b) Regularização relativa do SIN", loc="left", fontsize=10, fontweight="bold")
fig.tight_layout(); fig.savefig(OUT + "fig02_armazenamento_regularizacao.png"); plt.close(fig)

# ---------- Figura 3: vazões naturais x hidrogramas A e B ----------
QNAT = [8600, 13700, 18800, 19500, 14700, 6800, 3000, 1700, 1100, 1200, 1942, 4036]
HA = [1100, 1600, 2500, 4000, 1800, 1200, 1000, 900, 750, 700, 800, 900]
HB = [1100, 1600, 4000, 8000, 4000, 2000, 1200, 900, 750, 700, 800, 900]
fig, ax = plt.subplots(figsize=(8.2, 4.1))
xs = np.arange(12)
ax.fill_between(xs, QNAT, color="#cfe0f6", label="Vazão natural média mensal (1971–2014)")
ax.plot(xs, QNAT, color=BLUE, lw=2)
ax.step(xs, HB, where="mid", color=ORANGE, lw=2.2, label="Hidrograma B (TVR)")
ax.step(xs, HA, where="mid", color=AQUA, lw=2.2, label="Hidrograma A (TVR)")
ax.axhline(13900, color=GREY, ls="--", lw=1)
ax.text(11.4, 14300, "Turbinamento máx. casa de força principal: 13.900 m³/s", ha="right", fontsize=8, color="#52514e")
ax.annotate("Abril: 19.500 (natural)\n8.000 (B) | 4.000 (A)", xy=(3, 19500), xytext=(5.1, 20800), fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color=GREY))
ax.set_xticks(xs); ax.set_xticklabels(MESES); ax.set_ylabel("Vazão (m³/s)"); ax.set_ylim(0, 23500); ax.yaxis.set_major_formatter(TH)
ax.legend(loc="upper right", fontsize=8, frameon=False, bbox_to_anchor=(1.0, 0.86))
fig.tight_layout(); fig.savefig(OUT + "fig03_vazoes_naturais_hidrogramas.png"); plt.close(fig)

# ---------- Figura 4: geração simulada A x B ----------
pA = R["media|A"]["mensal_mw"]; pB = R["media|B"]["mensal_mw"]
fig, ax = plt.subplots(figsize=(8.2, 4.1))
w = 0.38
ax.bar(xs - w/2, pB, w, color=ORANGE, label=f"Hidrograma B (média {R['media|B']['mwmed_total']:,.0f} MWmed)".replace(",", "."))
ax.bar(xs + w/2, pA, w, color=AQUA, label=f"Hidrograma A (média {R['media|A']['mwmed_total']:,.0f} MWmed)".replace(",", "."))
ax.axhline(11233.1, color=GREY, ls="--", lw=1); ax.text(11.45, 11450, "Potência instalada 11.233 MW", ha="right", fontsize=8, color="#52514e")
ax.axhline(4571, color=VIOLET, ls=":", lw=1.4); ax.text(11.45, 4770, "Garantia física 4.571 MWmed", ha="right", fontsize=8, color=VIOLET)
ax.set_xticks(xs); ax.set_xticklabels(MESES); ax.set_ylabel("Potência média mensal simulada (MW)"); ax.set_ylim(0, 12800); ax.yaxis.set_major_formatter(TH)
ax.legend(loc="upper center", fontsize=8, frameon=False, ncol=2)
fig.tight_layout(); fig.savefig(OUT + "fig04_geracao_simulada_A_B.png"); plt.close(fig)

# ---------- Figura 5: curva de compromisso e alavancas ----------
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.9), gridspec_kw={"width_ratios": [1.1, 1]})
c = R["curva_k"]
xa = [d["abril"] for d in c]; yg = [d["ganho_mwmed"] for d in c]
a = ax[0]
a.plot(xa, yg, color=BLUE, lw=2.4, label="Pulso mar–jun do hidrograma B escalado por k (0,4–1,0)")
a.legend(loc="upper right", fontsize=7.5, frameon=False)
a.scatter([8000], [0], color=ORANGE, zorder=5, s=45); a.text(7850, 14, "B (em vigor)", ha="right", fontsize=8.5, color=ORANGE)
a.scatter([4000], [R["alavancas"]["reduzir_pico_abril_para_4000"]], color=GREEN if False else AQUA, zorder=5, s=45)
a.text(4150, R["alavancas"]["reduzir_pico_abril_para_4000"] - 55, "só abril reduzido a 4.000 m³/s\n(demais meses = B): +156 MWmed", fontsize=8, ha="left")
a.set_xlabel("Vazão do TVR em abril – pulso de cheia (m³/s)"); a.set_ylabel("Ganho de energia vs. B (MWmed)")
a.set_title("(a) Pulso de cheia × energia", loc="left", fontsize=10, fontweight="bold")
a.set_xlim(3000, 8400); a.xaxis.set_major_formatter(TH)
b = ax[1]
lab = ["Hidrograma A\nno lugar de B", "Pico de abril\n8.000→4.000", "TVR −100 m³/s\nago–nov", "Armazenar 1 m\n(516 km²)/ano", "Modulação diária\n(ponta)"]
val = [R["alavancas"]["hid_A_em_vez_de_B"], R["alavancas"]["reduzir_pico_abril_para_4000"],
       R["alavancas"]["tvr_menos_100_ago_nov"], R["alavancas"]["armazenar_1m_516km2_mwmed_equiv"], 0]
cols = [ORANGE, ORANGE, BLUE, BLUE, BLUE]
yy = np.arange(len(lab))[::-1]
b.barh(yy, val, color=cols, height=0.6)
for y, v in zip(yy, val):
    b.text(v + 6, y, f"{v:,.0f}".replace(",", ".") + (" (potência, não energia)" if v == 0 else ""), va="center", fontsize=8)
b.set_yticks(yy); b.set_yticklabels(lab, fontsize=8); b.set_xlim(0, 480)
b.set_xlabel("Ganho médio anual de energia (MWmed)")
b.set_title("(b) Alavancas de flexibilização", loc="left", fontsize=10, fontweight="bold")
fig.tight_layout(); fig.savefig(OUT + "fig05_compromisso_alavancas.png"); plt.close(fig)

# ---------- Figura 6: vazões mínimas referenciadas (log) ----------
itens = [
    ("Machadinho (Uruguai) – ictiofauna, abaixo da cota 473 m", 18),
    ("Serra da Mesa (Tocantins) – dez–mai (Res. ANA 70/2021)", 100),
    ("Itá (Uruguai) – inventário ONS 2008", 150),
    ("Santa Cecília/Guandu (Paraíba do Sul) – jusante, cond. favorável", 90),
    ("Santa Cecília (Paraíba do Sul) – vazão-objetivo normal", 190),
    ("Serra da Mesa (Tocantins) – jun–nov", 300),
    ("Belo Monte – reservatório dos canais (outorga)", 300),
    ("Sobradinho/Xingó (São Francisco) – faixa de restrição", 700),
    ("Belo Monte – TVR, outubro (hidrogramas A e B)", 700),
    ("Sobradinho/Xingó (São Francisco) – faixa de atenção", 800),
    ("Capivara (Paranapanema) – ONS 2021", 147),
    ("Tucuruí (Tocantins) – ONS 2022", 2000),
    ("Jupiá (Paraná) – proposta ANA CP 10/2025", 3300),
    ("Porto Primavera (Paraná) – temporária 2024-25", 3900),
    ("Porto Primavera (Paraná) – permanente declarada", 4600),
]
itens.sort(key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(8.8, 5.0))
yy = np.arange(len(itens))
colors = [ORANGE if "Belo Monte" in n else BLUE for n, _ in itens]
ax.barh(yy, [v for _, v in itens], color=colors, height=0.62)
ax.set_xscale("log"); ax.set_xlim(8, 12000)
for y, (n, v) in zip(yy, itens):
    ax.text(v * 1.08, y, f"{v:,}".replace(",", "."), va="center", fontsize=8)
ax.set_yticks(yy); ax.set_yticklabels([n for n, _ in itens], fontsize=7.8)
ax.set_xlabel("Vazão defluente mínima (m³/s, escala logarítmica)")
fig.tight_layout(); fig.savefig(OUT + "fig06_vazoes_minimas_referenciadas.png"); plt.close(fig)
print("ok")
