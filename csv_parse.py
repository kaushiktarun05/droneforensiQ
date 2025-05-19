import os
import pandas as pd

def fill_missing_values(csv_file_path, output_folder):
    """
    Reads the CSV file, fills missing values (empty cells) with zeroes,
    and saves the corrected file in the output folder.
    """
    try:
        # Read CSV using Pandas, treating empty values as NaN
        df = pd.read_csv(csv_file_path, dtype=str)  # Read as string to prevent type inference

        # Replace empty values (NaN) with '0'
        df.fillna("0", inplace=True)

        # Define final CSV path
        final_csv_path = os.path.join(output_folder, os.path.basename(csv_file_path))

        # Save the cleaned data
        df.to_csv(final_csv_path, index=False)

        return final_csv_path

    except Exception as e:
        print(f"Error processing CSV: {e}")
        return None
