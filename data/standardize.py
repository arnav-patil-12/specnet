import pandas as pd

INPUT_FILE = "dataset.csv"
OUTPUT_FILE = "data_std.csv"

df = pd.read_csv(INPUT_FILE)

for col in ["gain_max_dB", "gbw"]:
    mu = df[col].mean()
    sigma = df[col].std()
    df[col] = (df[col] - mu) / sigma
    print(f"{col}: mean={mu:.4f}, std={sigma:.4f}")

df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved normalized CSV to {OUTPUT_FILE}")