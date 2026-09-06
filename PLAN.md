# Plan działania

Dwa narzędzia, jeden kalendarz, kilka twardych reguł. Nic poza tym.

---

## 1. Czego szukają narzędzia

### Raport miesięczny (`spx_report.py`)
Odpowiada na jedno pytanie: **ile mam wpłacić w tym miesiącu.**

Liczy obsunięcie S&P 500 od szczytu i podstawia je do reguły, którą zapisałeś
z góry. Tabela base rate'ów jest kontekstem, nie sygnałem — pokazuje, jak często
historycznie spadek o tyle szedł głębiej.

Nie prognozuje. Nie mówi, kiedy kupić. Mówi, ile.

### Skaner (`skaner.py`)
Odpowiada na jedno pytanie: **które spółki spełniają cztery kryteria liczbowe.**

| Kryterium | Próg | Co bada |
|---|---|---|
| F-Score Piotroskiego | ≥ 7/9 | jakość bilansu i rentowności, trend rok do roku |
| FCF yield | ≥ 5% | ile gotówki firma generuje względem swojej wyceny |
| Dług netto / EBITDA | ≤ 3× | czy przetrwa gorszy rok |
| Kapitalizacja | ≥ 300 mln | płynność, odsiew mikrospółek |

Kolumna „od szczytu 3l" to **kontekst, nie kryterium**. Spółka może przejść filtr
przy szczycie wszech czasów.

### Czego skaner nie widzi

To jest ważniejsze niż to, co widzi:

- pozwy, odejścia zarządu, zmiany regulacyjne
- strukturalny schyłek branży
- czy FCF jest powtarzalny, czy pochodzi ze sprzedaży aktywów
- księgowość naciąganą, ale legalną

**Pułapka wartości wygląda w liczbach identycznie jak okazja.** Odróżnienie ich
to twoja praca, nie skanera. Punkt 3 poniżej jest o tym.

---

## 2. Kalendarz

| Kiedy | Co się dzieje samo | Co robisz ty | Czas |
|---|---|---|---|
| 1. dnia miesiąca | Raport DD się przelicza | Otwierasz, robisz przelew wg reguły | 2 min |
| 3. dnia miesiąca | Skaner się przelicza | Przeglądasz listę, wybierasz **max 1** spółkę do researchu | 10 min |
| w ciągu tygodnia | — | Research wybranej spółki (punkt 3) | 2–3 h |
| tydzień później | — | Decyzja: kupujesz albo odrzucasz | 15 min |
| koniec kwartału | — | Przegląd posiadanych spółek: czy teza nadal stoi | 1 h |
| koniec roku | — | Bramka (punkt 6) | 1 h |
| **cała reszta miesiąca** | — | **nic** | — |

Ostatni wiersz jest częścią planu, nie jego brakiem.

Jeśli w danym miesiącu lista skanera jest pusta — pomijasz wiersze 3 i 4.
Przelew z wiersza 1 robisz zawsze.

---

## 3. Research spółki — checklista

Bez przejścia wszystkich pięciu punktów nie kupujesz. Zapisujesz odpowiedzi.

**1. Dlaczego jest tanio?**
Napisz swoją hipotezę **zanim** zaczniesz szukać. Potem sprawdź, czy trafiłeś.
Jeśli nie potrafisz sformułować hipotezy — nie rozumiesz tej spółki.

**2. Ostatni raport roczny, sekcja Risk Factors.**
Nie streszczenie, nie artykuł. Oryginał. Szukasz rzeczy, których nie ma w liczbach.

**3. Skąd bierze się FCF?**
Rozbij na lata. Jeśli wysoki FCF pojawia się raz i pochodzi ze sprzedaży aktywów
albo cięcia capexu — to nie jest gotówka operacyjna, to jest zjadanie firmy.

**4. Czy branża rośnie, stoi, czy się kurczy?**
Przychody trzech największych konkurentów przez 5 lat. Tanio w kurczącej się
branży zwykle jutro jest jeszcze taniej.

**5. Teza i jej falsyfikator.**
Trzy zdania: co kupujesz i dlaczego. Plus jedno zdanie: **co konkretnie musiałoby
się wydarzyć, żebym uznał, że się myliłem.**

Jeśli nie umiesz napisać punktu 5 — nie kupujesz. To jedyny mechanizm, który
później pozwoli ci wyjść z pozycji z powodu innego niż emocje.

---

## 4. Twarde reguły

Ustalone z góry, żeby nie były przedmiotem decyzji w momencie pokusy.

- **Max 1 nowa pozycja na miesiąc.** Niezależnie od tego, ile spółek przeszło filtr.
- **Max 5% portfela na jedną spółkę.**
- **Max 25% portfela łącznie w pojedynczych akcjach.** Reszta w ETF.
- **Tydzień przerwy** między znalezieniem a kupnem. Bez wyjątków.
- **Pusta lista = brak zakupu.** Nie jest powodem do obniżenia progów.
- **Progi zmieniasz tylko w commicie z uzasadnieniem, obowiązuje od następnego
  przebiegu.** Nigdy w miesiącu, w którym lista jest pusta.

---

## 5. Konfiguracja — jednorazowo

1. Repo na GitHubie, pliki `spx_report.py`, `skaner.py`, oba workflow.
2. Ustaw `BAZOWA_WPLATA` i `REGULA_DCA` **zanim** odpalisz cokolwiek.
3. *Run workflow* na obu, przedebuguj skaner na żywych danych (Claude Code z telefonu).
4. GitHub Pages → oba linki na ekranie głównym telefonu.
5. Konto maklerskie z dostępem do rynku USA — do sprawdzenia u siebie, ale
   praktycznie: XTB, Bossa, mBank eMakler albo IBKR. Weryfikuj prowizje za akcje
   zagraniczne i przewalutowanie, bo to zjada wynik przy małych kwotach.
6. Załóż arkusz `log.csv` — patrz niżej. Bez niego bramka nie zadziała.

### Podatki
Zyski kapitałowe z zagranicznego brokera rozliczasz sam w PIT-38 — broker
zagraniczny nie wystawi ci PIT-8C. Dywidendy z USA mają swój tryb (W-8BEN,
podatek u źródła, dopłata w Polsce). **Zweryfikuj u doradcy albo w aktualnych
objaśnieniach KIS** — przepisy się zmieniają i nie opieraj się tu na mnie.

---

## 6. Bramka — po 12 miesiącach

Cały ten system może być stratą czasu. Za rok musisz umieć to sprawdzić, a to
wymaga logowania od pierwszego dnia.

`log.csv`, jeden wiersz na każdą transakcję:

```
data,ticker,kwota_pln,cena_wejscia,cena_ETF_tego_dnia,teza,falsyfikator
```

Po 12 miesiącach liczysz jedną rzecz: **wynik części spółkowej vs to, co dałoby
wrzucenie tych samych kwot w tych samych datach w zwykły ETF.**

- Przegrywasz z ETF → likwidujesz część spółkową, zostaje samo DCA. To jest
  sukces, nie porażka: kupiłeś tę informację za jeden rok zamiast za dziesięć.
- Wygrywasz → sprawdzasz, czy wygrałeś na wszystkich pozycjach, czy na jednej.
  Jedna pozycja to szczęście, nie proces.
- Remis → to przegrana. Poświęciłeś ~40 godzin rocznie, żeby wyjść na zero.

Wpisz sobie tę datę do kalendarza teraz.
