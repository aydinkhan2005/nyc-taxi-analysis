<img src="https://img.shields.io/badge/PySpark-FFB84D?style=for-the-badge" alt="PySpark"> <img src="https://img.shields.io/badge/StatsModels-4A235A?style=for-the-badge" alt="StatsModels"> <img src="https://img.shields.io/badge/Pandas-1F4788?style=for-the-badge" alt="Pandas"> <img src="https://img.shields.io/badge/Matplotlib-2ECC71?style=for-the-badge" alt="Matplotlib">
# Instructions to run repository

1. Download dependencies using the command:
``pip install -r requirements.txt``

2. Run the Jupyter notebooks


# Dataset sources
- NYC TLC datasets: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- MapPLUTO: https://hub.arcgis.com/datasets/DCP::mappluto-1/about
- MTA Subway Stations: https://catalog.data.gov/dataset/mta-subway-stations

# Repository structure
- ``preprocessing.ipynb``: Notebook for cleaning the datasets.
- ``eda.ipynb``: Notebook for exploring the data. Contains box plots, chloropleth maps, etc.
- ``modelling.ipynb``: Notebook for training and evaluating the two models.
- ``data/``: Folder which contains the raw parquet and CSV files.
- ``cleaned_data/``: Contains the preprocessed training and testing data.
- ``utils.py``: Python script for utility functions.
- ``Images/``: Folder which contains plot images, of which some are used in the report.

# Reference list
* GeeksforGeeks. "Implementing Generalized Least Squares (GLS) in Python." *GeeksforGeeks*, 23 July 2025, https://www.geeksforgeeks.org/machine-learning/implementing-generalized-least-squares-gls-in-python/. Accessed 30 Aug. 2026.
* Maddula, Srujana. "Random Forest Regression: A Complete Guide." *DataCamp*, June 2026, https://www.datacamp.com/tutorial/random-forest-regression. Accessed 27 Aug. 2026.
* Metropolitan Transportation Authority. *MTA Subway Stations*. State of New York Open Data, 2024, https://catalog.data.gov/dataset/mta-subway-stations. Accessed 30 Aug. 2026.
* New York City Department of City Planning. *MapPLUTO*. 2016, https://hub.arcgis.com/datasets/DCP::mappluto-1/about. Accessed 29 Aug. 2026.
* New York City Taxi and Limousine Commission. *Taxi Zone Lookup Table*. 2026, https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page. Accessed 27 Aug. 2026.
* New York City Taxi and Limousine Commission. *Taxi Zone Shapefile*. 2026, https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page. Accessed 27 Aug. 2026.
* New York City Taxi and Limousine Commission. *TLC Trip Record Data*. 2026, https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page. Accessed 1 May 2026.
* scikit-learn developers. "sklearn.model_selection.TimeSeriesSplit Documentation." *scikit-learn*, 2026, https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html. Accessed 31 Aug. 2026.
* "Generalized Least Squares." Wikipedia, Wikimedia Foundation, 2026, https://en.wikipedia.org/wiki/Generalized_least_squares. Accessed 31 Aug. 2026.
