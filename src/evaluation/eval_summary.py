import os
import json
import logging
from rouge_score import rouge_scorer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def evaluate_summaries(report_path="data/final_summary_report.json", ground_truth_path="evaluation/ground_truth.json", output_path="data/evaluation_results.json"):
    """
    Computes ROUGE-1, ROUGE-2, and ROUGE-L scores for generated extractive and generative briefs
    against human ground truth summaries.
    """
    logger.info("Initializing ROUGE evaluation...")
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Final summary report {report_path} does not exist. Run the pipeline first.")
    if not os.path.exists(ground_truth_path):
        raise FileNotFoundError(f"Ground truth file {ground_truth_path} does not exist.")

    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)

    # Initialize ROUGE scorer (English and Indonesian are supported; use_stemmer=True works with Porter stemming)
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    results = {}
    
    print("\n" + "="*80)
    print(f"{'TREND CATEGORY':<25} | {'METRIC':<8} | {'TYPE':<10} | {'PRECISION':<9} | {'RECALL':<6} | {'F-MEASURE':<9}")
    print("="*80)

    for category, ref_summary in ground_truth.items():
        if category not in report:
            logger.warning(f"Category '{category}' from ground truth not found in summary report.")
            continue

        gen_data = report[category]
        extractive_brief = gen_data.get("extractive_brief", "")
        generative_brief = gen_data.get("generative_brief", "")

        # Score extractive summary
        ext_scores = scorer.score(ref_summary, extractive_brief)
        # Score generative summary
        gen_scores = scorer.score(ref_summary, generative_brief)

        results[category] = {
            "extractive": {
                "rouge1": ext_scores["rouge1"]._asdict(),
                "rouge2": ext_scores["rouge2"]._asdict(),
                "rougeL": ext_scores["rougeL"]._asdict()
            },
            "generative": {
                "rouge1": gen_scores["rouge1"]._asdict(),
                "rouge2": gen_scores["rouge2"]._asdict(),
                "rougeL": gen_scores["rougeL"]._asdict()
            }
        }

        # Print scores in a clean table format
        for metric in ['rouge1', 'rouge2', 'rougeL']:
            ext_s = ext_scores[metric]
            gen_s = gen_scores[metric]
            print(f"{category:<25} | {metric:<8} | Extractive | {ext_s.precision:<9.4f} | {ext_s.recall:<6.4f} | {ext_s.fmeasure:<9.4f}")
            print(f"{category:<25} | {metric:<8} | Generative | {gen_s.precision:<9.4f} | {gen_s.recall:<6.4f} | {gen_s.fmeasure:<9.4f}")
            print("-"*80)

    # Save to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logger.info(f"ROUGE evaluation results saved successfully to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to save evaluation results: {e}")

    return output_path

if __name__ == "__main__":
    evaluate_summaries()
