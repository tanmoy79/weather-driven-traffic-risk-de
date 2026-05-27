# Weather-Driven Traffic Risk in Germany (`weather-driven-traffic-risk-de`)

This project is part of the course **"Research Software Engineering (RSE)"**, taught by Prof. Dr. Anna-Lena Lamprecht at the University of Potsdam.

A reproducible data pipeline and empirical analysis exploring the structural, environmental, spatial, and temporal relationships between adverse weather conditions and traffic accident dynamics across Germany. By leveraging historical meteorological data alongside spatialized accident coordinates, this repository automates data ingestion, cleaning, multi-criteria risk modeling, and regression analyses to quantify weather-induced road safety threats.

---

## Project Overview & Context

Traffic safety is highly sensitive to environmental dynamics. While infrastructure engineering and advanced driver assistance systems (ADAS) have steadily mitigated baseline risks, extreme or variable weather events present non-linear hazards to motorists. This project builds a reliable, reproducible research pipeline to systematically evaluate how weather phenomena (ranging from sub-zero frost to high-intensity summer solar radiation) influence risk across different road typologies and German federal states (*Bundesländer*).

The primary analytical dataset for traffic incidents is the official [German Accident Atlas (Unfallatlas)](https://unfallatlas.statistikportal.de/), maintained by the Federal Statistical Office and the Statistical Offices of the Länder. This is combined with high-resolution historical meteorological records to build a comprehensive data pipeline orchestrating preprocessing, spatial joining, risk-ratio estimation, and long-term trend evaluation.

---

## Research Questions

### 1. Infrastructure Vulnerability: Autobahn vs. Rural Roads (RQ1)
* **Question:** How do varying intensities of precipitation (light drizzle vs. heavy rainfall) and freezing temperatures differentially impact traffic accident frequency and severity on German Autobahns compared to rural roads (*Landstraßen*)?
* **Objective:** Quantify the interaction effect between roadway typology and specific precipitation thresholds, isolating how structural properties (e.g., drainage, lane width, speed limits) attenuate or exacerbate weather risks.

### 2. The Threat of the Summer Sun: Sun Glare vs. Heatwaves (RQ2)
* **Question:** To what extent do summer weather factors—specifically high global solar radiation (sun glare) and extreme heatwaves—predict commuter-hour traffic accident rates compared to rainy conditions?
* **Objective:** Move beyond traditional winter-centric risk models to establish the statistical significance of heat-induced cognitive fatigue and low-angle sun glare during peak morning and evening transit windows.

### 3. Spatial Sensitivity & Regional Driving Behavior (RQ3)
* **Question:** Which German states exhibit the strongest sensitivity of traffic accident patterns to changing weather conditions, and how does this sensitivity differ between highly urbanized and less densely populated federal states?
* **Objective:** Construct a state-level sensitivity index to evaluate regional resilience, correlating local risk variances with regional geographic profiles (e.g., urban micro-climates vs. topography-driven weather spikes).

### 4. The Evolution of Weather Risk Over Time (RQ4)
* **Question:** How have traffic safety patterns evolved under varying weather conditions in Germany over the past decade, and has the relative risk of weather-related accidents declined due to modern vehicle safety technology?
* **Objective:** Execute a time-series decomposition of accident-to-weather coefficients from the past decade to test whether active safety systems (such as ESP, autonomous braking, and lane-keep assist) have successfully decoupled adverse weather from high casualty counts.

---


## Community & Contributing

We welcome community contributions, bug reports, and structural analytical improvements! 

* **Contribution Guidelines:** [Contribution Guide (CONTRIBUTING.md)](CONTRIBUTING.md).

* **Code of Conduct:** In order to ensure a welcoming, inclusive, and collaborative environment for everyone, all project participants and contributors are expected to adhere to our standard [Code of Conduct](CONTRIBUTING.md#code-of-conduct).

---
