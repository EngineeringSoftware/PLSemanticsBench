import click
import sys
from pathlib import Path
from ..core.evaluator import LLMEvaluator

@click.command()
@click.option('-p', '--prediction_file', type=click.Path(exists=True, path_type=Path), required=True,
              help='Path to the file containing LLM predictions')
@click.option('--task', '-t', type=str, help='The task to evaluate')
@click.option('--semantics_type', '-s', type=str, help='Semantics type, choose from [nk, uk, mk]')
@click.option('--model_name', '-m', type=str, help='Model name')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def eval_command(prediction_file, task, semantics_type,  model_name, verbose):
    """
    Evaluate LLM predictions against ground truth.
    
    PREDICTION_FILE: Path to the file containing LLM predictions
    """
    try:
        if verbose:
            click.echo(f"Loading predictions from: {prediction_file}")
            click.echo(f"Task: {task}")
            click.echo(f"Semantics type: {semantics_type}")
            click.echo(f"Model name: {model_name}")

        # Initialize evaluator
        evaluator = LLMEvaluator(task=task, semantics_type=semantics_type)
        results = evaluator.evaluate(prediction_file, model_name)
        if verbose:
            print(results)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

def main():
    """Standalone entry point for plsemanticsbench eval command"""
    eval_command()

if __name__ == "__main__":
    main()
