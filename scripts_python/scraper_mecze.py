from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import io

url = "https://fbref.com/en/squads/2232debd/Widzew-Lodz-Stats"
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
    print("UWAGA: Przejdź do otwartego okna Chrome.")
    print("Jeśli widzisz zabezpieczenie Cloudflare, rozwiąż je.")
    print("Gdy zobaczysz na ekranie właściwe statystyki Widzewa, wróć tutaj.")
    input(">>> Wciśnij ENTER tutaj w konsoli, aby kontynuować pobieranie... <<<")
    print("=" * 50 + "\n")

    html = driver.page_source

    if "<table" not in html.lower():
        print("BŁĄD: Na stronie nadal nie ma tabel.")
    else:
        print("Zczytuję kod strony! Przetwarzam...")

        tabele = pd.read_html(io.StringIO(html))

        print(f"Znaleziono {len(tabele)} tabel na stronie.")

        df = tabele[0]
        print("\nPodgląd 5 pierwszych wierszy pobranej tabeli:")
        print(df.head())

        sciezka_zapisu = "../data_raw/widzew_surowe_dane.csv"
        df.to_csv(sciezka_zapisu, index=False, encoding='utf-8')
        print(f"\nSukces! Dane zapisane w: {sciezka_zapisu}")

except Exception as e:
    print(f"\nWystąpił błąd: {e}")
finally:
    driver.quit()