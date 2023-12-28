import pandas as pd


# GPS location, I need to make sure that the sites I am getting data from are in the proper locations
# SITE_LATITUDE  SITE_LONGITUDE
# The Corners are bottom left 40.453217,-112.142944,top right: 40.809652,-111.818848


def detection_logic(SITE_LATITUDE: float, SITE_LONGITUDE: float) -> bool:
    # only works because it is a rectangle and the sides are not at angles
    bottom_latitude: float = 40.453217
    top_latitude: float = 40.809652
    left_longitude: float = -112.142944
    right_longitude: float = -111.818848

    if (SITE_LATITUDE > bottom_latitude) & (SITE_LATITUDE < top_latitude):
        if (SITE_LONGITUDE < right_longitude) & (SITE_LONGITUDE > left_longitude):
            return True

    return False


def filter_sites(site):
    df = pd.read_csv(site, low_memory=False)
    df.sample(5)
    site_data = df[
        df.apply(
            lambda row: detection_logic(row["Latitude"], row["Longitude"]),
            axis=1,
        )
    ]
    # I think the important things I want from this data frame are
    # I am taking out Site Number because that will be placed back in
    # later because it will be an index from the function groupby
    cols = ["State Code", "County Code"]
    df_site = site_data.groupby("Site Number").apply(lambda x: x[cols])
    df_site.reset_index(inplace=True, level=0)
    df_site.drop_duplicates(subset=None, keep="first", inplace=True)
    return df_site


if __name__ == "__main__":
    filter_sites("data/aqs_monitors.csv")
