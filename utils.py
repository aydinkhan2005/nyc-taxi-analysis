import geopandas as gpd
from shapely.geometry import Point
from pyspark.sql.functions import coalesce, lit
def add_stations(station_data, df, spark):

    # ---------------------------------------------------------
    # 1. Read taxi zone polygons
    # ---------------------------------------------------------
    taxi_zones_geo = gpd.read_file(
        "data/taxi_zones/taxi_zones.shp"
    )

    # ---------------------------------------------------------
    # 2. Convert station_data from Spark -> Pandas
    # ---------------------------------------------------------
    stations_pd = station_data.toPandas()

    stations_pd["GTFS Latitude"] = stations_pd["GTFS Latitude"].astype(float)
    stations_pd["GTFS Longitude"] = stations_pd["GTFS Longitude"].astype(float)

    # ---------------------------------------------------------
    # 3. Create GeoDataFrame of subway stations
    # ---------------------------------------------------------
    stations_geo = gpd.GeoDataFrame(
        stations_pd,
        geometry=[
            Point(lon, lat)
            for lon, lat in zip(
                stations_pd["GTFS Longitude"],
                stations_pd["GTFS Latitude"]
            )
        ],
        crs="EPSG:4326"
    )

    # ---------------------------------------------------------
    # 4. Make sure both GeoDataFrames use the same CRS
    # ---------------------------------------------------------
    taxi_zones_geo = taxi_zones_geo.to_crs(stations_geo.crs)

    # ---------------------------------------------------------
    # 5. Assign each station to a taxi zone
    # ---------------------------------------------------------
    station_zones = gpd.sjoin(
        stations_geo,
        taxi_zones_geo[["LocationID", "geometry"]],
        how="left",
        predicate="within"
    )

    # ---------------------------------------------------------
    # 6. Count stations in each taxi zone
    # ---------------------------------------------------------
    station_counts = (
        station_zones
        .dropna(subset=["LocationID"])
        .groupby("LocationID")
        .size()
        .reset_index(name="num_stations")
    )

    station_counts["LocationID"] = station_counts["LocationID"].astype(int)

    # ---------------------------------------------------------
    # 7. Convert station counts back to Spark
    # ---------------------------------------------------------
    station_counts_spark = spark.createDataFrame(
        station_counts
    )

    # ---------------------------------------------------------
    # 8. Join station counts to the input DataFrame
    # ---------------------------------------------------------
    df = (
        df
        .join(
            station_counts_spark,
            df.PULocationID == station_counts_spark.LocationID,
            "left"
        )
        .drop("LocationID")
    )

    # ---------------------------------------------------------
    # 9. Zones without stations get 0
    # ---------------------------------------------------------
    df = df.withColumn(
        "num_stations",
        coalesce("num_stations", lit(0))
    )

    return df

def add_unemployment_rate(df, spark):
    from pyspark.sql import functions as F
    # ---------------------------------------------------------
    # 1. Create Year and Month from pickup timestamp
    # ---------------------------------------------------------
    df = (
        df
        .withColumn("Year", F.year("date"))
        .withColumn("Month", F.month("date"))
    )

    # ---------------------------------------------------------
    # 2. Read unemployment data
    # ---------------------------------------------------------
    unemployment = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv("data/unemployment.csv")
    )

    # ---------------------------------------------------------
    # 3. Read taxi zone lookup
    # ---------------------------------------------------------
    taxi_zones = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv("data/taxi_zone_lookup.csv")
    )

    # ---------------------------------------------------------
    # 4. Map taxi borough -> county name
    # ---------------------------------------------------------
    taxi_zones = taxi_zones.withColumn(
        "Area Name",
        F.when(F.col("Borough") == "Bronx", "Bronx County")
         .when(F.col("Borough") == "Brooklyn", "Kings County")
         .when(F.col("Borough") == "Manhattan", "New York County")
         .when(F.col("Borough") == "Queens", "Queens County")
         .when(F.col("Borough") == "Staten Island", "Richmond County")
    )

    # ---------------------------------------------------------
    # 5. Clean unemployment data
    # ---------------------------------------------------------

    # Convert "4.2%" -> 4.2
    unemployment = unemployment.withColumn(
        "unemployment_rate",
        F.regexp_replace(
            F.col("Unemployment Rate"),
            "%",
            ""
        ).cast("double")
    )

    # Make Year an integer
    unemployment = unemployment.withColumn(
        "Year",
        F.col("Year").cast("int")
    )

    # Convert "January", "February", etc. -> 1, 2, ...
    unemployment = unemployment.withColumn(
        "Month",
        F.month(
            F.to_date(
                F.concat(
                    F.lit("1 "),
                    F.col("Month"),
                    F.lit(" 2000")
                ),
                "d MMMM yyyy"
            )
        )
    )

    # ---------------------------------------------------------
    # 6. Create borough/year/month unemployment lookup
    # ---------------------------------------------------------
    borough_unemployment = (
        unemployment
        .select(
            "Area Name",
            "Year",
            "Month",
            "unemployment_rate"
        )
    )

    # ---------------------------------------------------------
    # 7. Attach unemployment data to each taxi zone
    # ---------------------------------------------------------
    zone_unemployment = (
        taxi_zones
        .join(
            borough_unemployment,
            on="Area Name",
            how="left"
        )
        .select(
            "LocationID",
            "Year",
            "Month",
            "unemployment_rate"
        )
    )

    # ---------------------------------------------------------
    # 8. Join unemployment rate onto df
    # ---------------------------------------------------------
    df = (
        df.alias("df")
        .join(
            zone_unemployment.alias("zu"),
            (F.col("df.PULocationID") == F.col("zu.LocationID"))
            & (F.col("df.Year") == F.col("zu.Year"))
            & (F.col("df.Month") == F.col("zu.Month")),
            how="left"
        )
        .select(
            "df.*",
            "zu.unemployment_rate"
        )
    )
    df = df.withColumn(
    "unemployment_rate",
    F.when(
        F.col("PULocationID") == 1,
        F.lit(0.0)
    ).otherwise(F.col("unemployment_rate"))
    )

    return df