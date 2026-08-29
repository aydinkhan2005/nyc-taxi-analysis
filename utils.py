import geopandas as gpd
from shapely.geometry import Point
from pyspark.sql.functions import coalesce, lit
def add_stations(df, spark):
    """
    Add the number of subway stations in each taxi zone to the input DataFrame.
    
    Parameters:
    - df: Spark DataFrame containing taxi trip data with 'PULocationID' column.
    - spark: SparkSession object.

    Returns:
    - Spark DataFrame with an additional column 'num_stations' indicating the number of subway stations in each taxi zone.
    """

    station_data = spark.read.csv('data/station_data.csv', header=True, inferSchema=True)
    # Read taxi zone polygons
    taxi_zones_geo = gpd.read_file(
        "data/taxi_zones/taxi_zones.shp"
    )

    # Convert station_data from Spark -> Pandas
    stations_pd = station_data.toPandas()

    stations_pd["GTFS Latitude"] = stations_pd["GTFS Latitude"].astype(float)
    stations_pd["GTFS Longitude"] = stations_pd["GTFS Longitude"].astype(float)

    # Create GeoDataFrame of subway stations
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

    # Make sure both GeoDataFrames use the same CRS
    taxi_zones_geo = taxi_zones_geo.to_crs(stations_geo.crs)

    # Assign each station to a taxi zone
    station_zones = gpd.sjoin(
        stations_geo,
        taxi_zones_geo[["LocationID", "geometry"]],
        how="left",
        predicate="within"
    )

    # Count stations in each taxi zone
    station_counts = (
        station_zones
        .dropna(subset=["LocationID"])
        .groupby("LocationID")
        .size()
        .reset_index(name="num_stations")
    )

    station_counts["LocationID"] = station_counts["LocationID"].astype(int)

    # Convert station counts back to Spark
    station_counts_spark = spark.createDataFrame(
        station_counts
    )

    # Join station counts to the input DataFrame
    df = (
        df
        .join(
            station_counts_spark,
            df.PULocationID == station_counts_spark.LocationID,
            "left"
        )
        .drop("LocationID")
    )

    # Zones without stations get 0
    df = df.withColumn(
        "num_stations",
        coalesce("num_stations", lit(0))
    )

    return df