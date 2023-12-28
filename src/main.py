""" as primeagean said, I just have a main that only imports functions """
# getting the data from https://aqs.epa.gov/aqsweb/documents/data_api.html
import get_sites

if __name__ == "__main__":
    file_site = "data/aqs_monitors.csv"
    df_site = get_sites.filter_sites(file_site)
    # I think the important things I want from this data frame are
    # I am taking out Site Number because that will be placed back in
    # later because it will be an index from the function groupby
    cols = ["State Code", "County Code"]
    df_site = df_site.groupby("Site Number").apply(lambda x: x[cols])
    df_site.reset_index(inplace=True, level=0)
    df_site.drop_duplicates(subset=None, keep="first", inplace=True)
    print(df_site)
