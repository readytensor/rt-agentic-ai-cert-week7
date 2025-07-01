import pandas as pd
import re

def extract_titles_from_reference_string(ref_str):
    """
    Extracts all 'title' fields from a string representation of Reference objects or Markdown links.
    Returns a set of lowercased titles.
    """
    if pd.isna(ref_str) or not isinstance(ref_str, str) or not ref_str.strip():
        return set()
    titles = set()
    for match in re.finditer(r"title=([\"'])(.*?)\1", ref_str):
        titles.add(match.group(2).strip().lower())
    for match in re.finditer(r"\[([^\]]+)\]\([^)]+\)", ref_str):
        titles.add(match.group(1).strip().lower())
    return titles

def jaccard_similarity(set1, set2):
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)

# Load your dataset
df = pd.read_csv("dataset/golden_dataset.csv")
df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

jaccard_scores = []

for idx, row in df.iterrows():
    truth_titles = extract_titles_from_reference_string(row.get("references_truth", ""))
    gen_titles = extract_titles_from_reference_string(row.get("references_generated", ""))
    score = jaccard_similarity(truth_titles, gen_titles)
    jaccard_scores.append(score)

df["references_jaccard_similarity"] = jaccard_scores
df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

output_csv = "result/references_jaccard_similarity_results.csv"
df.to_csv(output_csv, index=False)
print(f"Jaccard similarity results saved to {output_csv}")
