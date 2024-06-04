import emoji
from inspect import getsourcelines
import pandas as pd
from termcolor import colored

def _filter_emojis(text):
    """Depending on user's global settings, remove emojis."""
    if pd.get_option("vet.use_emojis"):
        return text
    return emoji.replace_emoji(text, replace='').strip()

def _format_success_message(message):
    return colored(message, pd.get_option("vet.success_text_fg_color"), pd.get_option("vet.success_text_bg_color"))

def _format_fail_message(message):
    return colored(message, pd.get_option("vet.fail_text_fg_color"), pd.get_option("vet.fail_text_bg_color"))

def _get_vet_table_styles():
    """Return empty list when all registered styles are {}"""
    return (
        [pd.get_option("vet.table_cell_hover_style")] if pd.get_option("vet.table_cell_hover_style") else []
    )

def _lambda_to_string(lambda_func):
    """TODO: This still returns all arguments to the calling function. They get entangled with the argument when it's a lambda function. Try other ways to get just the argument we want"""
    return (
        ''.join(
            getsourcelines(lambda_func)
            [0]
            )
        .lstrip(" .")
    )
