from .options import _initialize_format_options
import emoji
from IPython.display import display, Markdown
import matplotlib.pyplot as plt
import pandas as pd
from termcolor import colored

# Public functions
def set_format(**kwargs):
    """Set PandasVet output format. Options include:"""
    for arg, value in kwargs.items():
        vet_option = arg if arg.startswith("vet.") else "vet." + arg # Fully qualified
        if vet_option in pd._config.config._select_options("vet"):
            pd.set_option(vet_option, value)
        else:
            raise AttributeError(f"No Pandas Vet option for {vet_option}. Available options: {pd._config.config._select_options('vet')}")

def reset_format():
    """Re-initilaize all Pandas Vet options for formatting"""
    _initialize_format_options()

# Private functions
def _format_background_color(color):
    """Cleans background color for termcolor rendering"""
    return color if not color else f"on_{color}" if not color.startswith("on_") else color

def _lead_in(lead_in, foreground, background):
    return f"<span style='color:{foreground}; background-color:{background}'>{_filter_emojis(lead_in).strip()}: </span>" if lead_in else ""

def _render_text(text, tag, lead_in=None, colors={}):
    if text:
        # Format background_color for term_colors
        text_color = colors.get("text_color", None)
        text_background_color = colors.get("text_background_color", None)
        lead_in_text_color = colors.get("lead_in_text_color", None)
        lead_in_background_color = colors.get("lead_in_background_color", None)
        if pd.core.config_init.is_terminal(): # If we're not in IPython, display as text
                print() # White space for terminal display
                print(
                    f"{colored(_filter_emojis(lead_in), text_color, _format_background_color(lead_in_background_color))}:" if lead_in else "" + f"{colored(_filter_emojis(text), text_color, _format_background_color(text_background_color))}")
                
        else: # Print stylish!
            display(
                Markdown(
                    f"<{tag} style='text-align: left'>{_lead_in(lead_in, lead_in_text_color, lead_in_background_color)}" + f"<span 'color:{text_color};' 'background-color:{text_background_color}'>{_filter_emojis(text)}</span>" + f"</{tag}>"
                    )
                )

def _display_line(line, lead_in=None, colors={}):
    """This allows us to align plot titles, table titles, and other check outputs 
    for a cleaner output cell."""
    _render_text(
        line,
        tag=pd.get_option("vet.check_text_tag"),
        lead_in=lead_in,
        colors=colors
        )

def _display_table_title(line, lead_in=None, colors={}):
    """This allows us to align plot titles, table titles, and other check outputs 
    for a cleaner output cell."""
    _render_text(
        line,
        tag=pd.get_option("table_title_tag"),
        lead_in=lead_in,
        colors=colors
        )

def _display_plot_title(line, lead_in=None, colors={}):
    """This allows us to align plot titles, table titles, and other check outputs 
    for a cleaner output cell."""
    _render_text(
        line,
        tag=pd.get_option("plot_title_tag"),
        lead_in=lead_in,
        colors=colors
        )

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

def _get_vet_table_styles():
    """Return empty list when all registered styles are {}"""
    return (
        [pd.get_option("vet.table_row_hover_style")] if pd.get_option("vet.table_row_hover_style") else []
    )
