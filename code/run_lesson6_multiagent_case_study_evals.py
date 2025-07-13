import ast
import numpy as np
import asyncio
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import SemanticSimilarity, Faithfulness
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import OpenAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from dotenv import load_dotenv
from llm import get_llm

# Import your custom coherence metric
from coherence import ContentCoherenceMetric, CoherenceInput

# Import utility functions
from utils import (
    truncate_context,
    load_dataset,
    load_publication_descriptions,
    print_evaluation_scores,
    save_evaluation_results,
    print_evaluation_summary,
    initialize_result_dict,
    prepare_text_for_semantic_similarity,
    load_config,
)

config = load_config()

llm = get_llm(config.get("llm", "gpt-4o-mini"))
num_publications_to_evaluate = config.get("num_publications_to_evaluate", 2)


def jaccard_score(list1, list2):
    """
    Computes Jaccard similarity between two lists.
    """
    set1 = set(list1)
    set2 = set(list2)

    intersection = set1 & set2
    union = set1 | set2

    if not union:
        return 0.0  # define as 0 if both are empty
    return len(intersection) / len(union)


load_dotenv()


async def evaluate_semantic_similarity(generated_text, truth_text, metric_name):
    """Evaluate semantic similarity between generated and truth text."""
    # Create semantic similarity scorer
    evaluator_embedding = OpenAIEmbeddings(model="text-embedding-ada-002")
    semantic_scorer = SemanticSimilarity(
        embeddings=LangchainEmbeddingsWrapper(evaluator_embedding)
    )

    if isinstance(generated_text, list):
        scores = {f"{metric_name}_semantic_similarity": []}
        for item in generated_text:
            sample = SingleTurnSample(
                user_input="dummy", response=str(item), reference=str(truth_text)
            )
            score = await semantic_scorer.single_turn_ascore(sample)
            scores[f"{metric_name}_semantic_similarity"].append(score)
        scores[f"{metric_name}_semantic_similarity_mean"] = np.mean(
            scores[f"{metric_name}_semantic_similarity"]
        )
        return scores
    else:
        sample = SingleTurnSample(
            user_input="dummy", response=str(generated_text), reference=str(truth_text)
        )
        score = await semantic_scorer.single_turn_ascore(sample)
        return {f"{metric_name}_semantic_similarity": score}


async def evaluate_faithfulness(generated_text, context, user_input, metric_name):
    """Evaluate faithfulness of generated text against the context."""
    # Create faithfulness scorer
    evaluator_llm = LangchainLLMWrapper(llm)
    faithfulness_scorer = Faithfulness(llm=evaluator_llm)

    if isinstance(generated_text, list):
        scores = {f"{metric_name}_faithfulness": []}
        for item in generated_text:
            sample = SingleTurnSample(
                user_input=user_input,
                response=str(item),
                retrieved_contexts=[context] if context else [""],
            )
            score = await faithfulness_scorer.single_turn_ascore(sample)
            scores[f"{metric_name}_faithfulness"].append(score)
        scores[f"{metric_name}_faithfulness_mean"] = np.mean(
            scores[f"{metric_name}_faithfulness"]
        )
        return scores
    else:
        sample = SingleTurnSample(
            user_input=user_input,
            response=str(generated_text),
            retrieved_contexts=[context] if context else [""],
        )
        score = await faithfulness_scorer.single_turn_ascore(sample)
        return {f"{metric_name}_faithfulness": score}


async def evaluate_jaccard_similarity(generated_text, truth_text, metric_name):
    """Evaluate Jaccard similarity between generated and truth text."""

    updated_generated_text = generated_text
    updated_truth_text = truth_text
    if metric_name == "references":
        updated_generated_text = [i["url"] for i in generated_text]
        updated_truth_text = [i["url"] for i in truth_text]

    return {
        f"{metric_name}_jaccard_similarity": jaccard_score(
            updated_generated_text, updated_truth_text
        )
    }


async def evaluate_content_coherence(
    context, title_generated, tldr_generated, references_generated, tags_generated
):
    """Evaluate content coherence using the custom ContentCoherenceMetric."""
    # Create coherence scorer
    evaluator_llm = LangchainLLMWrapper(llm)
    coherence_scorer = ContentCoherenceMetric(llm=evaluator_llm)
    if not context:
        print("Warning: No context provided for coherence evaluation")
        return {"content_coherence": 0.0}

    # Create custom sample for coherence evaluation
    coherence_sample = CoherenceInput(
        context=context,
        title_generated=str(title_generated),
        tldr_generated=str(tldr_generated),
        references_generated=str(references_generated),
        tags_generated=str(tags_generated),
    )

    # Evaluate coherence using the custom metric
    score = await coherence_scorer._single_turn_ascore(coherence_sample, callbacks=None)
    return {"content_coherence": score}


async def evaluate_dataset(num_publications_to_evaluate: int = 2):
    """Evaluate the golden dataset with semantic similarity, Jaccard metrics, faithfulness, and content coherence."""

    # Load data using utility functions
    df = load_dataset(num_publications_to_evaluate=num_publications_to_evaluate)
    pub_descriptions = load_publication_descriptions()

    # Results storage
    results = []

    print(f"Evaluating {len(df)} publications...")

    for index, row in df.iterrows():
        print(
            f"Processing publication {index + 1}/{len(df)}: {row['publication_external_id']}"
        )

        title_generated = ast.literal_eval(row["title_generated"])
        tldr_generated = ast.literal_eval(row["tldr_generated"])
        references_generated = ast.literal_eval(row["references_generated"])
        references_truth = ast.literal_eval(row["references_truth"])
        tags_generated = row["tags_generated"]

        try:
            # Get publication description for context and truncate if needed
            pub_id = row["publication_external_id"]
            raw_context = pub_descriptions.get(pub_id, "")
            context = truncate_context(raw_context, max_tokens=8000)

            if len(raw_context) > len(context):
                print(
                    f"  Warning: Context truncated from {len(raw_context)} to {len(context)} characters"
                )

            # Initialize result dictionary using utility function
            result = {
                "publication_external_id": row["publication_external_id"],
            }

            # Title Evaluation
            title_semantic = await evaluate_semantic_similarity(
                title_generated, row["title_truth"], "title"
            )
            result.update(title_semantic)

            title_faithfulness = await evaluate_faithfulness(
                title_generated,
                context,
                "Generate a concise and accurate title for the given content.",
                "title",
            )
            result.update(title_faithfulness)

            # TLDR Evaluation
            tldr_semantic = await evaluate_semantic_similarity(
                tldr_generated, row["tldr_truth"], "tldr"
            )
            result.update(tldr_semantic)

            tldr_faithfulness = await evaluate_faithfulness(
                tldr_generated,
                context,
                "Provide a concise summary (TL;DR) for the given content that captures the main points and key takeaways.",
                "tldr",
            )
            result.update(tldr_faithfulness)

            # References Evaluation
            references_semantic = await evaluate_semantic_similarity(
                references_generated, row["references_truth"], "references"
            )
            result.update(references_semantic)

            references_jaccard_result = await evaluate_jaccard_similarity(
                references_generated, references_truth, "references"
            )
            result.update(references_jaccard_result)

            references_faithfulness = await evaluate_faithfulness(
                references_generated,
                context,
                "Extract and list the relevant references and citations mentioned in the given content.",
                "references",
            )
            result.update(references_faithfulness)

            # Tags Evaluation
            # Prepare text for semantic similarity
            tags_truth_prepared = prepare_text_for_semantic_similarity(
                row["tags_truth"], "tags"
            )
            tags_generated_prepared = prepare_text_for_semantic_similarity(
                tags_generated, "tags"
            )

            tags_semantic = await evaluate_semantic_similarity(
                tags_generated_prepared, tags_truth_prepared, "tags"
            )
            result.update(tags_semantic)

            tags_jaccard_result = await evaluate_jaccard_similarity(
                tags_generated, row["tags_truth"], "tags"
            )
            result.update(tags_jaccard_result)

            tags_faithfulness = await evaluate_faithfulness(
                tags_generated_prepared,
                context,
                "Generate relevant tags and keywords that accurately represent the main topics and themes of the given content.",
                "tags",
            )
            result.update(tags_faithfulness)

            # Content Coherence Evaluation
            coherence_result = await evaluate_content_coherence(
                context,
                title_generated,
                tldr_generated,
                references_generated,
                tags_generated,
            )
            result.update(coherence_result)

            results.append(result)

            # Print scores using utility function
            print_evaluation_scores(result)

        except Exception as e:
            print(f"Error processing publication {row['publication_external_id']}: {e}")
            import traceback

            traceback.print_exc()
            # Still add the result with None values using utility function
            result = initialize_result_dict(row["publication_external_id"])
            result["content_coherence"] = None
            results.append(result)

    # Save results and print summary using utility functions
    results_df, complete_results = save_evaluation_results(results, df)
    print_evaluation_summary(results_df)

    return results_df, complete_results


if __name__ == "__main__":
    # Evaluate entire dataset
    asyncio.run(evaluate_dataset())
