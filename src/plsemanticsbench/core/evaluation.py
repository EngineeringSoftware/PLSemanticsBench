import json
import tempfile
from typing import List
from pathlib import Path
from .evaluator import LLMEvaluator
from .exps.experiment_args import Task, Semantics_Type

def evaluate(
    predictions: str | Path | List[dict],
    task: Task,
    semantics_type: Semantics_Type,
    model_name: str,
    verbose: bool = False
) -> dict:
    """
    Evaluate LLM predictions against ground truth.
    
    Args:
        predictions: Either a path to a file containing predictions or a list of prediction dictionaries
        task (Task): The task to evaluate (e.g., "predstate", "predrule", "predtrace")
        semantics_type (Semantics_Type): The type of provided semantics (e.g., no/standard/non-standard semantics)
        model_name (str): Name of the model being evaluated
        verbose (bool): Whether to print verbose output
        
    Returns:
        dictionary containing evaluation metrics
    """
    # Initialize evaluator
    evaluator = LLMEvaluator(task=task, semantics_type=semantics_type)
    
    # Handle predictions input
    if isinstance(predictions, (str, Path)):
        # If predictions is a file path, use it directly
        results = evaluator.evaluate(str(predictions), model_name)
    else:
        # If predictions is a list of dicts, write to temp file and evaluate        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for pred in predictions:
                f.write(json.dumps(pred) + '\n')
            #rof
            temp_path = f.name
        #htiw
        try:
            results = evaluator.evaluate(temp_path, model_name)
        finally:
            # Clean up temp file
            Path(temp_path).unlink()
        #yrt
    #fi
    if verbose:
        print(results)
    #fi
    return results 
#fed
