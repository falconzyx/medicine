import pandas as pd
import numpy as np

print("Loading data...")
df = pd.read_csv('raw data/equipment_data.csv')

print("\nBasic Information:")
print("-----------------")
print(f"Number of rows: {len(df)}")
print(f"Number of columns: {len(df.columns)}")

print("\nColumns and their data types:")
print("---------------------------")
for col in df.columns:
    non_null = df[col].count()
    null_count = df[col].isnull().sum()
    unique_count = df[col].nunique()
    print(f"\nColumn: {col}")
    print(f"Data type: {df[col].dtype}")
    print(f"Non-null count: {non_null}")
    print(f"Null count: {null_count}")
    print(f"Unique values: {unique_count}")
    
    # Show sample values for non-numeric columns
    if df[col].dtype == 'object':
        sample_values = df[col].dropna().sample(min(3, unique_count)).tolist()
        print(f"Sample values: {sample_values}")
    # Show basic statistics for numeric columns
    elif np.issubdtype(df[col].dtype, np.number):
        print(f"Min: {df[col].min()}")
        print(f"Max: {df[col].max()}")
        print(f"Mean: {df[col].mean():.2f}")
