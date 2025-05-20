import pandas as pd
from analysis.models import DrugSale

# Map of filenames and their frequencies
FILES = {
    'salesmonthly.csv': 'monthly',
    'salesweekly.csv': 'weekly',
    'salesdaily.csv': 'daily',
    'saleshourly.csv': 'hourly',
}

# ATC code to drug name mapping
ATC_TO_NAME = {
    'M01AB': 'Anti-inflammatory, non-steroids - Acetic acid derivatives',
    'M01AE': 'Anti-inflammatory, non-steroids - Propionic acid derivatives',
    'N02BA': 'Other analgesics - Salicylic acid derivatives',
    'N02BE': 'Other analgesics - Pyrazolones and Anilides',
    'N05B': 'Psycholeptics - Anxiolytic drugs',
    'N05C': 'Psycholeptics - Hypnotics and sedatives',
    'R03': 'Drugs for obstructive airway diseases',
    'R06': 'Antihistamines for systemic use',
}

for filename, freq in FILES.items():
    print(f"Importing {filename} as {freq} data...")
    path = f'analysis/data/{filename}'
    df = pd.read_csv(path, parse_dates=['datum'])

    atc_columns = [col for col in df.columns if col in ATC_TO_NAME]

    # Melt the wide format into long format
    melted = df.melt(id_vars=['datum'], value_vars=atc_columns,
                     var_name='atc_code', value_name='quantity')

    # Drop any rows with missing quantities
    melted.dropna(subset=['quantity'], inplace=True)

    # Optional: round or cast quantities
    melted['quantity'] = melted['quantity'].astype(int)

    # Prepare data for bulk insert
    records = [
        DrugSale(
            datetime=row['datum'],
            drug_name=ATC_TO_NAME.get(row['atc_code'], 'Unknown'),
            quantity=row['quantity'],
            atc_code=row['atc_code'],
            frequency=freq
        )
        for _, row in melted.iterrows()
    ]

    # Insert in batches
    DrugSale.objects.bulk_create(records, batch_size=1000)
    print(f"Imported {len(records)} records from {filename}")
