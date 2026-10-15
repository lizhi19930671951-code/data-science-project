# Input data

No raw dataset is committed. For exact reproduction, place your course file
`northern_surface_temperature.csv` here. Its expected SHA-256 is recorded in
`../figures/metrics.json`. Do not publish a course redistribution without
checking its permission terms.

Alternatively, run `python fetch_data.py` to retrieve the current official NASA
Northern Hemisphere land-ocean anomaly table. NASA can revise historical values,
so this reproduces the methodology, not necessarily the exact snapshot results.

Source: https://data.giss.nasa.gov/gistemp/
Current table: https://data.giss.nasa.gov/gistemp/tabledata_v4/NH.Ts+dSST.csv
FAQ and methods: https://data.giss.nasa.gov/gistemp/faq/

Credit NASA GISS/GISTEMP. NASA-produced information is generally available for
public informational use; check the provider's current notices and any
third-party restrictions before redistributing data. This project does not
relicense the course CSV or assert permission over third-party material.
