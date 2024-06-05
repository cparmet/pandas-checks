import emoji
from inspect import getsourcelines
from IPython.display import display
import matplotlib.pyplot as plt
import pandas as pd
from termcolor import colored

def _display_plot_now():
    """Display the plot in cell outputs in the chronological order of chain execution,
    instead of attaching the plot at the bottom of a notebook cell"""
    if not pd.core.config_init.is_terminal():
        display(plt.gcf()) # Show it now
        plt.close() # Don't show it at the bottom of the cell too

def _filter_emojis(text):
    """Depending on user's global settings, remove emojis."""
    if pd.get_option("vet.use_emojis"):
        return text
    return emoji.replace_emoji(text, replace='').strip()

def _format_success_message(message):
    return colored(message, pd.get_option("vet.success_text_fg_color"), pd.get_option("vet.success_text_bg_color"))

def _format_fail_message(message):
    return colored(message, pd.get_option("vet.fail_text_fg_color"), pd.get_option("vet.fail_text_bg_color"))

def _lambda_to_string(lambda_func):
    """TODO: This still returns all arguments to the calling function. They get entangled with the argument when it's a lambda function. Try other ways to get just the argument we want"""
    return (
        ''.join(
            getsourcelines(lambda_func)
            [0]
            )
        .lstrip(" .")
    )
