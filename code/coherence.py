import typing as t
from dataclasses import dataclass, field
from ragas.metrics.base import MetricWithLLM, SingleTurnMetric, MetricType
from ragas.callbacks import Callbacks
from ragas.dataset_schema import SingleTurnSample
from ragas.prompt import PydanticPrompt
from pydantic import BaseModel, Field


class CoherenceInput(BaseModel):
    context: str = Field(description="The original publication content/context")
    title_generated: str = Field(description="AI generated title")
    tldr_generated: str = Field(description="AI generated TL;DR summary")
    references_generated: str = Field(description="AI generated references")
    tags_generated: str = Field(description="AI generated tags")


class CoherenceOutput(BaseModel):
    score: float = Field(description="Coherence score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation of the score")


class CoherencePrompt(PydanticPrompt[CoherenceInput, CoherenceOutput]):
    instruction = """You are an expert evaluator tasked with measuring the coherence and relevance of AI-generated content components.

Evaluate how well the generated title, TL;DR, references, and tags relate to each other and to the original context.

Consider the following criteria:

1. **Context Relevance (40% weight)**:
   - Do all generated components accurately reflect the main content and themes of the original context?
   - Are the key topics and concepts properly captured across all components?

2. **Internal Coherence (35% weight)**:
   - Do the title, TL;DR, references, and tags tell a consistent story?
   - Are there any contradictions or misalignments between components?
   - Do the tags align with the topics mentioned in the title and TL;DR?

3. **Thematic Consistency (25% weight)**:
   - Do all components maintain the same focus and scope as the original context?
   - Are the technical terms and domain-specific language consistent across components?
   - Do the references support the claims made in the title and TL;DR?

Rate on a scale of 0 to 1:
- 1.0: Perfect coherence - all components are highly relevant to context and perfectly aligned with each other
- 0.8-0.9: Very coherent - minor inconsistencies but overall strong alignment
- 0.6-0.7: Moderately coherent - some misalignment between components or with context
- 0.4-0.5: Poor coherence - significant inconsistencies or irrelevance to context
- 0.0-0.3: Very poor coherence - major contradictions or completely off-topic components"""

    input_model = CoherenceInput
    output_model = CoherenceOutput


@dataclass
class ContentCoherenceMetric(MetricWithLLM, SingleTurnMetric):
    """
    Custom metric to evaluate coherence between generated content components
    and their relevance to the original context.

    This metric measures whether the AI-generated title, TL;DR, references,
    and tags are coherent with each other and relevant to the source context.
    """

    name: str = "content_coherence"

    _required_columns: t.Dict[MetricType, t.Set[str]] = field(
        default_factory=lambda: {
            MetricType.SINGLE_TURN: {
                "context",
                "title_generated",
                "tldr_generated",
                "references_generated",
                "tags_generated",
            }
        }
    )

    coherence_prompt: PydanticPrompt = field(default_factory=CoherencePrompt)

    async def _single_turn_ascore(
        self, sample: SingleTurnSample, callbacks: Callbacks
    ) -> float:
        """
        Evaluate the coherence of generated content components.

        Args:
            sample: The sample containing context and generated content
            callbacks: Callbacks for monitoring

        Returns:
            Float score between 0 and 1 indicating coherence level
        """

        # Extract all required fields from the sample
        context = getattr(sample, "context", "")
        title_generated = getattr(sample, "title_generated", "")
        tldr_generated = getattr(sample, "tldr_generated", "")
        references_generated = getattr(sample, "references_generated", "")
        tags_generated = getattr(sample, "tags_generated", "")

        # Check if context is available
        if not context:
            print("Warning: No context found in sample")
            return 0.0

        # Prepare the prompt input
        prompt_input = CoherenceInput(
            context=context,
            title_generated=title_generated,
            tldr_generated=tldr_generated,
            references_generated=references_generated,
            tags_generated=tags_generated,
        )

        try:
            # Generate response using the PydanticPrompt
            prompt_response = await self.coherence_prompt.generate(
                data=prompt_input, llm=self.llm, callbacks=callbacks
            )

            return prompt_response.score

        except Exception as e:
            print(f"Error in LLM generation: {e}")
            return 0.5  # Default score if LLM fails
