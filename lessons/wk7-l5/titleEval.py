import os
from dotenv import load_dotenv
import pandas as pd
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval import evaluate

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY not found in environment. Please add it to your .env file.")
    exit(1)

csv_path = "dataset/golden_dataset.csv"
df = pd.read_csv(csv_path)
df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

similarity_metric = GEval(
    name="Title Similarity",
    criteria="Does the generated title convey the same meaning and intent as the reference title?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)
faithfulness_metric = GEval(
    name="Title Faithfulness",
    criteria="Is the generated title factually consistent with the reference title, without introducing hallucinated or incorrect information?",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
    threshold=0.8
)

title_similarity_scores = []
title_similarity_passed = []
title_similarity_reasons = []
title_faithfulness_scores = []
title_faithfulness_passed = []
title_faithfulness_reasons = []

for idx, row in df.iterrows():
    print(f"Evaluating row {idx+1}/{len(df)}...")
    if pd.isna(row["title_generated"]) or pd.isna(row["title_truth"]):
        title_similarity_scores.append(None)
        title_similarity_passed.append(None)
        title_similarity_reasons.append(None)
        title_faithfulness_scores.append(None)
        title_faithfulness_passed.append(None)
        title_faithfulness_reasons.append(None)
        print("  Skipped (missing title data)")
    else:
        # If generated title is a list-like string, extract the first title
        gen_title = row["title_generated"]
        if gen_title.startswith("[") and gen_title.endswith("]"):
            try:
                import ast
                gen_title_list = ast.literal_eval(gen_title)
                if isinstance(gen_title_list, list) and len(gen_title_list) > 0:
                    gen_title = gen_title_list[0]
            except Exception:
                pass

        test_case = LLMTestCase(
            input=row["tldr_truth"],  # Use TLDR as context for title evaluation
            actual_output=gen_title,
            expected_output=row["title_truth"]
        )
        # Similarity evaluation
        sim_result = evaluate(test_cases=[test_case], metrics=[similarity_metric])
        try:
            sim_test_result = sim_result.test_results[0]
            sim_metric_data = sim_test_result.metrics_data[0]
            sim_score = sim_metric_data.score
            sim_passed = sim_metric_data.success
            sim_reason = sim_metric_data.reason
        except Exception as e:
            sim_score = None
            sim_passed = None
            sim_reason = str(e)
        title_similarity_scores.append(sim_score)
        title_similarity_passed.append(sim_passed)
        title_similarity_reasons.append(sim_reason)

        # Faithfulness evaluation
        faith_result = evaluate(test_cases=[test_case], metrics=[faithfulness_metric])
        try:
            faith_test_result = faith_result.test_results[0]
            faith_metric_data = faith_test_result.metrics_data[0]
            faith_score = faith_metric_data.score
            faith_passed = faith_metric_data.success
            faith_reason = faith_metric_data.reason
        except Exception as e:
            faith_score = None
            faith_passed = None
            faith_reason = str(e)
        title_faithfulness_scores.append(faith_score)
        title_faithfulness_passed.append(faith_passed)
        title_faithfulness_reasons.append(faith_reason)

        print(f"  Similarity Score: {sim_score}, Passed: {sim_passed}")
        print(f"  Faithfulness Score: {faith_score}, Passed: {faith_passed}")

df_results = df.copy()
df_results["title_similarity_score"] = title_similarity_scores
df_results["title_similarity_passed"] = title_similarity_passed
df_results["title_similarity_reason"] = title_similarity_reasons
df_results["title_faithfulness_score"] = title_faithfulness_scores
df_results["title_faithfulness_passed"] = title_faithfulness_passed
df_results["title_faithfulness_reason"] = title_faithfulness_reasons

df_results = df_results.loc[:, ~df_results.columns.str.startswith('Unnamed')]

output_csv = "result/title_similarity_faithfulness_results.csv"
df_results.to_csv(output_csv, index=False)
print(f"\nEvaluation results saved to {output_csv}")
