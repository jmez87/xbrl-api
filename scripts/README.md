# NWN Flux Analysis

This folder contains a script to pull quarterly data for **NWN Holdings Company** from the XBRL US API and generate an Excel workbook comparing fiscal 1Q25 to 4Q24 quarter-to-date data. The script flags material fluctuations and provides a starting point for technical accounting review.

## Requirements

- Python 3.8+
- `requests`
- `pandas`
- An XBRL US API client ID and secret ([request one here](https://xbrl.us/apirequest)).

Install dependencies:

```bash
pip install pandas requests
```

## Usage

Set the following environment variables with your API credentials:

```bash
export XBRL_CLIENT_ID="YOUR_CLIENT_ID"
export XBRL_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

Run the script:

```bash
python nwn_flux_analysis.py
```

After running, `nwn_flux_analysis.xlsx` will be created in the current directory with three sheets:

1. **1Q25** – data for the quarter ending 1Q25
2. **4Q24** – quarter-to-date data for 4Q24
3. **Flux** – side-by-side comparison, including dollar change, percentage change, and a `Material` flag for items whose percentage change magnitude is greater than or equal to 10%.

Use the workbook as a basis to document explanations for material movements.
