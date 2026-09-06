# S&P 500 — base rate'y obsunięć

Raport odświeżany automatycznie 1. dnia każdego miesiąca. Otwierasz link, patrzysz, zamykasz.

## Konfiguracja przez telefon (bez terminala)

1. **github.com** → zaloguj się → `+` → **New repository**
   Nazwa dowolna, widoczność **Private**, zaznacz *Add a README*.

2. W repo: **Add file → Create new file**
   - nazwa: `spx_report.py`, wklej zawartość pliku → **Commit**
   - nazwa: `.github/workflows/raport.yml`, wklej zawartość → **Commit**
     (ukośniki w nazwie same tworzą foldery)

3. **Actions** → zaakceptuj włączenie → wybierz *Raport miesięczny*
   → **Run workflow**. Poczekaj ~1 min.

4. **Settings → Pages** → Source: *Deploy from a branch*
   → gałąź `main`, folder `/docs` → **Save**.

5. Po chwili raport jest pod `https://TWOJANAZWA.github.io/NAZWA-REPO/`
   Dodaj do ekranu głównego telefonu.

Repo prywatne + GitHub Pages wymaga płatnego planu. Jeśli masz darmowy — ustaw repo
jako **Public**. Nie ma tu żadnych twoich danych poza kwotą wpłaty; jeśli i to ci
przeszkadza, ustaw `BAZOWA_WPLATA = 1` i traktuj wynik jako mnożnik.

## Zanim odpalisz

Edytuj na górze `spx_report.py`:

```python
BAZOWA_WPLATA = 500
REGULA_DCA = [(0, 1.0), (-10, 2.0), (-20, 3.0), (-30, 4.0)]
```

Ustaw to **teraz**, zanim zobaczysz aktualne obsunięcie. Jeśli ustawisz po — to nie
jest reguła, tylko uzasadnienie decyzji, którą i tak podjąłeś.

## Czego to nie robi

Nie prognozuje. Nie mówi, kiedy kupić. Nie wie, czy dołek się pogłębi.
Pokazuje, jak często w przeszłości spadek o X% szedł dalej — przy n, które przy
głębokich progach jest jednocyfrowe.
