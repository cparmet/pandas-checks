# 🐼🩺 Pandas Checks

## Introduction
**Pandas Checks** is a Python library for data science and data engineering. It adds non-invasive health checks for Pandas method chains.

It can inspect and validate your data at various points in your Pandas pipelines, without modifying the underlying data.

So you don't need to chop up a functional method chain, or create intermediate variables, every time you need to diagnose, treat, or prevent problems with data processing.

As Fleetwood Mac says, [you would never break the chain](https://www.youtube.com/watch?v=xwTPvcPYaOo).
  
  
> 💡 Tip:  
> See the [full documentation](https://cparmet.github.io/pandas-checks/) for all the details on the what, why, and how of Pandas Checks.
  
  
## Installation

```bash
pip install pandas-checks
```

## Usage
After installing Pandas Checks, import it:

```python
import pandas as pd
import pandas_checks
```

Now you can use `.check` on your Pandas DataFrames and Series. You don't need to access `pandas_checks` directly, just work with Pandas as you normally would. The new Pandas Checks methods are available when you work with Pandas in Jupyter, IPython, and terminal environments.

Here's a basic example of using Pandas Checks:

```python
iris = pd.read_csv('iris.csv')

iris_new = (
    iris
    .check.assert_data(lambda df: (df['sepal_width']> 0).all(), fail_message="Sepal width can't be negative")  # Validate your data
    # ... Do your data processing in here ...
    .check.hist(column='petal_length')  # Plot a distribution
    .check.head(3)  # Display the first few rows
)
```

The `.check` methods will display the following results:

<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/sample_output.jpg" alt="Sample output" width="350" style="display: block; margin-left: auto; margin-right: auto;  width: 50%;"/>
  
  
> ⓘ Note:  
> These methods did not modify `iris`. That's the difference between Pandas `.head()` and Pandas Checks `.check.head()`.
  
  
## Methods available
Here's what's in the doctor's bag.

* **Describe**
    - Standard Pandas methods:
        - `.check.columns()`
        - `.check.dtypes()` (`.check.dtype` for Series)
        - `.check.describe()`
        - `.check.head()`
        - `.check.info()`
        - `.check.memory_usage()`
        - `.check.nunique()`
        - `.check.shape()`
        - `.check.tail()`
        - `.check.unique()`
        - `.check.value_counts()`
    - New functions in Pandas Checks:
        - `.check.function()`: Apply an arbitrary lambda function to your data and see the result
        - `.check.ncols()`
        - `.check.ndups()`
        - `.check.nnulls()`
        - `.check.print()`: Print a string, a variable, or the current dataframe

* **Export interim files**
    - `.check.write()`: Export the current data, inferring file format from the name

* **Time your code**
    - `.check.print_time_elapsed(start_time)`: Print the execution time since you called `start_time = pdc.start_timer()`
    - Tip: You can also use the stopwatcht outside a method chain:
        ```python
        from pandas_checks import print_elapsed_time, start_timer

        start_time = start_timer()
        ...
        print_elapsed_time(start_time, units="seconds")
        ```

* **Turn off Pandas Checks**
    - `.check.disable_checks()`: Don't run checks in this method chain, for production mode etc
    - `.check.ensable_checks()`

* **Validate** Perform assertions on your data in the middle of a chain using `.check.assert_data()`.

* **Visualize**
    - `.check.hist()`: Histogram
    - `.check.plot()`: An arbitrary plot

## Customizing results

You can use Pandas Checks methods like the regular Pandas methods. They accept the same arguments. For example, you can pass:
* `.check.head(7)`
* `.check.value_counts(column="species", dropna=False, normalize=True)`
* `.check.plot(kind="scatter", x="sepal_width", y="sepal_length")`.

Also, most Pandas Checks methods accept 3 additional arguments:
1. `check_name`: text to display before the result of the check
2. `fn`: a lambda function that modifies the data displayed by the check
3. `subset`: limit a check to certain columns

```python
iris_new = (
    iris
    .check.value_counts(column='species', check_name="Varieties after data cleaning")
    .assign(species=lambda df: df["species"].str.upper()) # Do your regular Pandas data processing, like upper-casing the species column
    .check.head(n=2, fn=lambda df: df["petal_width"]*2) # Modify the data that gets displayed in the check only
    .check.describe(subset=['sepal_width', 'sepal_length'])  # Only check certain columns
)
```
<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/power_user_output.jpg" alt="Power user output" width="350" style="display: block; margin-left: auto; margin-right: auto;  width: 50%;">


## Global configuration
You can customize Pandas Checks:

```python
import pandas_checks as pdc

# Set output precision and turn off the cute emojis
pdc.set_format(precision=3, use_emojis=False)

# Don't run any of the calls to Pandas Checks, globally. Useful when switching your code to production mode
pdc.disable_checks()
```
  
    
> 💡 Tip:  
> Run `pdc.describe_options()` to see the arguments you can pass to `.set_format()`.
  
  
You can also adjust settings within a method chain. This will set the global configuration. So if you only want the settings to be changed during the method chain, reset them at the end.

```python
# Customize format
iris_new = (
    iris
    .check.set_format(precision=7, use_emojis=False)
    ... # Any .check methods in here will use the new format
    .check.reset_format() # Restore default format
)

# Turn off Pandas Checks
iris_new = (
    iris
    .check.disable_checks()
    ... # Any .check methods in here will not be run
    .check.enable_checks() # Turn it back on for the next code
)
```

## Giving feedback and contributing

If you run into trouble or have questions, I'd love to know. Please open an issue.

Contributions are appreciated! Please see [more details](https://cparmet.github.io/pandas-checks/#giving-feedback-and-contributing).


## License

Pandas Checks is licensed under the [BSD-3 License](https://github.com/cparmet/pandas-checks/blob/main/LICENSE).

🐼🩺
