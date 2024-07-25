import pandas as pd


def merge_csv_files(file_list, output_file):
    """Merge multiple CSV files into a single CSV file."""
    # Initialize an empty list to store dataframes
    dataframes = []

    # Read each CSV file and append its dataframe to the list
    for file in file_list:
        df = pd.read_csv(file)
        dataframes.append(df)

    # Concatenate all dataframes into one
    merged_df = pd.concat(dataframes, ignore_index=True)

    # Save the merged dataframe to a new CSV file
    merged_df.to_csv(output_file, index=False)
    print(f"Merged CSV saved to {output_file}")


# List of CSV files to be merged
csv_files = [
    "../training_data/cpu_training_data.csv",
    "../training_data/ram_training_data.csv",
    "../training_data/motherboard_training_data.csv",
    "../training_data/ssd_training_data.csv",
]

# Output file name
output_csv_file = "../data/merged_data.csv"

# Merge the CSV files
merge_csv_files(csv_files, output_csv_file)
