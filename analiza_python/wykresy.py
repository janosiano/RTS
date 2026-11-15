"""Generuje wykresy do analiza_wynikow.md z plików w data_clean/.

Uruchomienie (z dowolnego miejsca):  python analiza_python/wykresy.py
Wykresy trafiają do folderu wykresy/.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DANE = ROOT / "data_clean"
WYKRESY = ROOT / "wykresy"
WYKRESY.mkdir(exist_ok=True)

KOLOR = {"W": "#2e7d32", "D": "#f9a825", "L": "#c62828"}
PUNKTY = {"W": 3, "D": 1, "L": 0}
plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})

mecze = pd.read_csv(DANE / "widzew_terminarz_czysty.csv")
mecze = mecze[mecze["Result"].isin(PUNKTY)].copy()
mecze["Kolejka"] = mecze["Round"].str.extract(r"(\d+)").astype(int)
mecze["Punkty"] = mecze["Result"].map(PUNKTY)
mecze["Skumulowane"] = mecze["Punkty"].cumsum()


def zapisz(nazwa):
    plt.tight_layout()
    plt.savefig(WYKRESY / nazwa)
    plt.close()
    print("zapisano", WYKRESY / nazwa)


# 1. Wyniki po kolejkach i punkty narastająco
fig, ax = plt.subplots(figsize=(9, 4.5))
# porażki mają 0 pkt, więc rysujemy je jako niski słupek, żeby były widoczne
ax.bar(mecze["Kolejka"], mecze["Punkty"].clip(lower=0.15), color=mecze["Result"].map(KOLOR))
ax.set_ylabel("Punkty w meczu")
ax.set_xlabel("Kolejka")
ax.set_xticks(mecze["Kolejka"])
ax.set_yticks([0, 1, 3])
ax.set_yticklabels(["0 (L)", "1 (D)", "3 (W)"])
ax2 = ax.twinx()
ax2.plot(mecze["Kolejka"], mecze["Skumulowane"], color="black", marker="o")
ax2.set_ylabel("Punkty narastająco")
ax2.spines["top"].set_visible(False)
ax.set_title("Widzew Łódź: punkty po kolejkach (zielony W, żółty D, czerwony L)")
zapisz("01_punkty_po_kolejkach.png")

# 2. Bramki strzelone i stracone
fig, ax = plt.subplots(figsize=(9, 4.5))
szer = 0.4
ax.bar(mecze["Kolejka"] - szer / 2, mecze["GF"], szer, label="Strzelone", color="#1565c0")
ax.bar(mecze["Kolejka"] + szer / 2, mecze["GA"], szer, label="Stracone", color="#ef6c00")
ax.set_xticks(mecze["Kolejka"])
ax.set_xlabel("Kolejka")
ax.set_ylabel("Bramki")
ax.set_title(f"Bramki w meczu (razem {int(mecze['GF'].sum())}:{int(mecze['GA'].sum())})")
ax.legend()
zapisz("02_bramki.png")

# 3. Posiadanie piłki a wynik
fig, ax = plt.subplots(figsize=(7, 5))
for wynik, grupa in mecze.groupby("Result"):
    ax.scatter(grupa["Poss"], grupa["GF"] - grupa["GA"], s=90, color=KOLOR[wynik], label=wynik)
ax.axvline(50, color="grey", linestyle="--", linewidth=1)
ax.axhline(0, color="grey", linewidth=1)
ax.set_xlabel("Posiadanie piłki (%)")
ax.set_ylabel("Bilans bramek w meczu")
ax.set_title("Posiadanie piłki a wynik (brak wygranych przy >= 50%)")
ax.legend(title="Wynik")
zapisz("03_posiadanie_a_wynik.png")

# 4. Punkty na mecz według ustawienia
ust = mecze.groupby("Formation").agg(mecze=("Punkty", "size"), ppm=("Punkty", "mean")).sort_values("ppm")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh([f"{u} ({int(r.mecze)} m.)" for u, r in ust.iterrows()], ust["ppm"], color="#455a64")
ax.set_xlabel("Punkty na mecz")
ax.set_title("Skuteczność według ustawienia (mała próba!)")
zapisz("04_ustawienia.png")

# 5. Strzały i celne strzały zawodników
def tylko_zawodnicy(df):
    """Usuwa wiersze zbiorcze FBref (Squad Total, Opponent Total)."""
    return df[~df["Player"].str.contains("Total", na=False)]


strz = tylko_zawodnicy(pd.read_csv(DANE / "widzew_zawodnicy_strzaly.csv"))
strz = strz[strz["Standard_Sh"] > 0].sort_values("Standard_Sh").tail(12)
fig, ax = plt.subplots(figsize=(8, 5.5))
poz = range(len(strz))
ax.barh(poz, strz["Standard_Sh"], color="#b0bec5", label="Strzały")
ax.barh(poz, strz["Standard_SoT"], color="#1565c0", label="Celne")
for i, g in enumerate(strz["Standard_Gls"]):
    ax.text(strz["Standard_Sh"].iloc[i] + 0.3, i, f"{int(g)} goli", va="center", fontsize=8)
ax.set_yticks(list(poz))
ax.set_yticklabels(strz["Player"])
ax.legend(loc="lower right")
ax.set_title("Najwięcej strzałów w drużynie (z liczbą goli)")
zapisz("05_strzaly_zawodnikow.png")

# 6. Kartki
faule = pd.read_csv(DANE / "widzew_zawodnicy_faule.csv")
zolte_druzyna = int(faule.loc[faule["Player"] == "Squad Total", "Performance_CrdY"].iloc[0])
kart_wszyscy = tylko_zawodnicy(faule)
kart = kart_wszyscy[kart_wszyscy["Performance_CrdY"] > 0].sort_values("Performance_CrdY").tail(12)
fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(kart["Player"], kart["Performance_CrdY"], color="#f9a825")
ax.set_xlabel("Żółte kartki")
ax.set_xticks(range(0, int(kart["Performance_CrdY"].max()) + 1))
ax.set_title(f"Żółte kartki zawodników (drużyna razem: {zolte_druzyna})")
zapisz("06_kartki.png")
