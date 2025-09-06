import os
import requests
import pandas as pd

API_HOST = os.environ.get('XBRL_API_HOST', 'https://api.xbrl.us')
CLIENT_ID = os.environ.get('XBRL_CLIENT_ID')
CLIENT_SECRET = os.environ.get('XBRL_CLIENT_SECRET')
TOKEN_ENDPOINT = f"{API_HOST}/oauth2/token"
FACT_ENDPOINT = f"{API_HOST}/api/v1/fact/search"

NWN_CIK = "0001639294"  # NWN HOLDINGS INC


def get_access_token() -> str:
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("XBRL_CLIENT_ID and XBRL_CLIENT_SECRET environment variables must be set")
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(TOKEN_ENDPOINT, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_facts(access_token: str, fiscal_period: str, fiscal_year: str) -> pd.DataFrame:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "entity.cik": NWN_CIK,
        "period.fiscal-period": fiscal_period,
        "period.fiscal-year": fiscal_year,
        "fact.limit": 20000,
        "concept.local-name": "*",  # all concepts
        "fields": "concept.local-name,fact.numerical-value,period.fiscal-period,period.fiscal-year,unit.local-name"
    }
    r = requests.get(FACT_ENDPOINT, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()["data"]
    df = pd.json_normalize(data)
    return df


def pivot_facts(df: pd.DataFrame) -> pd.DataFrame:
    # pivot by concept
    pivot = df.pivot_table(index="concept.local-name", values="fact.numerical-value", aggfunc="sum")
    pivot.index.name = "Concept"
    pivot.rename(columns={"fact.numerical-value": "Value"}, inplace=True)
    return pivot


def main():
    token = get_access_token()
    q1_2025 = fetch_facts(token, "1Q", "2025")
    q4_2024 = fetch_facts(token, "4QTD", "2024")

    df_q1 = pivot_facts(q1_2025)
    df_q4 = pivot_facts(q4_2024)

    flux = df_q1.join(df_q4, lsuffix="_1Q25", rsuffix="_4Q24")
    flux["Flux"] = flux["Value_1Q25"] - flux["Value_4Q24"]
    flux["PctChange"] = flux["Flux"] / flux["Value_4Q24"] * 100

    def flag(row):
        return abs(row["PctChange"]) >= 10
    flux["Material"] = flux.apply(flag, axis=1)

    writer = pd.ExcelWriter("nwn_flux_analysis.xlsx")
    df_q1.to_excel(writer, sheet_name="1Q25")
    df_q4.to_excel(writer, sheet_name="4Q24")
    flux.to_excel(writer, sheet_name="Flux")
    writer.save()
    print("Workbook saved as nwn_flux_analysis.xlsx")


if __name__ == "__main__":
    main()
