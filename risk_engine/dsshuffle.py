import pandas as pd
from sklearn.utils import shuffle

# -----------------------------
# Step 1: Load datasets
# -----------------------------
existing = pd.read_csv("PromptShield.csv")
generated = pd.read_csv("prompts.csv")

print("Existing dataset columns:", existing.columns)
print("Generated dataset columns:", generated.columns)

# -----------------------------
# Step 2: Keep only needed columns
# -----------------------------
existing = existing[['prompt', 'label']]
generated = generated[['prompt', 'label']]

# -----------------------------
# Step 3: Select 70% existing data
# -----------------------------
existing_sample = existing.sample(frac=0.7, random_state=42)

# -----------------------------
# Step 4: Select 30% generated data
# -----------------------------
generated_sample = generated.sample(frac=0.3, random_state=42)

# -----------------------------
# Step 5: Combine datasets
# -----------------------------
combined = pd.concat([existing_sample, generated_sample])

# -----------------------------
# Step 6: Shuffle dataset
# -----------------------------
combined = shuffle(combined, random_state=42)
combined = combined.drop_duplicates(subset=['prompt'])
# -----------------------------
# Step 7: Save final dataset
# -----------------------------
combined.to_csv("final_dataset.csv", index=False)

print("Dataset created successfully!")
print("Total samples:", len(combined))
print(combined.head())

# -----------------------------
# Step 8: Check label distribution
# -----------------------------
print("\nLabel distribution:")
print(combined['label'].value_counts())