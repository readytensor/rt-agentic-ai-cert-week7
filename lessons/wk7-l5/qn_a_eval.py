from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric
from deepeval.tracing import observe
import deepeval
import os
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
deepeval.login_with_confident_api_key(os.getenv("CONFIDENT_API_KEY"))

# Metrics
metrics = [
    AnswerRelevancyMetric(threshold=0.7),
    HallucinationMetric(threshold=0.01),  # Fail if hallucination > 1%
]

@observe(metrics=metrics)
def my_llm_component(user_query: str, context: str) -> str:
    system_prompt = f"Use the following context to answer the user:\n\n{context}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ✅ Case 1: Good
query_1 = "What is the capital of France?"
context_1 = "France’s capital city is Paris."
output_1 = my_llm_component(query_1, context_1)

test_case_1 = LLMTestCase(
    input=query_1,
    actual_output=output_1,
    expected_output="Paris",
    context=[context_1]
)

# ❌ Case 2: Bad — irrelevant context, fake answer
query_2 = "Who won the World Cup in 2022?"
context_2 = "This document only talks about European capital cities. No sports information is provided."
output_2 = my_llm_component(query_2, context_2)

test_case_2 = LLMTestCase(
    input=query_2,
    actual_output=output_2,
    expected_output="Argentina",
    context=[context_2]
)

# ❌ Case 3: Hallucination — fake science claim from cooking context
query_3 = "What is the half-life of carbon-14?"
context_3 = "This article describes recipes for baking banana bread and chocolate chip cookies."
output_3 = my_llm_component(query_3, context_3)

test_case_3 = LLMTestCase(
    input=query_3,
    actual_output=output_3,
    expected_output="5730 years",  # Correct value, but should be unsupported by context
    context=[context_3]
)

# Evaluate all
deepeval.evaluate([test_case_1, test_case_2, test_case_3], metrics=metrics)
