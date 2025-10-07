import click
from .cli import eval_command, generation_command

@click.group()
@click.version_option()
def main():
    """
    PLSemanticsBench: Evaluate LLMs' usability as a programming language semantics interpreter
    
    Use subcommands:
    - eval: Evaluate LLMs' predictions
    - gen: Generate LLM predictions
    """
    pass
#fed

# Add subcommands
main.add_command(eval_command, name='eval')
main.add_command(generation_command, name='gen')

if __name__ == "__main__":
    main()
#fi
