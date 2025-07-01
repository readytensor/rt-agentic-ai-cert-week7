import os
import pandas as pd
import re
from dotenv import load_dotenv
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval import evaluate

# --- Utility functions ---

def extract_titles_from_reference_string(ref_str):
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

def extract_tags(tag_str):
    if pd.isna(tag_str) or not isinstance(tag_str, str):
        return set()
    return set([t.strip().lower() for t in re.split(r"[|,]", tag_str) if t.strip()])

def clean_unnamed(df):
    return df.loc[:, ~df.columns.str.startswith('Unnamed')]

def get_first_title_from_listlike(gen_title):
    # Handles cases like "['Title 1', 'Title 2']"
    if isinstance(gen_title, str) and gen_title.strip().startswith("[") and gen_title.strip().endswith("]"):
        try:
            import ast
            gen_title_list = ast.literal_eval(gen_title)
            if isinstance(gen_title_list, list) and len(gen_title_list) > 0:
                return gen_title_list[0]
        except Exception:
            pass
    return gen_title

# --- Load environment and data ---

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found in environment. Please add it to your .env file.")
    exit(1)

csv_path = "dataset/golden_dataset.csv"
df = pd.read_csv(csv_path)
df = clean_unnamed(df)

# --- Define GEval metrics ---

tldr_judge_metric = GEval(
    name="LLM Judge TLDR",
    criteria="Does the generated TLDR accurately and concisely summarize the main points of the publication as expressed in the reference TLDR?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)
tldr_similarity_metric = GEval(
    name="TLDR Similarity",
    criteria="Does the generated TLDR convey the same meaning as the reference TLDR?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)
tldr_faithfulness_metric = GEval(
    name="TLDR Faithfulness",
    criteria="Is the generated TLDR factually consistent with the reference TLDR, without introducing hallucinated or incorrect information?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)
title_judge_metric = GEval(
    name="LLM Judge Title",
    criteria="Does the generated title accurately and concisely represent the main idea of the publication as expressed in the reference title?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)
title_similarity_metric = GEval(
    name="Title Similarity",
    criteria="Does the generated title convey the same meaning and intent as the reference title?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)
title_faithfulness_metric = GEval(
    name="Title Faithfulness",
    criteria="Is the generated title factually consistent with the reference title, without introducing hallucinated or incorrect information?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)

# --- Prepare result lists ---

tldr_judge_scores, tldr_judge_passed, tldr_judge_reasons = [], [], []
tldr_similarity_scores, tldr_similarity_passed, tldr_similarity_reasons = [], [], []
tldr_faithfulness_scores, tldr_faithfulness_passed, tldr_faithfulness_reasons = [], [], []

title_judge_scores, title_judge_passed, title_judge_reasons = [], [], []
title_similarity_scores, title_similarity_passed, title_similarity_reasons = [], [], []
title_faithfulness_scores, title_faithfulness_passed, title_faithfulness_reasons = [], [], []

tags_jaccard_scores = []
references_jaccard_scores = []

# --- Main evaluation loop ---

for idx, row in df.iterrows():
    print(f"Evaluating row {idx+1}/{len(df)}...")

    # --- TLDR ---
    if pd.isna(row.get("tldr_generated")) or pd.isna(row.get("tldr_truth")):
        tldr_judge_scores.append(None)
        tldr_judge_passed.append(None)
        tldr_judge_reasons.append(None)
        tldr_similarity_scores.append(None)
        tldr_similarity_passed.append(None)
        tldr_similarity_reasons.append(None)
        tldr_faithfulness_scores.append(None)
        tldr_faithfulness_passed.append(None)
        tldr_faithfulness_reasons.append(None)
    else:
        tldr_test_case = LLMTestCase(
            input=row.get("title_truth", ""),
            actual_output=row["tldr_generated"],
            expected_output=row["tldr_truth"]
        )
        # LLM Judge
        judge_result = evaluate(test_cases=[tldr_test_case], metrics=[tldr_judge_metric])
        try:
            test_result = judge_result.test_results[0]
            metric_data = test_result.metrics_data[0]
            tldr_judge_scores.append(metric_data.score)
            tldr_judge_passed.append(metric_data.success)
            tldr_judge_reasons.append(metric_data.reason)
        except Exception as e:
            tldr_judge_scores.append(None)
            tldr_judge_passed.append(None)
            tldr_judge_reasons.append(str(e))
        # Similarity
        sim_result = evaluate(test_cases=[tldr_test_case], metrics=[tldr_similarity_metric])
        try:
            test_result = sim_result.test_results[0]
            metric_data = test_result.metrics_data[0]
            tldr_similarity_scores.append(metric_data.score)
            tldr_similarity_passed.append(metric_data.success)
            tldr_similarity_reasons.append(metric_data.reason)
        except Exception as e:
            tldr_similarity_scores.append(None)
            tldr_similarity_passed.append(None)
            tldr_similarity_reasons.append(str(e))
        # Faithfulness
        faith_result = evaluate(test_cases=[tldr_test_case], metrics=[tldr_faithfulness_metric])
        try:
            test_result = faith_result.test_results[0]
            metric_data = test_result.metrics_data[0]
            tldr_faithfulness_scores.append(metric_data.score)
            tldr_faithfulness_passed.append(metric_data.success)
            tldr_faithfulness_reasons.append(metric_data.reason)
        except Exception as e:
            tldr_faithfulness_scores.append(None)
            tldr_faithfulness_passed.append(None)
            tldr_faithfulness_reasons.append(str(e))

    # --- TITLE ---
    if pd.isna(row.get("title_generated")) or pd.isna(row.get("title_truth")):
        title_judge_scores.append(None)
        title_judge_passed.append(None)
        title_judge_reasons.append(None)
        title_similarity_scores.append(None)
        title_similarity_passed.append(None)
        title_similarity_reasons.append(None)
        title_faithfulness_scores.append(None)
        title_faithfulness_passed.append(None)
        title_faithfulness_reasons.append(None)
    else:
        gen_title = get_first_title_from_listlike(row["title_generated"])
        title_test_case = LLMTestCase(
            input=row.get("tldr_truth", ""),
            actual_output=gen_title,
            expected_output=row["title_truth"]
        )
        # LLM Judge
        judge_result = evaluate(test_cases=[title_test_case], metrics=[title_judge_metric])
        try:
            test_result = judge_result.test_results[0]
            metric_data = test_result.metrics_data[0]
            title_judge_scores.append(metric_data.score)
            title_judge_passed.append(metric_data.success)
            title_judge_reasons.append(metric_data.reason)
        except Exception as e:
            title_judge_scores.append(None)
            title_judge_passed.append(None)
            title_judge_reasons.append(str(e))
        # Similarity
        sim_result = evaluate(test_cases=[title_test_case], metrics=[title_similarity_metric])
        try:
            test_result = sim_result.test_results[0]
            metric_data = test_result.metrics_data[0]
            title_similarity_scores.append(metric_data.score)
            title_similarity_passed.append(metric_data.success)
            title_similarity_reasons.append(metric_data.reason)
        except Exception as e:
            title_similarity_scores.append(None)
            title_similarity_passed.append(None)
            title_similarity_reasons.append(str(e))
        # Faithfulness
        faith_result = evaluate(test_cases=[title_test_case], metrics=[title_faithfulness_metric])
        try:
            test_result = faith_result.test_results[0]
            metric_data = test_result.metrics_data[0]
            title_faithfulness_scores.append(metric_data.score)
            title_faithfulness_passed.append(metric_data.success)
            title_faithfulness_reasons.append(metric_data.reason)
        except Exception as e:
            title_faithfulness_scores.append(None)
            title_faithfulness_passed.append(None)
            title_faithfulness_reasons.append(str(e))

    # --- TAGS ---
    tags_truth = extract_tags(row.get("tags_truth", ""))
    tags_generated = extract_tags(row.get("tags_generated", ""))
    tags_jaccard_scores.append(jaccard_similarity(tags_truth, tags_generated))

    # --- REFERENCES ---
    refs_truth = extract_titles_from_reference_string(row.get("references_truth", ""))
    refs_generated = extract_titles_from_reference_string(row.get("references_generated", ""))
    references_jaccard_scores.append(jaccard_similarity(refs_truth, refs_generated))

# --- Save results ---

df_results = df.copy()
df_results["tldr_judge_score"] = tldr_judge_scores
df_results["tldr_judge_passed"] = tldr_judge_passed
df_results["tldr_judge_reason"] = tldr_judge_reasons
df_results["tldr_similarity_score"] = tldr_similarity_scores
df_results["tldr_similarity_passed"] = tldr_similarity_passed
df_results["tldr_similarity_reason"] = tldr_similarity_reasons
df_results["tldr_faithfulness_score"] = tldr_faithfulness_scores
df_results["tldr_faithfulness_passed"] = tldr_faithfulness_passed
df_results["tldr_faithfulness_reason"] = tldr_faithfulness_reasons

df_results["title_judge_score"] = title_judge_scores
df_results["title_judge_passed"] = title_judge_passed
df_results["title_judge_reason"] = title_judge_reasons
df_results["title_similarity_score"] = title_similarity_scores
df_results["title_similarity_passed"] = title_similarity_passed
df_results["title_similarity_reason"] = title_similarity_reasons
df_results["title_faithfulness_score"] = title_faithfulness_scores
df_results["title_faithfulness_passed"] = title_faithfulness_passed
df_results["title_faithfulness_reason"] = title_faithfulness_reasons

df_results["tags_jaccard_similarity"] = tags_jaccard_scores
df_results["references_jaccard_similarity"] = references_jaccard_scores

df_results = clean_unnamed(df_results)

output_csv = "result/full_evaluation_results.csv"
df_results.to_csv(output_csv, index=False)
print(f"\nAll evaluation results saved to {output_csv}")
