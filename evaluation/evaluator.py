import logging
from rouge_score import rouge_scorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    def calculate_rouge(self, reference: str, candidate: str) -> dict:
        """
        Calculates ROUGE-1, ROUGE-2, and ROUGE-L F1 scores.
        """
        logger.info("Calculating ROUGE scores...")
        scores = self.scorer.score(reference, candidate)
        return {
            "rouge-1": scores['rouge1'].fmeasure,
            "rouge-2": scores['rouge2'].fmeasure,
            "rouge-l": scores['rougeL'].fmeasure
        }

if __name__ == "__main__":
    ref = "The company reported high sales of eco-friendly products during the second quarter."
    cand = "Eco-friendly products sales were reported to be high during Q2 by the company."
    evaluator = ModelEvaluator()
    scores = evaluator.calculate_rouge(ref, cand)
    print("ROUGE scores:", scores)
