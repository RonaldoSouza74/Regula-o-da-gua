"""Balanço hídrico mensal simplificado da UHE Belo Monte (ilustrativo).

Entradas (ver Tabela 3 do artigo para fontes):
  - vazões naturais médias mensais (m3/s): USP/UFAM (2021) [jan-out; série 1971-2014]
    e CBG/AGB (2024) [nov-dez]
  - hidrogramas A e B (m3/s): ANA (2014), Anexo III; Norte Energia (2012)
  - vazão máxima turbinada: 13.900 m3/s (casa de força principal) e 2.277 m3/s (complementar),
    ANA (2009) NT 129/2009
  - potência instalada: 11.000 MW (principal) e 233,1 MW (complementar)
Simplificações: produtibilidade constante; passo mensal; sem perdas por indisponibilidade,
sem variação de queda líquida, sem restrições de transmissão.
"""
import json
import numpy as np

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
DIAS = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
QNAT = np.array([8600, 13700, 18800, 19500, 14700, 6800, 3000, 1700, 1100, 1200, 1942, 4036.0])
HID_A = np.array([1100, 1600, 2500, 4000, 1800, 1200, 1000, 900, 750, 700, 800, 900.0])
HID_B = np.array([1100, 1600, 4000, 8000, 4000, 2000, 1200, 900, 750, 700, 800, 900.0])

QMAX_P = 13900.0           # m3/s, casa de força principal
QMAX_C = 2277.0            # m3/s, casa de força complementar
PROD_P = 11000.0 / QMAX_P  # MW por m3/s
PROD_C = 233.1 / QMAX_C    # MW por m3/s
QMIN_CANAL = 300.0         # m3/s, outorga (reservatório dos canais)
AREA_KM2 = 516.0           # km2 a NA 97,00 m (Projeto Básico)
AREA_INT_KM2 = 130.0
GF_P, GF_C = 4419.0, 152.0  # MWmed


def simula(qnat, hid, fator_hidro=1.0):
    q = qnat * fator_hidro
    tvr = np.minimum(hid, q)
    canal = np.minimum(np.maximum(q - tvr, 0.0), QMAX_P)
    vert = q - tvr - canal
    p_p = PROD_P * canal
    p_c = PROD_C * np.minimum(tvr, QMAX_C)
    return dict(q=q, tvr=tvr, canal=canal, vert=vert, p_p=p_p, p_c=p_c, p=p_p + p_c)


def medio(x):
    return float(np.sum(x * DIAS) / np.sum(DIAS))


def resumo(s):
    return dict(
        mwmed_principal=medio(s["p_p"]),
        mwmed_compl=medio(s["p_c"]),
        mwmed_total=medio(s["p"]),
        gwh_ano=float(np.sum(s["p"] * DIAS * 24) / 1000),
        tvr_medio=medio(s["tvr"]),
        tvr_pct_nat=medio(s["tvr"]) / medio(s["q"]) * 100,
        vert_medio=medio(s["vert"]),
        meses_canal_abaixo_300=[MESES[i] for i in range(12) if s["canal"][i] < QMIN_CANAL - 1e-9],
    )


out = {}
for nome, f in [("media", 1.0), ("seca_-30%", 0.7), ("umida_+30%", 1.3)]:
    for h, hid in [("A", HID_A), ("B", HID_B)]:
        s = simula(QNAT, hid, f)
        out[f"{nome}|{h}"] = resumo(s)
        out[f"{nome}|{h}"]["mensal_mw"] = [round(float(v), 1) for v in s["p"]]
        out[f"{nome}|{h}"]["mensal_canal"] = [round(float(v), 1) for v in s["canal"]]
        out[f"{nome}|{h}"]["mensal_vert"] = [round(float(v), 1) for v in s["vert"]]

# estatísticas do regime natural
out["qnat_medio"] = medio(QNAT)
out["razao_abr_set"] = float(QNAT[3] / QNAT[8])
out["agua_livre_m3s"] = [round(float(max(q - QMAX_P, 0)), 0) for q in QNAT]

# curva de compromisso: escala k sobre o pulso mar-jun do hidrograma B
ks = np.linspace(0.4, 1.0, 25)
curva = []
base = resumo(simula(QNAT, HID_B))["mwmed_total"]
for k in ks:
    h = HID_B.copy()
    h[2:6] = np.maximum(HID_B[2:6] * k, np.minimum(HID_B[2:6], 700))
    r = resumo(simula(QNAT, h))
    curva.append(dict(k=float(k), abril=float(h[3]), ganho_mwmed=r["mwmed_total"] - base,
                      tvr_medio=r["tvr_medio"], tvr_pct=r["tvr_pct_nat"]))
out["curva_k"] = curva

# alavancas (ganho médio anual de energia frente ao hidrograma B, ano médio)
a = resumo(simula(QNAT, HID_A))["mwmed_total"] - base
h = HID_B.copy(); h[7:11] = np.maximum(h[7:11] - 100, 0)
sec = resumo(simula(QNAT, h))["mwmed_total"] - base
h2 = HID_B.copy(); h2[3] = 4000  # só reduzir o pico de abril ao patamar do A
abr = resumo(simula(QNAT, h2))["mwmed_total"] - base
ENERGIA_HM3 = PROD_P * 1e6 / 3600  # MWh por hm3 (1 hm3 a 1 m3/s -> 277,8 h)
arm_1m_gwh = AREA_KM2 * 1.0 * ENERGIA_HM3 / 1000  # km2*m = hm3
out["alavancas"] = dict(
    hid_A_em_vez_de_B=a,
    reduzir_pico_abril_para_4000=abr,
    tvr_menos_100_ago_nov=sec,
    armazenar_1m_516km2_mwmed_equiv=arm_1m_gwh * 1000 / (8760),
)
out["armazenamento"] = dict(
    mwh_por_hm3=ENERGIA_HM3,
    gwh_1m=arm_1m_gwh,
    gwmes_1m=arm_1m_gwh / 730.0,
    hm3_1m=AREA_KM2,
    gwh_2m=2 * arm_1m_gwh,
)
# déficit de energia no período seco (ago-nov) frente à média anual (cenário B, ano médio)
sB = simula(QNAT, HID_B)
pm = medio(sB["p_p"])
deficit_mw_meses = float(np.sum((pm - sB["p_p"][7:11])))  # MW-mês (aprox., meses iguais)
out["deficit_seco_gwmes"] = deficit_mw_meses / 1000
out["media_ago_nov_mw"] = float(np.mean(sB["p_p"][7:11]))
# volume para elevar em 1000 m3/s a vazão do canal em ago-nov (122 dias)
vol_km3 = 1000 * 122 * 86400 / 1e9
out["volume_1000m3s_ago_nov_km3"] = vol_km3
# modulação diária no período seco (set): armazenar 20 h, turbinar 4 h
q_set = float(sB["canal"][8])
qp = q_set * 24 / 4
out["ponta_set"] = dict(q_medio=q_set, q_ponta=qp, mw_ponta=PROD_P * qp,
                         vol_hm3=(qp - q_set) * 4 * 3600 / 1e6,
                         desnivel_m_516=(qp - q_set) * 4 * 3600 / 1e6 / AREA_KM2,
                         desnivel_m_130=(qp - q_set) * 4 * 3600 / 1e6 / AREA_INT_KM2)
# razão TVR/natural por mês
out["razao_tvr_nat_B"] = [round(float(b / q * 100), 1) for b, q in zip(HID_B, QNAT)]
out["razao_tvr_nat_A"] = [round(float(b / q * 100), 1) for b, q in zip(HID_A, QNAT)]
out["prod_mw_por_m3s"] = PROD_P

json.dump(out, open("resultados_modelo.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k not in ("curva_k",)}, indent=1, ensure_ascii=False)[:9000])
