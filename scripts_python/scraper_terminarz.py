from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import io

# Twój zaktualizowany link do sezonu 25/26
url = "https://fbref.com/en/squads/2232debd/Widzew-Lodz-Stats#all_matchlogs"
print(f"Uruchamiam widoczną przeglądarkę dla: {url}")

chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(url)

    print("\n" + "=" * 50)
    print("UWAGA: Przejdź do okna Chrome i rozwiąż Cloudflare (jeśli wyskoczy).")
    print("Gdy strona sezonu 25/26 w pełni się załaduje, wróć tutaj.")
    input(">>> Wciśnij ENTER, aby pobrać terminarz... <<<")
    print("=" * 50 + "\n")

    html = driver.page_source

    if "<table" not in html.lower():
        print("BŁĄD: Brak tabel na stronie.")
    else:
        print("Skanuję stronę w poszukiwaniu tabeli meczowej...")

        # MAGIA PANDASA: Szukamy tylko tej tabeli, która ma kolumnę "Attendance" (frekwencja)
        tabele = pd.read_html(io.StringIO(html), match="Attendance")

        if len(tabele) > 0:
            # Pandas zwraca listę pasujących tabel, więc bierzemy pierwszą (i jedyną) z dopasowań
            df = tabele[0]
            print("\nPodgląd 5 pierwszych wierszy pobranego terminarza:")
            print(df.head())

            sciezka_zapisu = "../data_raw/widzew_terminarz_czysty.csv"
            df.to_csv(sciezka_zapisu, index=False, encoding='utf-8')
            print(f"\nSukces! Terminarz z sezonu 25/26 zapisano w: {sciezka_zapisu}")
        else:
            print("BŁĄD: Nie znaleziono tabeli 'Scores & Fixtures' z frekwencją.")

except Exception as e:
    print(f"\nWystąpił błąd: {e}")
finally:
    driver.quit()