import pandas as pd
from sklearn.utils import shuffle

# load datasets
main = pd.read_csv("augmented_dataset_final.csv")
extra = pd.read_csv("new.csv", quotechar='"')

# combine datasets
final = pd.concat([main, extra], ignore_index=True)

# remove duplicate prompts
final = final.drop_duplicates(subset="prompt")

# shuffle dataset
final = shuffle(final, random_state=42)

# reset index (important for clean dataset)
final = final.reset_index(drop=True)

# save dataset
final.to_csv("final_dataset_after_extra.csv", index=False)

print("Final dataset size:", len(final))
print("\nLabel distribution:")
print(final["label"].value_counts())