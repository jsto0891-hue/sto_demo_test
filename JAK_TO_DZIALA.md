# Jak to działa i co masz robić

## Co masz teraz

- **Repo:** https://github.com/jsto0891-hue/sto_demo_test (publiczne, darmowe)
- **Raport obsunięcia S&P 500:** https://jsto0891-hue.github.io/sto_demo_test/
- **Skaner fundamentalny:** https://jsto0891-hue.github.io/sto_demo_test/skaner.html
- **Log transakcji (prywatny, Google Sheets):** https://docs.google.com/spreadsheets/d/1EnYbpltjsh9_zfV0XPBpYNt77FgehNXNKV1u3Fdy_co/edit

Dodaj obie strony (raport + skaner) do ekranu głównego telefonu — to Twój codzienny/comiesięczny interfejs. Nic więcej nie musisz odpalać ręcznie.

## Co dzieje się samo

- **1. dnia każdego miesiąca, 07:00 UTC** — GitHub automatycznie przelicza raport obsunięcia i aktualizuje stronę.
- **3. dnia każdego miesiąca, 06:00 UTC** — GitHub automatycznie skanuje ~500 spółek S&P 500 + GPW i aktualizuje listę tych, które przeszły filtr.

Zero Twojej pracy przy tym. Nawet jeśli nie dotkniesz telefonu przez miesiąc, dane i tak się zaktualizują.

## Co robisz Ty (wg PLAN.md)

- **1. dnia miesiąca:** otwierasz link do raportu, patrzysz na kwotę do wpłaty wg Twojej reguły DCA, robisz przelew. 2 minuty.
- **3. dnia miesiąca:** otwierasz skaner, jeśli lista niepusta — wybierasz max 1 spółkę do researchu (checklista w `PLAN.md`, punkt 3).
- **Kupno:** dopiero tydzień po znalezieniu, max 1 pozycja/miesiąc, max 5% portfela na spółkę.
- **Każda transakcja:** zapisujesz w arkuszu Google (link wyżej) — data, ticker, kwota, cena, teza, falsyfikator.
- **Reszta miesiąca:** nic. To jest część planu, nie jego brak.

## Bezpieczeństwo — co jest publiczne, a co nie

- Kod (`skaner.py`, `spx_report.py`) i wygenerowane raporty (ceny, F-score spółek) — **publiczne, i to jest OK**, bo to tylko dane rynkowe, zero Twoich informacji.
- Log transakcji — **prywatny, w Google Sheets**, nie w repo. Nikt poza Tobą go nie widzi.
- Brak haseł, kluczy API i danych logowania gdziekolwiek w repo.
- Uprawnienia GitHub Actions ograniczone tylko do tego jednego repozytorium.

## Jeśli chcesz coś zmienić

- **Kwotę `BAZOWA_WPLATA`:** edytuj na GitHubie plik `spx_report.py` (ikona ołówka), zmień liczbę na górze pliku, zatwierdź commit. Następny przebieg (1. dnia miesiąca) użyje nowej wartości. Obecnie jest tam placeholder `500` — ustaw realną kwotę, zanim zaczniesz się kierować raportem.
- **Progi skanera** (F-Score, FCF yield, dług/EBITDA): edytujesz `skaner.py` tak samo — ale rób to tylko między przebiegami, z uzasadnieniem, nigdy w reakcji na akurat zobaczony wynik (patrz `PLAN.md`, punkt 4).
- **Powiadomienia o awarii workflow:** zainstaluj apkę GitHub Mobile, zaloguj się na konto `jsto0891-hue`, Settings → Notifications → włącz Actions.

## Co robić, jeśli coś nie zadziała

Wejdź na zakładkę **Actions** w repo — czerwony ✗ przy którymkolwiek workflow oznacza błąd. Kliknij w niego, rozwiń krok, który się wysypał, i wklej mi treść błędu — naprawimy to tak jak dziś (np. jeśli Yahoo Finance albo Wikipedia znowu zmienią coś po swojej stronie).
