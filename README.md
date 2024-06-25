# Pandas Checks
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pandas-checks)
  
<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/pandas-check-gh-social.jpg" alt="Banner image for Pandas Checks">  
  
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
  
```python
import pandas_checks
```
    
It works in Jupyter, IPython, and Python scripts run from the command line.  
  
## Usage
Pandas Checks adds `.check` methods to Pandas DataFrames and Series.  
  
Say you have a nice function.

```python
def clean_iris_data(iris: pd.DataFrame) -> pd.DataFrame:
    """Preprocess data about pretty flowers.

    Args:
        iris: The raw iris dataset.

    Returns:
        The cleaned iris dataset.
    """

    return (
        iris
        .dropna() # Drop rows with any null values
        .rename(columns={"FLOWER_SPECIES": "species"}) # Rename a column
        .query("species=='setosa'") # Filter to rows with a certain value
    )
```

But what if you want to make the chain more robust? Or see what's happening to the data as it flows down the pipeline? Or understand why your new `iris` CSV suddenly makes the cleaned data look weird? 
  
You can add some `.check` steps.

```python

(
    iris
    .dropna()
    .rename(columns={"FLOWER_SPECIES": "species"})

    # Validate assumptions
    .check.assert_positive(subset=["petal_length", "sepal_length"])

    # Plot the distribution of a column after cleaning
    .check.hist(column='petal_length') 

    .query("species=='setosa'")
    
    # Display the first few rows after cleaning
    .check.head(3)  
)
```

The `.check` methods will display the following results:

<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/sample_output.jpg" alt="Sample output" width="350" style="display: block; margin-left: auto; margin-right: auto;  width: 50%;"/>
  
  
The `.check` methods didn't modify how the `iris` data is processed by your code. They just let you check the data as it flows down the pipeline. That's the difference between Pandas `.head()` and Pandas Checks `.check.head()`.
  
  
## Features
### Check methods
Here's what's in the doctor's bag.

* **Describe**
    - Standard Pandas methods:
        - `.check.columns()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.columns) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.columns)
        - `.check.dtypes()` for [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.dtypes) | `.check.dtyp()` for [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.dtype)
        - `.check.describe()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.describe) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.describe)
        - `.check.head()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.head) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.head)
        - `.check.info()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.info) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.info)
        - `.check.memory_usage()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.memory_usage) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.memory_usage)
        - `.check.nunique()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.nunique) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.nunique)
        - `.check.shape()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.shape) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.shape)
        - `.check.tail()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.tail) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.tail)
        - `.check.unique()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.unique) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.unique)
        - `.check.value_counts()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.value_counts) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.value_counts)
    - New functions in Pandas Checks:
        - `.check.function()`: Apply an arbitrary lambda function to your data and see the result - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.function) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.function)
        - `.check.ncols()`: Count columns - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.ncols) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.ncols)
        - `.check.ndups()`: Count rows with duplicate values - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.ndups) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.ndups)
        - `.check.nnulls()`: Count rows with null values - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.nnulls) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.nnulls)
        - `.check.print()`: Print a string, a variable, or the current dataframe - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.print) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.print)

* **Export interim files**
    - `.check.write()`: Export the current data, inferring file format from the name - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.write) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.write)

* **Time your code**
    - `.check.print_time_elapsed(start_time)`: Print the execution time since you called `start_time = pdc.start_timer()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.print_time_elapsed) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.print_time_elapsed)
    - 💡 Tip:  You can also use this stopwatch outside a method chain, anywhere in your Python code:  

        ```python
        from pandas_checks import print_elapsed_time, start_timer

        start_time = start_timer()
        ...
        print_elapsed_time(start_time)
        ```
        
* **Turn off Pandas Checks**
    - `.check.disable_checks()`: Don't run checks, for production mode etc. By default, still runs assertions. - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.disable_checks) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.disable_checks)
    - `.check.enable_checks()`: Run checks - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.enable_checks) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.enable_checks)

* **Validate** 
    - *General*
        - `.check.assert_data()`: Check that data passes an arbitrary condition - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_data) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_data)
    - *Types*
        - `.check.assert_datetime()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_datetime) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_datetime)
        - `.check.assert_float()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_float) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_float)
        - `.check.assert_int()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_int) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_int)
        - `.check.assert_str()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_str) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_str)
        - `.check.assert_timedelta()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_timedelta) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_timedelta)
        - `.check.assert_type()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_type) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_type)
    - *Values*
        - `.check.assert_less_than()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_less_than) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_less_than)
        - `.check.assert_greater_than()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_greater_than) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_greater_than)
        - `.check.assert_negative()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_negative) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_negative)
        - `.check.assert_not_null()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_not_null) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_not_null)
        - `.check.assert_null()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_null) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_null)
        - `.check.assert_positive()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_positive) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_positive)
        - `.check.assert_unique()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_unique) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_unique)

* **Visualize**
    - `.check.hist()`: A histogram - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.hist) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.hist)
    - `.check.plot()`: An arbitrary plot you can customize - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.plot) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.plot)

### Customizing a check

You can use Pandas Checks methods like the regular Pandas methods. They accept the same arguments. For example, you can pass:
* `.check.head(7)`
* `.check.value_counts(column="species", dropna=False, normalize=True)`
* `.check.plot(kind="scatter", x="sepal_width", y="sepal_length")`

Also, most Pandas Checks methods accept 3 additional arguments:
1. `check_name`: text to display before the result of the check
2. `fn`: a lambda function that modifies the data displayed by the check
3. `subset`: limit a check to certain columns

```python
(
    iris
    .check.value_counts(column='species', check_name="Varieties after data cleaning")
    .assign(species=lambda df: df["species"].str.upper()) # Do your regular Pandas data processing, like upper-casing the values in one column
    .check.head(n=2, fn=lambda df: df["petal_width"]*2) # Modify the data that gets displayed in the check only
    .check.describe(subset=['sepal_width', 'sepal_length'])  # Only apply the check to certain columns
)
```
<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/power_user_output.jpg" alt="Power user output" width="350" style="display: block; margin-left: auto; margin-right: auto;  width: 50%;">


### Configuring Pandas Check
#### Global configuration
You can change how Pandas Checks works everywhere. For example:

```python
import pandas_checks as pdc

# Set output precision and turn off the cute emojis
pdc.set_format(precision=3, use_emojis=False)

# Don't run any of the calls to Pandas Checks, globally. Useful when switching your code to production mode
pdc.disable_checks()
```
    
Run `pdc.describe_options()` to see the arguments you can pass to `.set_format()`.
  
> 💡 Tip:  
> By default, `disable_checks()` and `enable_checks()` do not change whether Pandas Checks will run assertion methods (`.check.assert_*`).
> 
> To turn off assertions too, add the argument `enable_asserts=False`, such as: `disable_checks(enable_asserts=False)`.

#### Local configuration
You can also adjust settings within a method chain by bookending the chain, like this:

```python
# Customize format during one method chain
(
    iris
    .check.set_format(precision=7, use_emojis=False)
    ... # Any .check methods in here will use the new format
    .check.reset_format() # Restore default format
)

# Turn off Pandas Checks during one method chain
(
    iris
    .check.disable_checks()
    ... # Any .check methods in here will not be run
    .check.enable_checks() # Turn it back on for the next code
)
```

> 💡 Tip:  **Hybrid EDA-Prod data processing**
>    
> Exploratory data analysis (EDA) is traditionally thought of as the first step of data projects. But often when we're in production, we wish we could reuse parts of the EDA. Maybe we're debugging, editing prod code, or need to change the input data. Unfortunately, the EDA code is often too stale to fire up again. The prod pipeline has changed too much.  
>  
> If you used Pandas Checks during EDA, you can keep your `.check` methods in your first prod code. In production, you can disable Pandas Checks, but enable it when you need it. This can make your prod pipline more transparent and easier to inspect.  


## Giving feedback and contributing

If you run into trouble or have questions, I'd love to know. Please open an issue.

Contributions are appreciated! Please see [more details](https://cparmet.github.io/pandas-checks/#giving-feedback-and-contributing).

## License

Pandas Checks is licensed under the [BSD-3 License](https://github.com/cparmet/pandas-checks/blob/main/LICENSE).

🐼🩺
