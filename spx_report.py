#!/usr/bin/env python3
"""
spx_report.py — liczy warunkowe base rate'y dla S&P 500 i zapisuje docs/index.html

Odpalane automatycznie przez GitHub Actions raz w miesiacu.
NIE PROGNOZUJE. Pokazuje, co historycznie dzialo sie PO spadku o X% od szczytu.
"""

import os
import sys
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

# --- TWOJA REGULA -----------------------------------------------------------
# Ustaw ZANIM zobaczysz aktualny drawdown. Potem nie ruszaj.
BAZOWA_WPLATA = 500  # PLN / miesiac
REGULA_DCA = [(0, 1.0), (-10, 2.0), (-20, 3.0), (-30, 4.0)]
# ---------------------------------------------------------------------------

ZRODLO = "^GSPC"  # S&P 500, Yahoo Finance przez yfinance
PROGI = [-5, -10, -15, -20, -25, -30, -40, -50]
HORYZONTY = {"1 rok": 252, "3 lata": 756, "5 lat": 1260, "10 lat": 2520}
OD = "1950-01-01"


def pobierz():
    # Stooq od pewnego czasu wymaga wykonania JS ("verify your browser") i nie da
    # sie go juz odpytac zwyklym requests.get — stad yfinance jako zrodlo danych.
    hist = yf.Ticker(ZRODLO).history(period="max", auto_adjust=False)
    if hist.empty:
        raise RuntimeError(f"yfinance nie zwrocilo danych dla {ZRODLO}")
    df = hist.reset_index()[["Date", "Close"]].copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna().sort_values("Date")
    df = df[df["Date"] >= pd.Timestamp(OD)].reset_index(drop=True)
    if len(df) < 5000:
        raise RuntimeError(f"Za malo danych: {len(df)} sesji. Prawdopodobnie blad zrodla.")
    df["ATH"] = df["Close"].cummax()
    df["DD"] = (df["Close"] / df["ATH"] - 1.0) * 100.0
    return df


def epizody(df, prog):
    """Pierwsze przekroczenie progu w kazdym odrebnym epizodzie obsuniecia."""
    dd = df["DD"].to_numpy()
    out, aktywny = [], False
    for i, v in enumerate(dd):
        if not aktywny and v <= prog:
            out.append(i)
            aktywny = True
        elif aktywny and v >= -1.0:
            aktywny = False
    return out


def najglebszy(df, start):
    dd = df["DD"].to_numpy()
    i, worst = start, dd[start]
    while i < len(dd) and dd[i] < -1.0:
        worst = min(worst, dd[i])
        i += 1
    return worst


def fwd(df, start, sesje):
    c = df["Close"].to_numpy()
    k = start + sesje
    return None if k >= len(c) else (c[k] / c[start] - 1.0) * 100.0


def policz(df):
    wiersze = []
    for prog in PROGI:
        ep = epizody(df, prog)
        if not ep:
            continue
        glebiej = {}
        for kolejny in PROGI:
            if kolejny < prog:
                trafienia = sum(1 for e in ep if najglebszy(df, e) <= kolejny)
                glebiej[kolejny] = 100.0 * trafienia / len(ep)
        zwroty = {}
        for nazwa, sesje in HORYZONTY.items():
            z = [x for x in (fwd(df, e, sesje) for e in ep) if x is not None]
            zwroty[nazwa] = (pd.Series(z).median(), 100.0 * (pd.Series(z) > 0).mean(), len(z)) if z else None
        wiersze.append({"prog": prog, "n": len(ep), "glebiej": glebiej, "zwroty": zwroty,
                        "ostatni": df["Date"].iloc[ep[-1]].date()})
    return wiersze


def mnoznik(dd):
    m = 1.0
    for prog, mult in sorted(REGULA_DCA, reverse=True):
        if dd <= prog:
            m = mult
    return m


CSS = """
:root{--tlo:#EDF0F1;--karta:#FFFFFF;--atrament:#17262E;--cichy:#66787F;
--linia:#D3DADD;--sygnal:#3E6B7A;--uwaga:#8A5A2B}
*{box-sizing:border-box}
body{margin:0;background:var(--tlo);color:var(--atrament);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
padding:20px 16px 56px;max-width:640px;margin-inline:auto}
h1{font:400 17px/1.3 -apple-system,sans-serif;color:var(--cichy);margin:0 0 22px}
.hero{background:var(--karta);border:1px solid var(--linia);border-radius:3px;
padding:24px 20px;margin-bottom:14px}
.dd{font:400 62px/1 Georgia,"Times New Roman",serif;letter-spacing:-.02em;
color:var(--sygnal);margin:0}
.pod{color:var(--cichy);font-size:14px;margin:10px 0 0}
.regula{background:var(--karta);border:1px solid var(--linia);border-left:3px solid var(--uwaga);
border-radius:3px;padding:18px 20px;margin-bottom:26px}
.kwota{font:400 30px/1.2 Georgia,serif;margin:0 0 6px}
.regula p{margin:0;font-size:14px;color:var(--cichy)}
h2{font:400 15px/1.3 -apple-system,sans-serif;margin:0 0 6px}
.wstep{font-size:14px;color:var(--cichy);margin:0 0 14px}
.przewin{overflow-x:auto;-webkit-overflow-scrolling:touch;
background:var(--karta);border:1px solid var(--linia);border-radius:3px}
table{border-collapse:collapse;font-size:13px;min-width:100%}
th,td{padding:9px 11px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--linia)}
th{font-weight:500;color:var(--cichy);font-size:12px}
tbody th{text-align:left;position:sticky;left:0;background:var(--karta);
color:var(--atrament);font-variant-numeric:tabular-nums}
td{font-variant-numeric:tabular-nums}
tr:last-child th,tr:last-child td{border-bottom:none}
.maly{color:var(--cichy)}
.uwagi{margin-top:30px;font-size:13px;line-height:1.65;color:var(--cichy)}
.uwagi li{margin-bottom:7px}
footer{margin-top:30px;font-size:12px;color:var(--cichy);border-top:1px solid var(--linia);padding-top:14px}
"""


def html(df, wiersze):
    ost = df.iloc[-1]
    dd = float(ost["DD"])
    m = mnoznik(dd)
    sma = df["Close"].rolling(210).mean().iloc[-1]
    stan = "powyżej" if ost["Close"] > sma else "poniżej"

    kol = [p for p in PROGI if p < PROGI[0]]
    th = "".join(f"<th>do {p}%</th>" for p in kol)
    th += "".join(f"<th>{h}</th>" for h in HORYZONTY)

    body = ""
    for w in wiersze:
        cells = ""
        for p in kol:
            v = w["glebiej"].get(p)
            cells += f"<td>{v:.0f}%</td>" if v is not None else '<td class="maly">·</td>'
        for h in HORYZONTY:
            z = w["zwroty"].get(h)
            if z:
                med, dod, n = z
                cells += f"<td>{med:+.0f}%<br><span class='maly'>{dod:.0f}% dodatnich · n={n}</span></td>"
            else:
                cells += '<td class="maly">·</td>'
        body += f"<tr><th>{w['prog']}%<br><span class='maly'>n={w['n']}</span></th>{cells}</tr>"

    gen = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html><html lang="pl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>S&P 500 — base rate'y</title><style>{CSS}</style></head><body>
<h1>S&amp;P 500 — obsunięcie od szczytu</h1>
<div class="hero">
<p class="dd">{dd:+.1f}%</p>
<p class="pod">Zamknięcie {ost['Close']:,.0f} wobec szczytu {ost['ATH']:,.0f}.
Dane z {ost['Date'].date()}. Cena {stan} 10-miesięcznej średniej.</p>
</div>
<div class="regula">
<p class="kwota">{BAZOWA_WPLATA * m:,.0f} PLN</p>
<p>Twoja reguła przy tym obsunięciu: mnożnik {m:.1f}×. Zapisałeś ją, zanim zobaczyłeś tę liczbę.</p>
</div>
<h2>Co działo się dalej</h2>
<p class="wstep">Wiersz to próg obsunięcia. Kolumny „do −X%" mówią, w ilu procentach epizodów
spadek pogłębił się do tego poziomu. Kolumny czasowe to mediana zwrotu ceny od dnia
pierwszego dotknięcia progu.</p>
<div class="przewin"><table>
<thead><tr><th>Próg</th>{th}</tr></thead><tbody>{body}</tbody></table></div>
<ul class="uwagi">
<li>Liczone są epizody, nie dni. Każdy epizod kończy się dopiero po powrocie do szczytu — inaczej n byłoby sztucznie zawyżone o rząd wielkości.</li>
<li>Przy głębokich progach n jest jednocyfrowe. Z czterech obserwacji nie liczy się prawdopodobieństw.</li>
<li>Okna zwrotów nakładają się, więc obserwacje nie są niezależne.</li>
<li>Zwroty cenowe, bez dywidend, inflacji i podatku Belki.</li>
<li>Jeden indeks jednego kraju, który akurat wygrał XX wiek.</li>
<li>To mówi, co bywało. Nie mówi, co będzie.</li>
</ul>
<footer>Dane: Yahoo Finance (^GSPC, od {OD[:4]}). Przeliczono {gen}.
Odświeża się automatycznie pierwszego dnia miesiąca.</footer>
</body></html>"""


def main():
    try:
        df = pobierz()
    except Exception as e:
        print(f"BLAD: {e}", file=sys.stderr)
        sys.exit(1)
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html(df, policz(df)))
    print(f"OK — {len(df)} sesji, DD {df['DD'].iloc[-1]:+.2f}%")


if __name__ == "__main__":
    main()
