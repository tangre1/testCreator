import random
from collections import defaultdict
from typing import Dict, List

from .models import Question


def generate_exam(
    questions: List[Question],
    total: int,
    weights: Dict[str, float],
    seed: int | None = None
) -> List[Question]:
    """
    Selects questions for an exam based on topic weights.

    Args:
        questions: Full list of available questions
        total: Total number of questions to select
        weights: Mapping of topic -> proportion of exam
        seed: Optional random seed for reproducibility

    Returns:
        List[Question]: Selected questions in randomized order

    Raises:
        ValueError: If weights are invalid or insufficient questions exist
    """

    if total <= 0:
        raise ValueError("Total number of questions must be positive")

    if not weights:
        raise ValueError("Topic weights must be provided")

    # Optional deterministic behavior
    if seed is not None:
        random.seed(seed)

    # Group questions by topic
    questions_by_topic: Dict[str, List[Question]] = defaultdict(list)
    for q in questions:
        questions_by_topic[q.topic].append(q)

    # Validate weight totals (soft validation)
    weight_sum = sum(weights.values())
    if not 0.99 <= weight_sum <= 1.01:
        raise ValueError("Topic weights must sum to approximately 1.0")

    selected: List[Question] = []

    # Select questions per topic
    for topic, weight in weights.items():
        count = round(total * weight)

        pool = questions_by_topic.get(topic, [])
        if len(pool) < count:
            raise ValueError(
                f"Not enough questions for topic '{topic}' "
                f"(needed {count}, found {len(pool)})"
            )

        selected.extend(random.sample(pool, count))

    # Final shuffle to avoid topic clustering
    random.shuffle(selected)

    # Safety check
    if len(selected) != total:
        raise ValueError(
            f"Exam generation error: expected {total} questions, "
            f"got {len(selected)}"
        )

    return selected
