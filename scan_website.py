import pandas as pd

from scan import scan

def read_csv_file():
    # read csv file using pandas
    df = pd.read_csv("websites.csv")
    # return pandas dataframe
    return df

def main():
    df = read_csv_file()
    # convert pandas dataframe to numpy array for faster processing
    website_list = df['Website'].values
    for website in website_list:
        scan(df, website)
    return None

if __name__ == "__main__":
    main()