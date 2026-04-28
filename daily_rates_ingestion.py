import requests
import pandas as pd
from datetime import date, datetime, timedelta, timezone

CDN_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{currency}.min.json"
FALLBACK_URL = "https://{date}.currency-api.pages.dev/v1/currencies/{currency}.min.json"

CSV_PATH = "src/NIS_Exchange_Rates.csv"

# currency code → (column name in CSV, scale factor applied to raw ILS rate)
CURRENCY_CONFIG: dict[str, tuple[str, int]] = {
    "usd": ("USD",     1),
    "gbp": ("GBP",     1),
    "jpy": ("JPY_100", 100),  # quoted per 100 JPY
    "eur": ("EUR",     1),
    "chf": ("CHF",     1),
}


def load_csv() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    df = df[df["Date"].notna() & (df["Date"].str.strip() != "")]
    df["Date"] = pd.to_datetime(df["Date"].str.strip(), format="%d/%m/%Y")
    for col, _ in CURRENCY_CONFIG.values():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "updated_at" not in df.columns:
        df["updated_at"] = pd.NaT
    return df.sort_values("Date").reset_index(drop=True)


def fetch_rate(d: date, currency: str) -> float | None:
    date_str = d.isoformat()
    for url in [CDN_URL.format(date=date_str, currency=currency), FALLBACK_URL.format(date=date_str, currency=currency)]:
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                return resp.json()[currency].get("ils")
        except Exception:
            continue
    return None


def fetch_missing(from_date: date, to_date: date) -> list[dict]:
    rows = []
    current = from_date
    while current <= to_date:
        if current.weekday() >= 5:  # 5=Saturday, 6=Sunday
            current += timedelta(days=1)
            continue
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        row: dict = {"Date": pd.to_datetime(current)}
        any_data = False
        for currency, (col, scale) in CURRENCY_CONFIG.items():
            rate = fetch_rate(current, currency)
            row[col] = rate * scale if rate is not None else None
            if rate is not None:
                any_data = True
        if any_data:
            row["updated_at"] = now_utc
            rows.append(row)
            rates_str = ", ".join(f"{col}={row[col]}" for col, _ in CURRENCY_CONFIG.values() if row.get(col) is not None)
            print(f"  {current}: {rates_str}")
        else:
            print(f"  {current}: no data (weekend/holiday)")
        current += timedelta(days=1)
    return rows


if __name__ == "__main__":
    df = load_csv()
    latest = df["Date"].max().date()
    print(f"Latest date in CSV: {latest}")

    next_day = latest + timedelta(days=1)
    today = date.today()

    if next_day > today:
        print("CSV is already up to date.")
    else:
        print(f"\nFetching {next_day} → {today}...")
        new_rows = fetch_missing(next_day, today)

        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True).sort_values("Date")
            print(f"\nAdded {len(new_rows)} new rows.")
        else:
            print("No new data returned.")

    df["Date"] = df["Date"].dt.strftime("%d/%m/%Y")
    df.to_csv(CSV_PATH, index=False)
    print(f"CSV saved: {CSV_PATH}")
