"""Utilities for displaying text, tables, and plots in Pandas Checks in both terminal and IPython/Jupyter environments.
"""

import base64
import io
import textwrap
from typing import Any, Dict, Union

import emoji
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, Markdown, display
from termcolor import colored

# -----------------------
# Utilities
# -----------------------


def _display_router(
    data: Any, data_for_print_fn: Union[str, None] = None, bypass_print_fn: bool = False
) -> None:
    """Renders content to the output destination(s) as configured globally, including rich content such as plots in IPython/Jupyter environments.

    Args:
        data: A displayable object, such as a string, DataFrame, Series, or plot.
        data_for_print_fn: Optional, simplied version of text to display when data is formatted HTML (so it doesn't look odd when print_fn is logging.info, for example).
        bypass_print_fn: Optional flag to disable printing to custom_print_fn. Used when we want to display data (such as a plot title) in IPython/Jupyter but not in a logger or other custom_print_fn (since plots aren't logged).

    Returns:
        None
    """

    if pd.get_option("pdchecks.print_to_stdout"):
        display(data)

    # Check if we have a custom print function, and the caller wants to use it
    if (
        callable(print_fn := pd.get_option("pdchecks.custom_print_fn"))
        and not bypass_print_fn
    ):
        # Output "plain" version of data, if it exists, to custom_print_fn (e.g. logger)
        print_fn(data_for_print_fn if data_for_print_fn else data)


def _print_router(
    text: Union[str, None],
    custom_print_fn_only: bool = False,
    text_for_print_fn: Union[str, None] = None,
    bypass_print_fn: bool = False,
) -> None:
    """Prints given text to the output destination(s) as configured globally.

    Args:
        text: The text to print.
        custom_print_fn_only: Whether to only call the custom print function if it exists, without attempting to print to standard output. Used when _print_router() is called only to access custom_print_fn.
        text_for_print_fn: Optional, simplied version of text to display without colors (so it doesn't look odd when print_fn is logging.info, for example).
        bypass_print_fn: Optional flag to disable printing to custom_print_fn. Used when we want to display text (such as white space lines) in Terminal but not in a logger or other custom_print_fn.

    Returns:
        None
    """

    if pd.get_option("pdchecks.print_to_stdout") and not custom_print_fn_only:
        print(text)

    if (
        callable(print_fn := pd.get_option("pdchecks.custom_print_fn"))
        and not bypass_print_fn
    ):
        print_fn(text_for_print_fn if text_for_print_fn else text)


def _filter_emojis(text: str) -> str:
    """Removes emojis from text if user has globally forbidden them.

    Args:
        text: The text to filter emojis from.

    Returns:
        The text with emojis removed if the user's global settings do not allow emojis. Else, the original text.
    """
    if pd.get_option("pdchecks.use_emojis"):
        return text
    return emoji.replace_emoji(text, replace="").strip()


def _render_html_with_indent(object_as_html: str) -> None:
    """Renders HTML with an optional indent.

    Args:
        object_as_html: The HTML to render.

    Returns:
        None
    """
    indent = pd.get_option("pdchecks.indent_table_plot_ipython")  # In pixels
    _display_router(
        HTML(
            f'<div style="margin-left: {indent}px;">{object_as_html}</div>'
            if indent
            else object_as_html
        ),
        bypass_print_fn=True,
    )


def _render_text(
    text: str,
    tag: str,
    lead_in: Union[str, None] = None,
    colors: Dict = {},
    bypass_print_fn: bool = False,
) -> None:
    """Renders text with optional formatting.

    Args:
        text: The text to render.
        tag: The HTML tag to use for rendering.
        lead_in: Optional text to display before the main text.
        colors: Optional colors for the text and lead-in text.
            Keys include:
                - text_color: The foreground color of the main text.
                - text_background_color: The background or highlight color of the main text.
                - lead_in_text_color: The foreground color of lead-in text.
                - lead_in_background_color: The background color of lead-in text.
            Color values are phrased such as "blue" or "white". They are passed to either HTML
                for Jupyter/IPython outputs and to `termcolor` when code is run in terminal.
                For color options when code is run in terminal, see
                    https://github.com/termcolor/termcolor.
        bypass_print_fn: Optional flag to decide whether the text should also be sent to the global custom print function, if it exists. See _display_router() for details.

    Returns:
        None
    """
    if text:
        # Create plain text version for custom_print_fn
        text_for_print_fn = (
            f"{_filter_emojis(lead_in) + ': ' if lead_in else ''}{_filter_emojis(text)}"
            .rstrip("\n")
            .rstrip("")
        )  # fmt: skip

        # Format background_color for term_colors
        text_color = colors.get("text_color", None)
        text_background_color = colors.get("text_background_color", None)
        lead_in_text_color = colors.get("lead_in_text_color", None)
        lead_in_background_color = colors.get("lead_in_background_color", None)

        # Remove termcolor background style format ("on_green") if user passed it that way.
        # This syntax will be added back if we display in terminal,
        # but must be removed if we're displaying HTML in Jupyter or IPython
        text_background_color = (
            text_background_color.replace("on_", "")
            if text_background_color
            else text_background_color
        )
        lead_in_background_color = (
            lead_in_background_color.replace("on_", "")
            if lead_in_background_color
            else lead_in_background_color
        )

        # If we're not in IPython, display as text
        if pd.core.config_init.is_terminal():
            lead_in_rendered = (
                f"{colored(_filter_emojis(lead_in), text_color, _format_background_color(lead_in_background_color))}: "
                if lead_in
                else ""
            )
            _print_router("", bypass_print_fn=True)  # White space
            _print_router(
                lead_in_rendered
                + f"{colored(_filter_emojis(text), text_color, _format_background_color(text_background_color))}",
                text_for_print_fn=text_for_print_fn,
            )
        else:  # Print stylish!
            lead_in_rendered = _lead_in(
                lead_in, lead_in_text_color, lead_in_background_color
            )
            _display_router(
                data=Markdown(
                    f"<{tag} style='text-align: left'>{lead_in_rendered + ' ' if lead_in_rendered else ''}<span style='color:{text_color}; background-color:{text_background_color}'>{_filter_emojis(text)}</span></{tag}>"
                ),
                data_for_print_fn=text_for_print_fn,
                bypass_print_fn=bypass_print_fn,
            )


def _warning(
    message: str, lead_in: str = "🐼🩺 Pandas Checks warning", clean_type: bool = False
) -> None:
    """Displays a warning message.

    Args:
        message: The warning message to display.
        lead_in: Optional lead-in text to display before the warning message.
        clean_type: Optional flag to remove the class type from the message, when running .check.dtype().

    Returns:
        None
    """
    _display_line(
        lead_in=lead_in,
        line=(
            # Funny story: When using check.dtype(), _display_line() of text including a Python class type (like pd.DataFrame) will garble the output.
            # Because <class gets parsed as html :D
            message.replace("<class ", "").rstrip(">.")
            if clean_type
            else message
        ),
        colors={"lead_in_text_color": "black", "lead_in_background_color": "yellow"},
    )


# -----------------------
# Tables
# -----------------------


def _print_table(
    table: Union[pd.DataFrame, pd.Series],
    title: Union[str, None],
    custom_print_fn_only: bool = False,
) -> None:
    """Prints a Pandas table in a terminal with an optional indent.

    Args:
        table: A DataFrame or Series.

    Returns:
        None
    """
    # Indent table
    indent_prefix = pd.get_option("pdchecks.indent_table_terminal")  # In spaces
    table_as_str = textwrap.indent(
        text=table.to_string(), prefix=" " * indent_prefix if indent_prefix else ""
    )
    # Prepend title
    if title:
        table_as_str = f"{_filter_emojis(title)}\n" + table_as_str
    _print_router(
        table_as_str,
        custom_print_fn_only=custom_print_fn_only,
    )


def _display_table(
    table: Union[pd.DataFrame, pd.Series], title: Union[str, None]
) -> None:
    """Renders a Pandas DataFrame or Series in an IPython/Jupyter environment with an optional indent.

    Args:
        table: The DataFrame or Series to display.
        title: Optional title for the table.

    Returns:
        None
    """
    if title:
        # Display the table title on its own line.
        # Bypasses custom_print_fn by default.
        _display_table_title(title)

    # Display on screen as HTML
    if isinstance(table, pd.Series):
        table_to_display = pd.DataFrame(table)
    else:
        table_to_display = table
    _render_html_with_indent(
        object_as_html=table_to_display.style.set_table_styles(
            [pd.get_option("pdchecks.table_row_hover_style")]
            if pd.get_option("pdchecks.table_row_hover_style")
            else []
        )
        .format(precision=pd.get_option("pdchecks.precision"))
        .to_html()
    )
    # Ensure we send it to the custom_print_fn too, if it exists
    # If table is a Series, we do not convert to DataFrame here
    _print_table(table, title=title, custom_print_fn_only=True)


def _display_table_title(
    line: str, lead_in: Union[str, None] = None, colors: Dict = {}
) -> None:
    """Displays a table title with optional formatting.

    Args:
        line: The title text to display.
        lead_in: Optional text to display before the title.
        colors: An optiona dictionary containing color options for the text and lead-in text. See details in docstring for _render_text()

    Returns:
        None
    """
    _render_text(
        line,
        tag=pd.get_option("table_title_tag"),
        lead_in=lead_in,
        colors=colors,
        bypass_print_fn=True,
    )


# -----------------------
# Plots
# -----------------------


def _display_plot() -> None:
    """Renders the active Pandas Checks matplotlib plot object in an IPython/Jupyter environment with an optional indent.

    Returns:
        None

    Note:
        It assumes the plot has already been drawn by another function, such as with .plot() or .hist().
    """
    if not pd.core.config_init.is_terminal():
        indent = pd.get_option("pdchecks.indent_table_plot_ipython")  # In pixels
        # Save the figure to a bytes buffer
        buffer = io.BytesIO()
        fig = (
            plt.gcf()
        )  # TODO: Get the figure from passing the `fig` argument to _display_plot() but without generating a UserWarning from matplotlib.
        fig.savefig(buffer, format="png")
        plt.close(fig)  # Don't show it at the bottom of the cell too
        buffer.seek(0)
        #  Encode the image to base64 string, then display it as HTML
        _display_router(
            data=HTML(
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
            ),
            bypass_print_fn=True,
        )


def _display_plot_title(
    line: str, lead_in: Union[str, None] = None, colors: Dict = {}
) -> None:
    """Displays a plot title with optional formatting.

    Args:
        line: The title text to display.
        lead_in: Optional text to display before the title.
        colors: An optional dictionary containing color settings for the text and lead-in text. See details in docstring for _render_text().

    Returns:
        None
    """
    _render_text(
        line,
        tag=pd.get_option("plot_title_tag"),
        lead_in=lead_in,
        colors=colors,
        # Since custom_print_fn won't get plot, don't render plot title there either
        bypass_print_fn=True,
    )


# -----------------------
# Text
# -----------------------


def _format_background_color(color: str) -> str:
    """Applies a background color to text used being displayed in the terminal.

    Args:
        color: The background color to format. See syntax in docstring for _render_text().

    Returns:
        The formatted background color.
    """
    return (
        color if not color else f"on_{color}" if not color.startswith("on_") else color
    )


def _lead_in(lead_in: Union[str, None], foreground: str, background: str) -> str:
    """Formats a lead-in text with colors.

    Args:
        lead_in: The lead-in text to format.
        foreground: The foreground color for the lead-in text. See syntax in docstring for _render_text().
        background: The background color for the lead-in text. See syntax in docstring for _render_text().

    Returns:
        The formatted lead-in text.
    """
    return (
        f"<span style='color:{foreground}; background-color:{background}'>{_filter_emojis(lead_in).strip()}</span>:"
        if lead_in
        else ""
    )


def _display_line(
    line: str, lead_in: Union[str, None] = None, colors: Dict = {}
) -> None:
    """Displays a line of text with optional formatting.

    Args:
        line: The text to display.
        lead_in: The optional text to display before the main text.
        colors: An optional dictionary containing color options for the text and lead-in text. See syntax in docstring for _render_text().

    Returns:
        None
    """
    _render_text(
        line,
        tag=pd.get_option("pdchecks.check_text_tag"),
        lead_in=lead_in,
        colors=colors,
    )


# ---------------------------------------------
# Main function for showing results of checks
# ---------------------------------------------


def _display_check(data: Any, name: Union[str, None] = None) -> None:
    """Renders the result of a Pandas Checks method.

    Args:
        data: The data to display, whether a DataFrame, Series, string, or other printable.
        name: The optional name of the check.

    Returns:
        None
    """
    # Are we in IPython/Jupyter?
    if not pd.core.config_init.is_terminal():
        # Is it a DF?
        if isinstance(data, pd.DataFrame):
            _display_table(data, title=name)
        # Or a Series we should format as a DF?
        elif isinstance(data, pd.Series):
            # For Series based on some Pandas outputs like memory_usage(),
            # don't show a column name of 0
            if data.name != 0 and data.name is not None:
                data = data.rename(data.name)
            else:
                data = data.rename("")
            _display_table(data, title=name)
        # Display the result on one line
        else:
            _display_line(f"{name}: {data}" if name else data)

    # We're in the terminal/command line
    else:
        if isinstance(data, (pd.DataFrame, pd.Series)):
            # Can't display styled tables or use IPython rendering
            # Print check name and data on separate lines
            _print_router("", bypass_print_fn=True)  # White space
            _print_table(data, title=name)
        else:
            _display_line(f"{name}: {data}" if name else data)
