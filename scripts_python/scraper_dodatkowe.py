import io
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BASE = "https://fbref.com/en/squads/2232debd/"

# Strona drużyny: tabele zawodników (strzały, bramkarze, czas gry, faule)
STRONA_DRUZYNY = BASE + "Widzew-Lodz-Stats"
TABELE_ZAWODNIKOW = {
    "SoT/90": "widzew_zawodnicy_strzaly",
    "Save%": "widzew_bramkarze",
    "On-Off": "widzew_zawodnicy_czas_gry",
    "Fls": "widzew_zawodnicy_faule",
}

# Logi meczowe Ekstraklasy: dane z każdego meczu osobno
LOGI_MECZOWE = {
    "strzaly": BASE + "2026-2027/matchlogs/c36/shooting/Widzew-Lodz-Match-Logs-Ekstraklasa",
    "bramkarz": BASE + "2026-2027/matchlogs/c36/keeper/Widzew-Lodz-Match-Logs-Ekstraklasa",
    "misc": BASE + "2026-2027/matchlogs/c36/misc/Widzew-Lodz-Match-Logs-Ekstraklasa",
}


def splaszcz(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            dol if gora.startswith("Unnamed") else f"{gora}_{dol}".replace(" ", "_")
            for gora, dol in df.columns
        ]
    return df


def zapisz(df, nazwa):
    df = splaszcz(df)
    df = df[df.iloc[:, 0].astype(str) != df.columns[0]]  # usuń powtórzone nagłówki
    sciezka = f"../data_clean/{nazwa}.csv"
    df.to_csv(sciezka, index=False, encoding="utf-8")
    print(f"  zapisano {sciezka} ({len(df)} wierszy)")


chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

try:
    from webdriver_manager.chrome import ChromeDriverManager

    service = Service(ChromeDriverManager().install())
except Exception:
    service = Service()  # Selenium Manager (np. gdy webdriver_manager nie ma sieci/certyfikatu)

driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(STRONA_DRUZYNY)
    print("Rozwiąż Cloudflare w oknie Chrome, jeśli się pojawi.")
    input(">>> Wciśnij ENTER, gdy widzisz statystyki Widzewa... <<<")

    print("Strona drużyny:")
    html = driver.page_source
    for fraza, nazwa in TABELE_ZAWODNIKOW.items():
        try:
            zapisz(pd.read_html(io.StringIO(html), match=fraza)[0], nazwa)
        except ValueError:
            print(f"  BRAK tabeli z frazą '{fraza}'")

    for nazwa, url in LOGI_MECZOWE.items():
        print(f"Logi meczowe: {nazwa}")
        driver.get(url)
        time.sleep(10)
        html = driver.page_source
        try:
            tabele = pd.read_html(io.StringIO(html), match="Opponent")
        except ValueError:
            print("  BRAK tabel (możliwe Cloudflare)")
            continue
        for i, t in enumerate(tabele[:2]):  # 0 = nasze statystyki, 1 = rywale
            zapisz(t, f"widzew_log_{nazwa}_{'dla' if i == 0 else 'przeciw'}")
finally:
    driver.quit()
