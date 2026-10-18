import pandas as pd

sciezka_surowa = "../data_raw/widzew_surowe_dane.csv"
sciezka_czysta = "../data_clean/widzew_czyste.csv"

print("Wczytuję surowe dane z folderu data_raw...")

df = pd.read_csv(sciezka_surowa, header=[0, 1])

# 1. Spłaszczanie podwójnych nagłówków (MultiIndex)
nowe_kolumny = []
for poziom1, poziom2 in df.columns:
    if "Unnamed" in poziom1:
        # Jeśli górny nagłówek jest pusty, bierzemy tylko dolny (np. 'Player', 'Age')
        nowe_kolumny.append(poziom2)
    else:
        # Jeśli obie mają nazwy, łączymy je (np. 'Playing Time_Min') i usuwamy spacje
        nowa_nazwa = f"{poziom1}_{poziom2}".replace(" ", "_")
        nowe_kolumny.append(nowa_nazwa)

df.columns = nowe_kolumny

# 2. Usuwanie "śmieciowych" wierszy
# FBref co 20 wierszy powtarza nagłówek, więc usuwamy wiersze, gdzie w kolumnie Player jest słowo 'Player'
df = df[df['Player'] != 'Player']

# 3. Czyszczenie wartości pustych (NaN)
# Jeśli zawodnik nie ma statystyki (bo nie grał), wstawiamy 0, zamiast pustego znaku, aby SQL to zrozumiał
df = df.fillna(0)

print("\nPodgląd 5 pierwszych wierszy po wyczyszczeniu:")
print(df.head())
print(f"\nZostało {len(df)} wierszy gotowych do wgrania do bazy.")

# 4. Zapis do folderu data_clean (gotowe dla bazy SQL)
df.to_csv(sciezka_czysta, index=False, encoding='utf-8')
print(f"\nSukces! Wyczyszczone dane zapisano w: {sciezka_czysta}")