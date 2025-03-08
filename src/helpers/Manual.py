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
# 
# It can traverse classes to access non private builtin classes as well.
# ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
import inspect
import os

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from typing import Type, TypeVar
T = TypeVar('T') # Define a generic type variable for type annotation.

from src.Spotify_Features import SpotifyFeatures

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DESCRIPTION: Fancy way to manually invoke any method from any class or member class.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class MethodInvoker:
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Simply assigns the given object that we will be method invoking manually.
    INPUT: obj - Non builtin obj instance.
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def __init__(self, obj) -> None:
        self.obj = obj
        self.console = Console()
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Query the user for a valid selection from a range.
    INPUT: prompt - Str of what should be displayed to the user asking for their input.
           max_choice - Int of the max range of options presented to the user (0 -> 'max_choice').
    OUTPUT: Int of which value was selected (defaults to 0 if none is given).
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_valid_choice(self, prompt: str, max_choice: int) -> int:
        while True:
            choice = Prompt.ask(prompt)
            if choice == "":
                return 0
            if choice.isdigit() and int(choice) <= max_choice:
                return int(choice)
            self.console.print(f"Invalid input. Please select a valid option.", style="bold red")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Prompts the user for the inputs and casts them to the specified type (NOTE THIS RELIES ON GOOD INPUT 
                 VALIDATION OF OUR METHODS).
    INPUT: param_name - Str of the parameter name. 
           param_type - Python type of the 'param'.
           default_value = 'param_type' type default value for our method (can be None).
    OUTPUT: 'param_type' casted value of the user input.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_user_input(self, param_name: str, param_type: Type[T], default_value: T = None) -> None:
        while True:
            prompt_text = f"Enter value for {param_name} ({param_type.__name__})"
            if default_value is not None:
                prompt_text += f" [cyan]default: {str(default_value)}[/cyan]"
            try:
                value = Prompt.ask(prompt_text)
                return param_type(value) if value else default_value
            except ValueError:
                self.console.print(f"Invalid input. Expected type: {param_type.__name__}", style="bold red")

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Generates a dict of all methods and their name for our current obj.
    INPUT: methods - List of available methods from our obj.
    OUTPUT: N/A (prints to table to console).
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def get_available_classes(self) -> dict:
        return {
            attr_name: attr_value
            for attr_name, attr_value in self.obj.__dict__.items()
            if not attr_name.startswith("_")                # Ignore private variables
            and hasattr(attr_value, "__dict__")             # Ensure it's an object with attributes
            and type(attr_value).__module__ != "builtins"   # Exclude primitive types
        }

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Displays all available classes within our object, if another class is selected we continue to
                 programatically print out all available classes until one is chosen.
    INPUT: N/A
    OUTPUT: N/A (self.obj is updated to point to the desired class).
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def select_class(self) -> None:
        parent_name = type(self.obj).__name__
        while True:
            table = Table(title=f"Available Classes in \'{parent_name}\'", show_header=True, header_style="magenta")
            table.add_column("No.", style="dim", width=3)
            table.add_column("Attribute Name", style="cyan")
            table.add_column("Class Type", style="green")
            table.add_row("0", f"[bold yellow]Use {parent_name} (Main)[/bold yellow]", "-")
            
            class_attrs = self.get_available_classes()
            for idx, (attr_name, class_instance) in enumerate(class_attrs.items(), 1):
                class_type = type(class_instance).__name__
                table.add_row(str(idx), f"[cyan]{attr_name}[/cyan]", f"[green]{class_type}[/green]")

            self.console.print(table)
            choice = self.get_valid_choice("[bold magenta]Select a class by number[/bold magenta]", len(class_attrs))
            if choice == 0:
                return

            selected_attr_name = list(class_attrs.keys())[choice - 1]
            self.obj = class_attrs[selected_attr_name]
            parent_name = f"{selected_attr_name} ({type(self.obj).__name__})"

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Generically display all of the avaialable methods and arguments for those methods.
    INPUT: N/A.
    OUTPUT: Dict of all methods, key value pair being (name, method) with method being the actual obj reference.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def display_available_methods(self):
        methods = {name: method for name, method in inspect.getmembers(self.obj, predicate=inspect.ismethod) 
                   if not name.startswith("_")}

        table = Table(title=f"Available Methods for \'{type(self.obj).__name__}\'"
                      , show_header=True, header_style="magenta")
        table.add_column("No.", style="dim", width=len(str(len(methods))) + 1) # Gross way to get number of digits.
        table.add_column("Method Name", style="cyan")
        table.add_column("Arguments", style="green")

        for idx, (name, method) in enumerate(methods.items(), 0):
            params = "\n".join([f"[red]{param.name}[/red] ({param.annotation.__name__})"
                    + (" [white]\\[opt][/white]" if param.default is not inspect.Parameter.empty else "")
                    for param in inspect.signature(method).parameters.values()])
            table.add_row(str(idx), f"{name}", params)

        self.console.print(table)
        return methods

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    DESCRIPTION: Handles obtaining the user's desired class, method, and all potential arguments before running said
                 method with arguments.
    INPUT: N/A
    OUTPUT: N/A
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""''""""""
    def invoke_method(self):
        self.select_class()
        methods = self.display_available_methods()
        choice = self.get_valid_choice("[bold magenta]Select a method by number[/bold magenta]", len(methods))
        method_name = list(methods.keys())[choice]
        method = methods[method_name]
        kwargs = {}

        for param_name, param in inspect.signature(method).parameters.items():
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else str
            default_value = param.default if param.default != inspect.Parameter.empty else None
            kwargs[param_name] = self.get_user_input(param_name, param_type, default_value)
        
        self.console.print(f"\nRunning {method_name} with arguments: {kwargs}\n", style="bold green")
        result = method(**kwargs)
        self.console.print(f"Result: {result}\n", style="bold yellow")


def main():
    os.system("clear")
    features = SpotifyFeatures(log_file_name="Manual.log")

    invoker = MethodInvoker(features)
    invoker.invoke_method()

if __name__ == "__main__":
    main()


# FIN ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════