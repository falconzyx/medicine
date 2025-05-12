import pandas as pd

# Read the Excel file with optimized settings
print("Starting conversion...")
df = pd.read_excel('vw_equipment_phsa (2).xlsx', engine='openpyxl')

# Save to CSV in the raw data folder
print("Saving to CSV...")
df.to_csv('raw data/equipment_data.csv', index=False)
print("Conversion completed successfully!")
