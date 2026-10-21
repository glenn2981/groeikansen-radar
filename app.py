import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone

st.set_page_config(page_title="Groeikansen Radar", page_icon="📈", layout="wide")

st.title("📈 Groeikansen Radar")
st.caption("Wereldwijde groeiaandelen • markttrends • openbare beleggersinformatie")

st.info(
    "Prototype: koersen en financiële gegevens komen via Yahoo Finance/yfinance en kunnen vertraagd, "
    "onvolledig of tijdelijk niet beschikbaar zijn. Dit is geen beleggingsadvies. "
    "De app toont geen gegarandeerde voorspellingen."
)

DEFAULT_TICKERS = "NVDA, MSFT, AMZN, GOOGL, META, TSM, ASML, AVGO, MELI, NU, SHOP, PLTR"
ETF_MAP = {
    "VS - brede markt": "SPY",
    "Wereldwijde aandelen": "VT",
    "Opkomende markten": "VWO",
    "India": "INDA",
    "China": "MCHI",
    "Halfgeleiders": "SMH",
    "Cybersecurity": "CIBR",
    "Robotica & automatisering": "BOTZ",
    "Biotechnologie": "XBI",
    "Schone energie": "ICLN",
}

def safe_float(value):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None

def load_ticker(symbol):
    ticker = yf.Ticker(symbol.strip().upper())
    hist = ticker.history(period="6mo", interval="1d", auto_adjust=True)
    info = {}
    try:
        info = ticker.info or {}
    except Exception:
        pass
    return ticker, hist, info

tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Dashboard", "🚀 Groeiaandelen", "🌍 Wereld & sectoren", "🏦 Grote beleggers"
])

with tab1:
    st.subheader("Marktoverzicht")
    symbols = [x.strip().upper() for x in DEFAULT_TICKERS.split(",")]
    cols = st.columns(4)
    for i, symbol in enumerate(["SPY", "QQQ", "VT", "VWO"]):
        try:
            hist = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=True)
            if not hist.empty:
                last = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last
                change = ((last / prev) - 1) * 100 if prev else 0
                cols[i].metric(symbol, f"{last:,.2f}", f"{change:+.2f}%")
            else:
                cols[i].metric(symbol, "Geen data")
        except Exception:
            cols[i].metric(symbol, "Niet beschikbaar")
    st.markdown("### Wat deze marktmeters volgen")
    st.write(
        "- **SPY**: Amerikaanse brede aandelenmarkt\n"
        "- **QQQ**: grote Nasdaq-100-bedrijven\n"
        "- **VT**: wereldwijde aandelen\n"
        "- **VWO**: opkomende markten"
    )
    st.caption(
        "ETF-koersbewegingen zijn slechts een indicatie van marktstemming. "
        "Ze bewijzen niet hoeveel nieuw geld er op dit moment instroomt."
    )

with tab2:
    st.subheader("Groeiaandelen vergelijken")
    ticker_input = st.text_input("Aandelen (komma's ertussen)", DEFAULT_TICKERS)
    st.caption("Begin met de voorbeeldlijst of vul eigen tickers in. Voorbeeld: ASML, NVDA, TSM")
    if st.button("Analyseer aandelen", type="primary"):
        symbols = list(dict.fromkeys(x.strip().upper() for x in ticker_input.split(",") if x.strip()))
        rows = []
        progress = st.progress(0)
        status = st.empty()
        for idx, symbol in enumerate(symbols):
            status.write(f"Gegevens ophalen: {symbol}…")
            try:
                ticker, hist, info = load_ticker(symbol)
                if hist.empty:
                    rows.append({"Ticker": symbol, "Bedrijf": info.get("shortName", symbol), "Status": "Geen koersdata"})
                    continue
                last = safe_float(hist["Close"].iloc[-1])
                prev = safe_float(hist["Close"].iloc[-2]) if len(hist) > 1 else last
                month_ago = safe_float(hist["Close"].iloc[-22]) if len(hist) > 22 else safe_float(hist["Close"].iloc[0])
                six_month = safe_float(hist["Close"].iloc[0])
                daily = ((last / prev) - 1) * 100 if last and prev else None
                month_change = ((last / month_ago) - 1) * 100 if last and month_ago else None
                six_month_change = ((last / six_month) - 1) * 100 if last and six_month else None
                rows.append({
                    "Ticker": symbol,
                    "Bedrijf": info.get("shortName", symbol),
                    "Koers": round(last, 2) if last is not None else None,
                    "Dag %": round(daily, 2) if daily is not None else None,
                    "Ongeveer 1 maand %": round(month_change, 2) if month_change is not None else None,
                    "6 maanden %": round(six_month_change, 2) if six_month_change is not None else None,
                    "Omzetgroei %": round(safe_float(info.get("revenueGrowth")) * 100, 1) if safe_float(info.get("revenueGrowth")) is not None else None,
                    "Winstmarge %": round(safe_float(info.get("profitMargins")) * 100, 1) if safe_float(info.get("profitMargins")) is not None else None,
                    "P/E": round(safe_float(info.get("trailingPE")), 1) if safe_float(info.get("trailingPE")) is not None else None,
                    "Marktkapitalisatie": info.get("marketCap"),
                    "Status": "Indicatieve gegevens"
                })
            except Exception as exc:
                rows.append({"Ticker": symbol, "Bedrijf": symbol, "Status": f"Gegevens niet beschikbaar"})
            progress.progress((idx + 1) / max(len(symbols), 1))
        status.empty()
        progress.empty()
        df = pd.DataFrame(rows)
        if not df.empty:
            if "Marktkapitalisatie" in df.columns:
                df["Marktkapitalisatie"] = df["Marktkapitalisatie"].apply(
                    lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and pd.notna(x) else x
                )
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download resultaten als CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name="groeikansen_radar.csv",
                mime="text/csv"
            )
            st.caption("Gebruik deze cijfers om verder onderzoek te doen; dit is geen automatisch koopadvies.")

with tab3:
    st.subheader("Wereld- en sectortrends")
    st.write(
        "Deze eerste versie volgt ETF's als **marktindicatoren**. Voor echte dagelijkse geldstromen "
        "is een gespecialiseerde databron nodig; ETF-rendement alleen is geen bewijs van instroom."
    )
    chosen = st.multiselect(
        "Kies markten of sectoren",
        list(ETF_MAP.keys()),
        default=["VS - brede markt", "Wereldwijde aandelen", "Opkomende markten", "Halfgeleiders"]
    )
    if st.button("Bekijk markttrends"):
        rows = []
        for label in chosen:
            symbol = ETF_MAP[label]
            try:
                hist = yf.Ticker(symbol).history(period="6mo", interval="1d", auto_adjust=True)
                if hist.empty:
                    rows.append({"Markt/sector": label, "ETF": symbol, "Status": "Geen data"})
                    continue
                last = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last
                start = float(hist["Close"].iloc[0])
                rows.append({
                    "Markt/sector": label,
                    "ETF": symbol,
                    "Laatste koers": round(last, 2),
                    "Dagverandering %": round((last / prev - 1) * 100, 2) if prev else None,
                    "6 maanden %": round((last / start - 1) * 100, 2) if start else None,
                    "Gem. volume (6 mnd)": int(hist["Volume"].mean()) if "Volume" in hist else None,
                    "Status": "Koers-/volume-indicator"
                })
            except Exception:
                rows.append({"Markt/sector": label, "ETF": symbol, "Status": "Gegevens niet beschikbaar"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown("**Volgende uitbreidingsstap:** een betaalbare databron aansluiten die expliciete ETF-fondsenstromen rapporteert.")

with tab4:
    st.subheader("Grote beleggers — openbare rapportages")
    st.write(
        "Yahoo Finance kan voor sommige aandelen openbare institutionele houders tonen. "
        "Beschikbaarheid en actualiteit verschillen per bedrijf en markt."
    )
    symbol = st.text_input("Ticker om te bekijken", "NVDA").strip().upper()
    if st.button("Bekijk gerapporteerde houders"):
        try:
            holders = yf.Ticker(symbol).institutional_holders
            if holders is not None and not holders.empty:
                st.dataframe(holders, use_container_width=True, hide_index=True)
                st.caption(
                    "Dit zijn gerapporteerde posities, niet de live transacties van beleggers. "
                    "Rapportages kunnen achterlopen."
                )
            else:
                st.warning("Er zijn via deze bron geen institutionele houders beschikbaar voor deze ticker.")
        except Exception:
            st.warning("Houdersgegevens zijn op dit moment niet beschikbaar voor deze ticker.")

st.divider()
st.caption(f"Groeikansen Radar • prototype • laatst geopend: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
st.caption("Controleer altijd de brongegevens. Geen enkel model kan toekomstige koersstijgingen garanderen.")
