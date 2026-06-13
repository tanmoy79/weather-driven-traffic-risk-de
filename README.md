# Weather-Driven Traffic Risk in Germany (`weather-driven-traffic-risk-de`)

This project is part of the course **"Research Software Engineering (RSE)"**, taught by Prof. Dr. Anna-Lena Lamprecht at the University of Potsdam.

A reproducible Snakemake workflow that combines German traffic accident records with hourly weather observations to analyse how precipitation, frost, heat and solar radiation relate to traffic accident frequency and severity in Germany (2020–2024).

The accident data comes from the official [German Accident Atlas (Unfallatlas)](https://unfallatlas.statistikportal.de/), maintained by the Federal Statistical Office and the Statistical Offices of the Länder. The weather data comes from the [DWD Climate Data Center (CDC)](https://opendata.dwd.de/climate_environment/CDC/) open data server.

---

## Research Questions

### 1. Weather and Accident Severity (RQ1)
* **Question:** How do varying intensities of precipitation (light drizzle vs. heavy rainfall) and freezing temperatures impact traffic accident frequency and severity, and do they shift the mix of accident types (e.g., loss-of-control accidents vs. collisions)?
* **Objective:** Quantify how specific precipitation thresholds and frost change the accident rate, the share of severe accidents, and the kind of accidents that happen. (Originally we wanted to compare Autobahns against rural roads, but the published Unfallatlas data contains no road-class attribute, so the question was refined to severity and accident types instead.)

### 2. The Threat of the Summer Sun: Sun Glare vs. Heatwaves (RQ2)
* **Question:** To what extent do summer weather factors—specifically high global solar radiation (sun glare) and extreme heat—predict commuter-hour traffic accident rates compared to rainy conditions?
* **Objective:** Move beyond traditional winter-centric risk models and test whether heat and low-angle sun glare during peak morning and evening transit windows measurably raise accident rates.

### 3. Spatial Sensitivity & Regional Driving Behavior (RQ3)
* **Question:** Which German states exhibit the strongest sensitivity of traffic accident patterns to changing weather conditions, and how does this sensitivity differ between city states and territorial states?
* **Objective:** Construct a state-level sensitivity index (rain and frost risk ratios per state) to evaluate regional differences between highly urbanized city states (Berlin, Hamburg, Bremen) and the larger territorial states.

### 4. The Evolution of Weather Risk Over Time (RQ4)
* **Question:** How have traffic safety patterns evolved under varying weather conditions in Germany between 2020 and 2024, and has the relative risk of weather-related accidents declined over that period?
* **Objective:** Track the yearly weather risk ratios and severity shares from 2020 to 2024 to see whether adverse weather has become less dangerous over time (for example through modern vehicle safety technology such as ESP and autonomous braking).

## Key Results

The full generated report with figures is in [results/report.md](results/report.md).

* **RQ1:** Accidents on wet roads happened **2.65×** as often per rainy hour as dry-road accidents per dry hour. On icy roads, **64 %** of accidents were loss-of-control accidents (vs. 17 % on dry roads), and the share of *severe* accidents was lower on icy roads (16.8 % vs. 18.7 % on dry roads) — drivers apparently slow down.
* **RQ2:** Neither strong sunshine (rate ratio 1.03) nor heat (1.02) raised summer commuter-hour accident rates measurably; summer rain remains the more relevant factor.
* **RQ3:** Mecklenburg-Vorpommern (sensitivity index 2.93) and Schleswig-Holstein (2.87) were the most weather-sensitive states, Bayern (1.21) the least; the three city states (Berlin, Hamburg, Bremen) averaged 2.16 vs. 1.96 for territorial states.
* **RQ4:** Rain remained roughly equally dangerous across 2020–2024 (no significant trend, p = 0.42), but the share of severe accidents on wet/icy roads fell steadily from 18.5 % in 2020 to 15.0 % in 2024 — consistent with modern vehicle safety technology softening the consequences.

---

## What the Workflow Does

The workflow follows the activity diagram in [docs/requirements.md](docs/requirements.md):

1. **prepare_accidents** – merges the yearly Unfallatlas files (changing column formats) into one clean table.
2. **download_weather** – selects DWD stations (2 per federal state) and downloads hourly temperature, precipitation and solar radiation (CC-BY 4.0).
3. **prepare_weather** – turns the archives into a gap-free hourly series in local time.
4. **join_data** – assigns every accident to its nearest weather station (KD-tree).
5. **build_features** – aggregates weather hours and accident counts into time cells (station, year, month, weekend, hour) with configurable thresholds. This is necessary because the Unfallatlas does not publish exact accident dates.
6. **descriptive_stats** – summary statistics and overview figures.
7. **analyze_rq / plot_rq** – statistics and one figure per research question (standardized rate ratios, chi-square tests, correlations, trends).
8. **report** – assembles everything into `results/report.md`.

## Installation

Requires Python ≥ 3.10. Set up a virtual environment and install the dependencies:

```bash
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Workflow

The raw accident data (2020–2024) is included in `data/raw_accidents/`. The weather data (~200 MB) is downloaded automatically from the DWD open data server on the first run, so an internet connection is needed once.

```bash
snakemake --cores 4 -s workflow/Snakefile
```

The whole run takes roughly 15–20 minutes on a normal laptop. The prepared hourly climate data is saved separately to `data/climate/`, the joined accident–station data to `data/joined/`, remaining intermediate files to `data/processed/`, and all results (tables, figures, report) to `results/`.

### Configuration

All parameters live in [config/config.yaml](config/config.yaml): the year range, stations per state, the maximum accident-to-station distance and the thresholds for rain, heavy rain, frost, heat and strong sun. Each step is also a standalone command-line tool (see `python src/<tool>.py --help`) and can be run independently.

### Reproducing the Example Results

The committed files in `results/` were produced with the default configuration. To reproduce them, delete the `results/` directory and run the workflow again — the analysis is deterministic, so the tables and figures will be identical (the weather download is cached in `data/raw_weather/`).

## Tests

The core functionality (format handling, cleaning, joining, classification, statistics) is covered by unit tests:

```bash
pytest tests
```

## Repository Structure

```
weather-driven-traffic-risk-de/
├── CITATION.cff                       # Citation metadata for this software
├── CONDUCT.md                         # Code of conduct
├── CONTRIBUTING.md                    # Contribution guidelines
├── LICENSE                            # MIT license
├── README.md
├── requirements.txt                   # Python dependencies (pip)
├── .flake8                            # Linter configuration
├── .github/
│   └── workflows/
│       └── ci.yml                     # CI: flake8, pytest, Snakemake dry run
├── config/
│   └── config.yaml                    # All workflow parameters (years, thresholds, …)
├── data/
│   └── raw_accidents/                 # Unfallatlas accident records (committed)
│       ├── Unfallorte2020_LinRef.csv  #   one file per year, 2020–2024;
│       ├── ...                        #   data/raw_weather/, data/climate/,
│       └── Unfallorte2024_LinRef.csv  #   data/joined/ and data/processed/
│                                      #   are generated on the first run
├── docs/                              # Requirements and activity diagrams
│   ├── requirements.md                # Detailed requirements and research questions
│   ├── Activity Diagram.png
│   ├── activity_diagram_updated.drawio
│   └── activity_diagram_updated.png
├── results/                           # Generated output (reproducible)
│   ├── report.md                      # Final assembled report
│   ├── summary_statistics.csv
│   ├── rq1_results.csv … rq4_results.csv
│   └── figures/                       # Overview and per-RQ figures (PNG)
├── src/                               # One command-line tool per workflow step
│   ├── prepare_accidents.py           # Merge yearly Unfallatlas files
│   ├── download_weather.py            # Select DWD stations, download observations
│   ├── prepare_weather.py             # Build gap-free hourly weather series
│   ├── join_data.py                   # Match accidents to nearest station (KD-tree)
│   ├── build_features.py              # Aggregate into time cells with thresholds
│   ├── descriptive_stats.py           # Summary statistics and overview figures
│   ├── analyze_rq.py                  # Statistics per research question
│   ├── plot_results.py                # One figure per research question
│   └── make_report.py                 # Assemble results/report.md
├── tests/                             # Pytest unit tests
│   ├── conftest.py
│   ├── test_prepare_accidents.py
│   ├── test_prepare_weather.py
│   ├── test_join_data.py
│   ├── test_build_features.py
│   └── test_analyze_rq.py
└── workflow/
    └── Snakefile                      # Snakemake pipeline tying it all together
```

## Data Sources and Licenses

* **Unfallatlas** – © Statistische Ämter des Bundes und der Länder, [Datenlizenz Deutschland – Namensnennung – 2.0](https://www.govdata.de/dl-de/by-2-0).
* **DWD Climate Data Center** – Deutscher Wetterdienst, [CC-BY 4.0](https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf); hourly station observations of air temperature, precipitation and solar radiation.

## Citation

If you use this software, please cite it using the metadata in [CITATION.cff](CITATION.cff).

---

## Community & Contributing

We welcome community contributions, bug reports, and structural analytical improvements!

* **Contribution Guidelines:** [Contribution Guide (CONTRIBUTING.md)](CONTRIBUTING.md).

* **Code of Conduct:** In order to ensure a welcoming, inclusive, and collaborative environment for everyone, all project participants and contributors are expected to adhere to our [Code of Conduct](CONDUCT.md).

## License

This project is licensed under the [MIT License](LICENSE).
