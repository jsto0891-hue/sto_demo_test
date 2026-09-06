#!/usr/bin/env python3
"""
skaner.py — deterministyczny skaner fundamentalny. Zero komentarza, same liczby.

Kryteria sa stale i zapisane nizej. Skaner NIE mowi "kup".
Mowi: "te spolki przeszly filtr, oto ich liczby".
Jesli w danym miesiacu nie przejdzie zadna — wynikiem jest pusta tabela.
To jest poprawny wynik, nie blad.
"""

import html
import io
import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd
import requests
import yfinance as yf

# --- PROGI. Zmieniaj TYLKO miedzy przebiegami, nigdy po zobaczeniu wyniku. ---
MIN_F_SCORE = 7        # z 9
MIN_FCF_YIELD = 5.0    # %
MAX_NET_DEBT_EBITDA = 3.0
MIN_MCAP_USD = 300e6
# ---------------------------------------------------------------------------

GPW = ["PKO.WA", "PKN.WA", "PZU.WA", "PEO.WA", "KGH.WA", "CDR.WA", "DNP.WA",
       "ALE.WA", "LPP.WA", "SPL.WA", "CPS.WA", "OPL.WA", "PGE.WA", "MBK.WA",
       "ING.WA", "ACP.WA", "KTY.WA", "BDX.WA", "TPE.WA", "ATT.WA", "EAT.WA",
       "TEN.WA", "PLW.WA", "XTB.WA", "BFT.WA", "WPL.WA", "ABE.WA", "CIG.WA"]

SP500_SRC = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def wiersz(df, *nazwy):
    """yfinance zmienia etykiety wierszy miedzy wersjami — szukamy po kolei."""
    if df is None or df.empty:
        return None
    for n in nazwy:
        for idx in df.index:
            if str(idx).strip().lower() == n.lower():
                return df.loc[idx]
    return None


def val(seria, i):
    try:
        v = seria.iloc[i]
        return None if pd.isna(v) else float(v)
    except Exception:
        return None


def f_score(fin, bs, cf):
    """Piotroski F-Score (Piotroski 2000). 9 testow binarnych, 2 ostatnie lata."""
    ni = wiersz(fin, "Net Income", "Net Income Common Stockholders")
    ta = wiersz(bs, "Total Assets")
    cfo = wiersz(cf, "Operating Cash Flow", "Total Cash From Operating Activities")
    ltd = wiersz(bs, "Long Term Debt", "Long Term Debt And Capital Lease Obligation")
    ca = wiersz(bs, "Current Assets", "Total Current Assets")
    cl = wiersz(bs, "Current Liabilities", "Total Current Liabilities")
    shares = wiersz(bs, "Ordinary Shares Number", "Share Issued", "Common Stock")
    rev = wiersz(fin, "Total Revenue")
    gp = wiersz(fin, "Gross Profit")

    if any(x is None for x in (ni, ta, cfo, rev)):
        return None, {}

    def d(s, i):
        return val(s, i) if s is not None else None

    pkt, szczegoly = 0, {}

    def test(nazwa, war):
        nonlocal pkt
        if war is True:
            pkt += 1
        szczegoly[nazwa] = war

    roa0 = (d(ni, 0) / d(ta, 0)) if d(ni, 0) is not None and d(ta, 0) else None
    roa1 = (d(ni, 1) / d(ta, 1)) if d(ni, 1) is not None and d(ta, 1) else None

    test("ROA>0", roa0 is not None and roa0 > 0)
    test("CFO>0", d(cfo, 0) is not None and d(cfo, 0) > 0)
    test("ROA rosnie", None if (roa0 is None or roa1 is None) else roa0 > roa1)
    test("CFO>zysk", None if (d(cfo, 0) is None or d(ni, 0) is None) else d(cfo, 0) > d(ni, 0))

    if ltd is not None and d(ltd, 0) is not None and d(ltd, 1) is not None and d(ta, 0) and d(ta, 1):
        test("dlug maleje", (d(ltd, 0) / d(ta, 0)) <= (d(ltd, 1) / d(ta, 1)))
    else:
        test("dlug maleje", None)

    if ca is not None and cl is not None and all(d(x, i) for x in (ca, cl) for i in (0, 1)):
        test("plynnosc rosnie", (d(ca, 0) / d(cl, 0)) > (d(ca, 1) / d(cl, 1)))
    else:
        test("plynnosc rosnie", None)

    if shares is not None and d(shares, 0) is not None and d(shares, 1) is not None:
        test("brak emisji", d(shares, 0) <= d(shares, 1) * 1.01)
    else:
        test("brak emisji", None)

    if gp is not None and all(d(x, i) for x in (gp, rev) for i in (0, 1)):
        test("marza rosnie", (d(gp, 0) / d(rev, 0)) > (d(gp, 1) / d(rev, 1)))
    else:
        test("marza rosnie", None)

    if all(d(x, i) for x in (rev, ta) for i in (0, 1)):
        test("rotacja rosnie", (d(rev, 0) / d(ta, 0)) > (d(rev, 1) / d(ta, 1)))
    else:
        test("rotacja rosnie", None)

    return pkt, szczegoly


def analizuj(tk):
    t = yf.Ticker(tk)
    info = t.info or {}
    fin, bs, cf = t.financials, t.balance_sheet, t.cashflow

    mcap = info.get("marketCap")
    if not mcap:
        return None

    cfo = wiersz(cf, "Operating Cash Flow", "Total Cash From Operating Activities")
    capex = wiersz(cf, "Capital Expenditure", "Capital Expenditures")
    fcf = None
    if cfo is not None and val(cfo, 0) is not None:
        c = val(capex, 0) if capex is not None else 0.0
        fcf = val(cfo, 0) + (c or 0.0)  # capex zwykle ujemny

    ebitda = info.get("ebitda")
    dlug = info.get("totalDebt")
    gotowka = info.get("totalCash")
    nd_ebitda = None
    if ebitda and dlug is not None:
        nd_ebitda = (dlug - (gotowka or 0)) / ebitda

    hist = t.history(period="3y")
    dd3y = None
    if not hist.empty:
        dd3y = (hist["Close"].iloc[-1] / hist["Close"].max() - 1) * 100

    fs, _ = f_score(fin, bs, cf)

    return {
        "ticker": tk,
        "nazwa": (info.get("shortName") or tk)[:28],
        "branza": info.get("industry") or info.get("sector") or "",
        "mcap": mcap,
        "waluta": info.get("currency", "?"),
        "f_score": fs,
        "fcf_yield": (fcf / mcap * 100) if fcf and mcap else None,
        "nd_ebitda": nd_ebitda,
        "pe": info.get("trailingPE"),
        "pb": info.get("priceToBook"),
        "roe": (info.get("returnOnEquity") or 0) * 100 or None,
        "dd3y": dd3y,
    }


def przechodzi(r):
    return (r["f_score"] is not None and r["f_score"] >= MIN_F_SCORE
            and r["fcf_yield"] is not None and r["fcf_yield"] >= MIN_FCF_YIELD
            and r["nd_ebitda"] is not None and r["nd_ebitda"] <= MAX_NET_DEBT_EBITDA
            and r["mcap"] >= MIN_MCAP_USD)


def uniwersum_sp500():
    # Wikipedia od pewnego czasu blokuje domyslny User-Agent pandas/requests (403).
    r = requests.get(SP500_SRC, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    tab = pd.read_html(io.StringIO(r.text))[0]
    return [str(s).replace(".", "-") for s in tab["Symbol"]]


def skanuj(tickery, etykieta):
    wyniki, bledy = [], 0
    for i, tk in enumerate(tickery, 1):
        try:
            r = analizuj(tk)
            if r:
                wyniki.append(r)
        except Exception:
            bledy += 1
        if i % 25 == 0:
            print(f"  {etykieta}: {i}/{len(tickery)}", flush=True)
        time.sleep(0.25)
    print(f"  {etykieta}: gotowe, bledow {bledy}/{len(tickery)}")
    return wyniki


def fmt(v, suf="", prec=1):
    return "·" if v is None else f"{v:,.{prec}f}{suf}"


def tabela(wyniki, tylko_przechodzace):
    dane = [r for r in wyniki if przechodzi(r)] if tylko_przechodzace else wyniki
    dane.sort(key=lambda r: -(r["fcf_yield"] or -99))
    if not dane:
        return "<p class='pusto'>Żadna spółka nie przeszła filtra w tym miesiącu.</p>"
    rows = ""
    for r in dane[:40]:
        nazwa = html.escape(r["nazwa"])
        branza = html.escape(r.get("branza") or "")
        opis = f"<br><span class='branza'>{branza}</span>" if branza else ""
        rows += (f"<tr><th>{html.escape(r['ticker'])}<br><span class='maly'>{nazwa}</span>{opis}</th>"
                 f"<td>{fmt(r['f_score'],'/9',0)}</td><td>{fmt(r['fcf_yield'],'%')}</td>"
                 f"<td>{fmt(r['nd_ebitda'],'×')}</td><td>{fmt(r['pe'])}</td>"
                 f"<td>{fmt(r['pb'])}</td><td>{fmt(r['roe'],'%')}</td>"
                 f"<td>{fmt(r['dd3y'],'%')}</td></tr>")
    return ("<div class='przewin'><table><thead><tr><th>Spółka</th><th>F-Score</th>"
            "<th>FCF yield</th><th>Dług/EBITDA</th><th>P/E</th><th>P/B</th><th>ROE</th>"
            "<th>Od szczytu 3l</th></tr></thead><tbody>" + rows + "</tbody></table></div>")


CSS = """:root{--tlo:#EDF0F1;--karta:#FFF;--atrament:#17262E;--cichy:#66787F;--linia:#D3DADD}
*{box-sizing:border-box}body{margin:0;background:var(--tlo);color:var(--atrament);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
padding:20px 16px 56px;max-width:760px;margin-inline:auto}
h1{font:400 17px/1.3 -apple-system,sans-serif;color:var(--cichy);margin:0 0 20px}
h2{font:400 16px/1.3 -apple-system,sans-serif;margin:32px 0 4px}
.wstep{font-size:14px;color:var(--cichy);margin:0 0 12px}
.przewin{overflow-x:auto;-webkit-overflow-scrolling:touch;background:var(--karta);
border:1px solid var(--linia);border-radius:3px}
table{border-collapse:collapse;font-size:13px;min-width:100%}
th,td{padding:9px 11px;text-align:right;white-space:nowrap;border-bottom:1px solid var(--linia)}
thead th{font-weight:500;color:var(--cichy);font-size:12px}
tbody th{text-align:left;position:sticky;left:0;background:var(--karta);
font-weight:400;font-variant-numeric:tabular-nums}
td{font-variant-numeric:tabular-nums}
tr:last-child th,tr:last-child td{border-bottom:none}
.maly{color:var(--cichy);font-size:11px}
.branza{color:var(--cichy);font-size:11px;font-style:italic}
.pusto{background:var(--karta);border:1px solid var(--linia);border-radius:3px;
padding:22px;margin:0;color:var(--cichy);font-size:14px}
.uwagi{margin-top:32px;font-size:13px;line-height:1.65;color:var(--cichy)}
.uwagi li{margin-bottom:7px}
footer{margin-top:28px;font-size:12px;color:var(--cichy);border-top:1px solid var(--linia);padding-top:14px}"""


def main():
    try:
        us = uniwersum_sp500()
    except Exception as e:
        print(f"Nie udalo sie pobrac listy S&P 500: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Skanuje {len(us)} spolek S&P 500...")
    w_us = skanuj(us, "S&P500")
    print(f"Skanuje {len(GPW)} spolek GPW...")
    w_pl = skanuj(GPW, "GPW")

    gen = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skaner fundamentalny</title><style>{CSS}</style></head><body>
<h1>Skaner fundamentalny</h1>
<p class="wstep">Filtr: F-Score ≥ {MIN_F_SCORE}/9, FCF yield ≥ {MIN_FCF_YIELD}%,
dług netto/EBITDA ≤ {MAX_NET_DEBT_EBITDA}×, kapitalizacja ≥ {MIN_MCAP_USD/1e6:.0f} mln.
Sortowanie po FCF yield. Kryteria ustalone z góry i niezmieniane po zobaczeniu wyniku.</p>
<h2>S&amp;P 500 — przeszły filtr</h2>
{tabela(w_us, True)}
<h2>GPW — wszystkie, do wglądu</h2>
<p class="wstep">Bez filtra, poglądowo. Pokrycie danych fundamentalnych dla GPW
w yfinance jest niepełne — puste pola oznaczają brak danych, nie zero.</p>
{tabela(w_pl, False)}
<h2>Co oznaczają kolumny</h2>
<ul class="uwagi">
<li><b>F-Score</b> — 9-punktowy test Piotroskiego: bilans, rentowność, trend rok do roku. Skala 0–9. Filtr wymaga ≥{MIN_F_SCORE}. Wysoki nie znaczy „tanio", tylko „solidne liczby".</li>
<li><b>FCF yield</b> — gotówka operacyjna minus capex, podzielona przez kapitalizację. Im wyżej, tym więcej gotówki firma generuje względem swojej wyceny. Filtr wymaga ≥{MIN_FCF_YIELD:.0f}%.</li>
<li><b>Dług/EBITDA</b> — dług netto do zysku operacyjnego przed amortyzacją. Im niżej, tym mniej zadłużona firma, tym większa szansa, że przetrwa gorszy rok. Filtr wymaga ≤{MAX_NET_DEBT_EBITDA:.0f}×.</li>
<li><b>P/E</b> — cena do zysku. Kontekst, nie kryterium filtra. Wysoki bywa „drogo" albo „rynek oczekuje wzrostu"; niski bywa „tanio" albo „coś jest nie tak" — liczba sama tego nie mówi.</li>
<li><b>P/B</b> — cena do wartości księgowej. Kontekst. Poniżej 1 czasem okazja, czasem spółka w kłopotach — trzeba sprawdzić dlaczego.</li>
<li><b>ROE</b> — zysk netto do kapitału własnego. Kontekst. Wysoki bywa dobry, bywa też efektem dużego zadłużenia — sprawdź Dług/EBITDA obok.</li>
<li><b>Od szczytu 3l</b> — ile % poniżej 3-letniego szczytu jest dziś kurs. Kontekst, nie kryterium — spółka może przejść filtr przy szczycie wszech czasów.</li>
</ul>
<ul class="uwagi">
<li>To nie jest rekomendacja. Filtr mówi tylko, że spółka spełniła kryteria liczbowe.</li>
<li>F-Score bada bilans i rentowność, nie wycenę. Wysoki F-Score nie znaczy „tanio".</li>
<li>Niski wskaźnik często oznacza realny problem, którego liczby jeszcze nie pokazują.</li>
<li>Dane z yfinance, nieaudytowane, z opóźnieniem. Przed jakąkolwiek decyzją sprawdź raport spółki.</li>
<li>Brak spółek na liście to poprawny wynik. Nie jest powodem do obniżania progów.</li>
</ul>
<footer>Przeliczono {gen}. Odświeża się 3. dnia miesiąca.</footer></body></html>"""

    os.makedirs("docs", exist_ok=True)
    with open("docs/skaner.html", "w", encoding="utf-8") as f:
        f.write(html)
    ile = sum(1 for r in w_us if przechodzi(r))
    print(f"OK — {ile} spolek przeszlo filtr")


if __name__ == "__main__":
    main()
