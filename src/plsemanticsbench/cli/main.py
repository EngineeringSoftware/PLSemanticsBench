import click
from .eval import eval_command

@click.group()
@click.version_option()
def main():
    """
    PLSemanticsBench: Evaluate LLMs' usability as a programming language semantics interpreter
    
    Use subcommands:
    - eval: Evaluate LLMs' predictions
    """
    pass

# Add subcommands
main.add_command(eval_command, name='eval')

if __name__ == "__main__":
    main()