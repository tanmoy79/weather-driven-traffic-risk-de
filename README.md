# Weather-Driven Traffic Risk in Germany (`weather-driven-traffic-risk-de`)

This project is part of the course **"Research Software Engineering (RSE)"**, taught by Prof. Dr. Anna-Lena Lamprecht at the University of Potsdam.

A reproducible data pipeline and empirical analysis exploring the structural, environmental, spatial, and temporal relationships between adverse weather conditions and traffic accident dynamics across Germany. By leveraging historical meteorological data alongside spatialized accident coordinates, this repository automates data ingestion, cleaning, multi-criteria risk modeling, and regression analyses to quantify weather-induced road safety threats.

---

## Project Overview & Context

Traffic safety is highly sensitive to environmental dynamics. While infrastructure engineering and advanced driver assistance systems (ADAS) have steadily mitigated baseline risks, extreme or variable weather events present non-linear hazards to motorists. This project builds a reliable, reproducible research pipeline to systematically evaluate how weather phenomena (ranging from sub-zero frost to high-intensity summer solar radiation) influence risk across different road typologies and German federal states (*Bundesländer*).

The primary analytical dataset for traffic incidents is the official [German Accident Atlas (Unfallatlas)](https://unfallatlas.statistikportal.de/), maintained by the Federal Statistical Office and the Statistical Offices of the Länder. This is combined with high-resolution historical meteorological records to build a comprehensive data pipeline orchestrating preprocessing, spatial joining, risk-ratio estimation, and long-term trend evaluation.

---

## Research Questions

### 1. Weather and Accident Severity (RQ1)
* **Question:** How do varying intensities of precipitation (light drizzle vs. heavy rainfall) and freezing temperatures impact traffic accident frequency and severity, and do they shift the mix of accident types (e.g., loss-of-control accidents vs. collisions)?
* **Objective:** Quantify how specific precipitation thresholds and frost change the accident rate, the share of severe accidents, and the kind of accidents that happen. (Originally we wanted to compare Autobahns against rural roads, but the published Unfallatlas data contains no road-class attribute, so the question was refined to severity and accident types instead.)

### 2. The Threat of the Summer Sun: Sun Glare vs. Heatwaves (RQ2)
* **Question:** To what extent do summer weather factors—specifically high global solar radiation (sun glare) and extreme heatwaves—predict commuter-hour traffic accident rates compared to rainy conditions?
* **Objective:** Move beyond traditional winter-centric risk models to establish the statistical significance of heat-induced cognitive fatigue and low-angle sun glare during peak morning and evening transit windows.

### 3. Spatial Sensitivity & Regional Driving Behavior (RQ3)
* **Question:** Which German states exhibit the strongest sensitivity of traffic accident patterns to changing weather conditions, and how does this sensitivity differ between city states and territorial states?
* **Objective:** Construct a state-level sensitivity index (rain and frost risk ratios per state) to evaluate regional differences between highly urbanized city states (Berlin, Hamburg, Bremen) and the larger territorial states.

### 4. The Evolution of Weather Risk Over Time (RQ4)
* **Question:** How have traffic safety patterns evolved under varying weather conditions in Germany between 2016 and 2024, and has the relative risk of weather-related accidents declined over that period?
* **Objective:** Track the yearly weather risk ratios and severity shares from 2016 to 2024 to see whether adverse weather has become less dangerous over time (for example through modern vehicle safety technology such as ESP and autonomous braking).

---


## Community & Contributing

We welcome community contributions, bug reports, and structural analytical improvements! 

* **Contribution Guidelines:** [Contribution Guide (CONTRIBUTING.md)](CONTRIBUTING.md).

* **Code of Conduct:** In order to ensure a welcoming, inclusive, and collaborative environment for everyone, all project participants and contributors are expected to adhere to our standard [Code of Conduct](CONTRIBUTING.md#code-of-conduct).

---
