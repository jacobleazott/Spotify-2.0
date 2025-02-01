# ╔════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦════╗
# ║  ╔═╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩═╗  ║
# ╠══╣                                                                                                            ╠══╣
# ║  ║    MANUAL OPERATIONS                       CREATED: 2025-01-30          https://github.com/jacobleazott    ║  ║
# ║══║                                                                                                            ║══║
# ║  ╚═╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦══════╦═╝  ║
# ╚════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩══════╩════╝
# ═══════════════════════════════════════════════════ DESCRIPTION ════════════════════════════════════════════════════
# Sometimes, especially when testing we need a way to manually trigger operations instead of just relying on the 
#   scheduled jobs. This file is to give a relatively user friendly interface to run various features manually.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import inspect
import os

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from typing import Type, TypeVar
# Define a generic type variable
T = TypeVar('T')

from src.Spotify_Features import SpotifyFeatures

# Initialize console object
console = Console()

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Prompts the user for the inputs and casts them to the specified type (NOTE THIS RELIES ON GOOD INPUT 
             VALIDATION OF OUR METHODS).
INPUT: param_name - Str of the parameter name. 
       param_type - Python type of the 'param'.
       default_value = 'param_type' type default value for our method (can be None).
OUTPUT: 'param_type' casted value of the user input.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_user_input(param_name: str, param_type: Type[T], default_value: T=None):
    while True:
        prompt_text = f"Enter value for {param_name} ({param_type.__name__})"
        if default_value is not None:
            prompt_text += f" [cyan]default: {str(default_value)}[/cyan]"
        try:
            value = Prompt.ask(prompt_text)
            # Cast input to the correct type or use default if no val was given.
            return param_type(value) if value else default_value
        except ValueError:
            print(f"Invalid input. Expected type: {param_type.__name__}")


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Generically display all of the avaialable methods and arguments for those methods.
INPUT: methods - List of available methods from our obj.
OUTPUT: NA (prints to table to console).
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def display_available_features(methods):
    table = Table(title="Available Features", show_header=True, header_style="magenta")
    table.add_column("No.", style="dim", width=len(str(len(methods))) + 1) 
    table.add_column("Feature Name", style="cyan")
    table.add_column("Arguments", style="green")

    for idx, (name, method) in enumerate(methods.items(), 1):
        params = "\n".join([f"[red]{param.name}[/red] ({param.annotation.__name__})"
                + (" [white]\\[opt][/white]" if param.default is not inspect.Parameter.empty else "")
                for param in inspect.signature(method).parameters.values()])
        table.add_row(str(idx), f"{name}", params)

    console.print(table)


def main():
    os.system("clear")
    
    features = SpotifyFeatures(log_file_name="Manual.log")
    features.skip_track()
    
    methods = {
        name: method for name, method in inspect.getmembers(features, predicate=inspect.ismethod)
            if not name.startswith("_")}
    
    display_available_features(methods)
    choice = Prompt.ask(f"[bold magenta]Select a feature by number[/bold magenta]")

    try:
        choice = int(choice)
    except ValueError:
        console.print("Invalid input. Please select a valid number.", style="bold red")
        return

    if choice < 1 or choice > len(methods):
        console.print("Choice out of range. Please select a valid feature number.", style="bold red")
        return

    method_name = list(methods.keys())[choice - 1]
    method = methods[method_name]
    sig = inspect.signature(method)
    kwargs = {}

    for param_name, param in sig.parameters.items():
        param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
        default_value = param.default if param.default != inspect.Parameter.empty else None
        kwargs[param_name] = get_user_input(param_name, param_type, default_value)
        print(kwargs[param_name])
    
    console.print(f"\nRunning {method_name} with arguments: {kwargs}\n", style="bold green")
    result = method(**kwargs)
    console.print(f"Result: {result}\n", style="bold yellow")

if __name__ == "__main__":
    main()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════