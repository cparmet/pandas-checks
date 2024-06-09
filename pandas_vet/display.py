from .options import _initialize_format_options
import emoji
from IPython.display import display, HTML, Markdown
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from termcolor import colored
import textwrap


# -----------------------
# Utilities
# -----------------------

def _filter_emojis(text):
    """Depending on user's global settings, remove emojis."""
    if pd.get_option("vet.use_emojis"):
        return text
    return emoji.replace_emoji(text, replace='').strip()


def _render_html_with_indent(object_as_html):
    indent = pd.get_option("vet.indent_table_plot_ipython") # In pixels
    display(
        HTML(
            f'<div style="margin-left: {indent}px;">{object_as_html}</div>' 
            if indent else object_as_html
        )
    )

def _render_text(text, tag, lead_in=None, colors={}):
    if text:
        # Format background_color for term_colors
        text_color = colors.get("text_color", None)
        text_background_color = colors.get("text_background_color", None)
        lead_in_text_color = colors.get("lead_in_text_color", None)
        lead_in_background_color = colors.get("lead_in_background_color", None)
        if pd.core.config_init.is_terminal(): # If we're not in IPython, display as text
                print() # White space for terminal display
                lead_in_rendered = f"{colored(_filter_emojis(lead_in), text_color, _format_background_color(lead_in_background_color))}:" if lead_in else ""
                print(lead_in_rendered + f"{colored(_filter_emojis(text), text_color, _format_background_color(text_background_color))}")
        else: # Print stylish!
            lead_in_rendered = _lead_in(lead_in, lead_in_text_color, lead_in_background_color)
            display(
                Markdown(
                    f"<{tag} style='text-align: left'>{lead_in_rendered + ' ' if lead_in_rendered else ''}<span 'color:{text_color};' 'background-color:{text_background_color}'>{_filter_emojis(text)}</span></{tag}>"
                    )
                )

# -----------------------
# Tables
# -----------------------

def _print_table_terminal(table):
    """Print a Pandas DF or Series in a terminal, with optional indent """
    indent_prefix = pd.get_option("vet.indent_table_terminal") # In spaces
    print(
        textwrap.indent
        (
        text=table.to_string(),
            prefix=' ' * indent_prefix if indent_prefix else ''
        )
    )

def _display_table(table):
    """Render a Pandas DF or Series in an IPython/Jupyter environment, with optional indent """
    _render_html_with_indent(table.to_html())


def _display_table_title(line, lead_in=None, colors={}):
    """This allows us to align plot titles, table titles, and other check outputs
    for a cleaner output cell."""
    _render_text(
        line,
        tag=pd.get_option("table_title_tag"),
        lead_in=lead_in,
        colors=colors
        )

def _get_vet_table_styles():
    """Return empty list when all registered styles are {}"""
    return (
        [pd.get_option("vet.table_row_hover_style")] if pd.get_option("vet.table_row_hover_style") else []
    )

# -----------------------
# Plots
# -----------------------

def _display_plot():
    """Renders a PandasVet plot object in an IPython/Jupyter environment, with optional indent. Also displays the plot in the chronological order of chain execution, instead of attaching the plot at the bottom of a notebook cell

    TODO: Presumes matplotlib is the Pandas plotting back end.
    """
    if not pd.core.config_init.is_terminal():
        indent = pd.get_option("vet.indent_table_plot_ipython") # In pixels
        # Save the figure to a bytes buffer
        buffer = io.BytesIO()
        fig = plt.gcf() # TODO: Get the figure from passing the `fig` argument to _display_plot() but without generating a UserWarning from matplotlib.
        fig.savefig(buffer, format='png')
        plt.close(fig)  # Don't show it at the bottom of the cell too
        buffer.seek(0)
        #  Encode the image to base64 string, then display it as HTML
        display(
            HTML(
                f"""
                <style>
                .indent-plot {{
                    display: flex;
                    padding-left: {indent}px;
                    }}
                </style>

                <div class="indent-plot">
                    <img src="data:image/png;base64,{

                        base64
                        .b64encode(buffer.read())
                        .decode('utf-8')
                        }" />
                </div>
                """
                )
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

# -----------------------
# Text
# -----------------------

def _format_background_color(color):
    """Cleans background color for termcolor rendering"""
    return color if not color else f"on_{color}" if not color.startswith("on_") else color

def _lead_in(lead_in, foreground, background):
    return f"<span style='color:{foreground}; background-color:{background}'>{_filter_emojis(lead_in).strip()}:</span>" if lead_in else ""

def _display_line(line, lead_in=None, colors={}):
    """This allows us to align plot titles, table titles, and other check outputs
    for a cleaner output cell."""
    _render_text(
        line,
        tag=pd.get_option("vet.check_text_tag"),
        lead_in=lead_in,
        colors=colors
        )

# ---------------------------------------------
# Main function for showing results of checks
# ---------------------------------------------

def _display_check(data, name=None):
    """ Render the result of our check.
    Behave differently if we're in an IPython interactive session / Jupyter nobteook"""
    try:
        # Is it a one-liner result?
        if isinstance(data, (int, np.int8, np.int32, np.int64, str, float, np.float16, np.float32, np.float64, list, dict, tuple)):
            _display_line(f"{name}: {data}" if name else data) # Print check name and result in one line
        # This is a Pandas dataframe or Series, or other multi-line object
        # Are we in IPython/Jupyter?
        elif not pd.core.config_init.is_terminal():
            # Is it a DF?
            if isinstance(data, pd.DataFrame):
                _display_table_title(name)
                _display_table(
                    data
                    .style.set_table_styles(_get_vet_table_styles())
                    .format(precision=pd.get_option("vet.precision"))
                    )
            # Or a Series we should format as a DF?
            elif isinstance(data, pd.Series):
                _display_table_title(name)
                _display_table(
                    pd.DataFrame(
                        # For Series based on some Pandas outputs like memory_usage(),
                        # don't show a column name of 0
                        data.rename(data.name if data.name!=0 and data.name!=None else "")
                        )
                    .style.set_table_styles(_get_vet_table_styles())
                    .format(precision=pd.get_option("vet.precision"))
                    ) # Add check name as column head
            # Otherwise, show check name and data on separate lines
            else:
                _display_line(name)
                display(data) # Use IPython rendering
        else: # We're in a Terminal. Can't display Styled tables or use IPython rendering
            print() # White space for terminal display
            # Print check name and data on separate lines
            if name:
                print(_filter_emojis(name))
            _print_table_terminal(data)
    except TypeError:
        raise TypeError(f"Can't _display_data object of type {type(data)} in this environment.")
