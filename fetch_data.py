"""Optional: download the CURRENT NASA NH table, not the course snapshot."""
from pathlib import Path
from urllib.request import Request, urlopen
from io import BytesIO
import argparse
import pandas as pd

URL = "https://data.giss.nasa.gov/gistemp/tabledata_v4/NH.Ts+dSST.csv"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "data" / "northern_surface_temperature.csv")
args = parser.parse_args()
if args.output.exists():
    parser.error("Output already exists; choose --output to avoid overwriting a snapshot")
request = Request(URL, headers={"User-Agent": "CISC7204-educational-analysis/1.0"})
with urlopen(request, timeout=60) as response:
    raw = response.read()
frame = pd.read_csv(BytesIO(raw), skiprows=1, na_values=["***", "****"])
cols = "Year Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
if not set(cols).issubset(frame.columns):
    raise ValueError("NASA table structure changed. Inspect before adapting.")
frame = frame.loc[frame.Year.between(1880, 2018), cols]
args.output.parent.mkdir(parents=True, exist_ok=True)
frame.to_csv(args.output, index=False)
print(f"Downloaded {len(frame)} historical years from {URL}")
print("Current NASA revisions may differ from the figures supplied with this project.")
