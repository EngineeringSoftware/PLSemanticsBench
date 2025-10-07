import click
import sys
from pathlib import Path
from ..core.evaluator import LLMEvaluator
from ..core.exps.experiment_args import (
    Task,
    Language,
    Formalization,
    Semantics_Type,
    PLDataset,
    PROMPT_STRATEGY,
    ExperimentArgs,
    to_exp_enum
)
from ..core.exps.ollama_experiment import OllamaRunner
from ..core.exps.gpt_experiment import GPTRunner

def enum_choice(enum_cls):
    return click.Choice([e.value for e in enum_cls])
#fed

@click.command()
@click.option('-p', '--prediction_file', type=click.Path(exists=True, path_type=Path), required=True,
              help='Path to the file containing LLM predictions')
@click.option('--task', '-t', type=enum_choice(Task), help='The task to evaluate')
@click.option('--semantics_type', '-s', type=enum_choice(Semantics_Type), help='Semantics type')
@click.option('--model_name', '-m', type=str, help='Model name')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def eval_command(prediction_file, task, semantics_type,  model_name, verbose):
    """Evaluate LLM predictions against ground truth."""
    try:
        if verbose:
            click.echo(f"Loading predictions from: {prediction_file}")
            click.echo(f"Task: {task}")
            click.echo(f"Semantics type: {semantics_type}")
            click.echo(f"Model name: {model_name}")
        #fi

        # Initialize evaluator
        evaluator = LLMEvaluator(
            task=to_exp_enum(Task, task),
            semantics_type=to_exp_enum(Semantics_Type, semantics_type)
            )
        results = evaluator.evaluate_from_file(prediction_file, model_name)
        if verbose:
            print(results)
        #fi
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    #yrt
#fed

@click.command()
@click.option('--model_name', '-m', type=str, help='Model name')
@click.option('--runner_type', '-u', type=click.Choice(['OpenAI', 'Ollama']), help='Runner type')
@click.option('--task', '-t', type=enum_choice(Task), help='The task to evaluate')
@click.option('--language', '-l', type=enum_choice(Language), help='Language')
@click.option('--formalization', '-f', type=enum_choice(Formalization), help='Formalization')
@click.option('--semantics_type', '-s', type=enum_choice(Semantics_Type), help='Semantics type')
@click.option('--dataset', '-d', type=enum_choice(PLDataset), help='Dataset')
@click.option('--prompt_strategy', '-p', type=enum_choice(PROMPT_STRATEGY), help='Prompt Strategy')
@click.option('--num_datapoints', '-n', type=int, help='Number of dataset points to run')
@click.option('--result_file', '-r', type=click.Path(exists=False, path_type=Path), required=True,
              help="Path to the file to dump model's results")
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def generation_command(model_name, runner_type, task, language, formalization, semantics_type, dataset, prompt_strategy, num_datapoints, result_file, verbose):
    """Generate predictions on the specified experiment configuration"""
    try:
        exp_args = ExperimentArgs.from_str(
            dataset=dataset,
            task=task,
            language=language,
            formalization=formalization,
            semantics_type=semantics_type,
            model_name=model_name,
            prompt_strategy=prompt_strategy,
            num_datapoints_to_run=num_datapoints
        )
        click.echo(f"Generating for model {model_name} on experiment configuration: {exp_args}")

        runner = None
        match runner_type:
            case "OpenAI":
                runner = GPTRunner(args=exp_args)
            case "Ollama":
                runner = OllamaRunner(args=exp_args)
            case _:
                click.echo(f"Invalid runner type {runner_type}!")
                sys.exit(-1)
        #hctam

        predictions = runner.do_experiment(result_file)
        
        if verbose:
            print(predictions)
        #fi
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    #yrt
#fed
