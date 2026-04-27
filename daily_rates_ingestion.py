import requests
import pandas as pd
from datetime import date, datetime, timedelta, timezone

CDN_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date}/v1/currencies/usd.min.json"
FALLBACK_URL = "https://{date}.currency-api.pages.dev/v1/currencies/usd.min.json"

CSV_PATH = "src/USD-NIS Exchange Rate.csv"


def load_csv() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    df = df[df["Date"].notna() & (df["Date"].str.strip() != "")]
    df["Date"] = pd.to_datetime(df["Date"].str.strip(), format="%d/%m/%Y")
    df["USD"] = pd.to_numeric(df["USD"], errors="coerce")
    if "updated_at" not in df.columns:
        df["updated_at"] = pd.NaT
    return df.sort_values("Date").reset_index(drop=True)


def fetch_rate(d: date) -> float | None:
    date_str = d.isoformat()
    for url in [CDN_URL.format(date=date_str), FALLBACK_URL.format(date=date_str)]:
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok:
                return resp.json()["usd"].get("ils")
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
        rate = fetch_rate(current)
        if rate is not None:
            rows.append({
                "Date": pd.to_datetime(current),
                "USD": rate,
                "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            })
            print(f"  {current}: {rate}")
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
