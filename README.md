# Pandas Checks
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pandas-checks)
  
<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/pandas-check-gh-social.jpg" alt="Banner image for Pandas Checks" style="max-height: 90px; width: auto;">  
    
Pandas Checks adds `.check` methods to Pandas so you can inspect method chains without cutting them up.  
  
As Fleetwood Mac says, [you would never break the chain](https://www.youtube.com/watch?v=xwTPvcPYaOo).

```python
import pandas_checks

iris_processed = (
    iris
    .dropna()
    .check.assert_positive(subset=["petal_length", "sepal_length"]) # 🐼🩺 Validate assumptions
    .check.hist(column='petal_length') # 🐼🩺 Plot the distribution of a column after cleaning

    .query("species=='setosa'")
    .check.head(3)  # 🐼🩺 Display the first few rows after more cleaning
    .check.write("iris_processed.parquet") # 🐼🩺 Export the interim data, with type inferred from name
)
```
<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/sample_output.jpg" alt="Sample output" width="350" style="display: block; margin-left: auto; margin-right: auto;  width: 50%;"/>
<br/><br/>
  
The `.check` methods didn't modify how `iris` data got processed. That's the difference between `.head()` and `.check.head()`.
  
## Table of Contents
  
> 💡 See the [docs](https://cparmet.github.io/pandas-checks/) for details and configuration options.

  * [Installation](#installation)
  * [`.check` methods](#check-methods)
    + [Assertions](#assertions)
    + [Describe data](#describe-data)
    + [Disable Pandas Checks](#disable-pandas-checks)
    + [Export interim files](#export-interim-files)
    + [Time your code](#time-your-code)
    + [Visualize data](#visualize-data)
  * [Giving feedback and contributing](#giving-feedback-and-contributing)
  * [License](#license)

## Installation

```bash
# With uv
uv add pandas-checks

# Or with pip
pip install pandas-checks
```
    
## `.check` methods  
Here's what's in the doctor's bag.

### Assertions
General:
- `.check.assert_data()` - Check that data passes an arbitrary condition, expressed as a lambda function - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_data) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_data)

Type assertions:
- `.check.assert_datetime()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_datetime) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_datetime)
- `.check.assert_float()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_float) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_float)
- `.check.assert_int()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_int) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_int)
- `.check.assert_str()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_str) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_str)
- `.check.assert_timedelta()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_timedelta) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_timedelta)
- `.check.assert_type()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_type) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_type)
  
Value assertions:
- `.check.assert_all_nulls()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_all_nulls) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_all_nulls)
- `.check.assert_less_than()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_less_than) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_less_than)
- `.check.assert_greater_than()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_greater_than) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_greater_than)
- `.check.assert_negative()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_negative) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_negative)
- `.check.assert_no_nulls()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_no_nulls) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_no_nulls)
- `.check.assert_nrows()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_nrows) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_nrows)
- `.check.assert_positive()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_positive) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_positive)
- `.check.assert_same_nrows()` - Confirm that the DataFrame/Series has the same number of rows as that of another DF/Series - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_same_nrows) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_same_nrows)
- `.check.assert_unique()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.assert_unique) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.assert_unique)

### Describe data
- `.check.columns()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.columns)
- `.check.describe()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.describe) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.describe)
- `.check.dtype()` - [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.dtype)
- `.check.dtypes()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.dtypes)
- `.check.function()` - Apply an arbitrary lambda function to your data and see the result - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.function) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.function)
- `.check.head()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.head) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.head)
- `.check.info()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.info) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.info)
- `.check.memory_usage()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.memory_usage) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.memory_usage)
- `.check.ncols()` - Count columns - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.ncols) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.ncols)
- `.check.ndups()` - Count rows with duplicate values - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.ndups) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.ndups)
- `.check.nnulls()` - Count rows with null values - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.nnulls) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.nnulls)
- `.check.nrows()` - Count rows - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.nrows) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.nrows)
- `.check.nunique()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.nunique) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.nunique)
- `.check.print()` - Print a string, a variable, or the current dataframe - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.print) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.print)
- `.check.shape()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.shape) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.shape)
- `.check.tail()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.tail) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.tail)
- `.check.unique()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.unique) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.unique)
- `.check.value_counts()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.value_counts) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.value_counts)

### Disable Pandas Checks
These methods can disable Pandas Checks methods, temporarily or permanently.
- `.check.disable_checks()` - Don't run checks. By default, still runs assertions. - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.disable_checks) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.disable_checks)
- `.check.enable_checks()` - Run checks again. - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.enable_checks) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.enable_checks)

### Export interim files
- `.check.write()` - Export the current data, inferring file format from the name - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.write) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.write)

### Time your code
- `.check.print_time_elapsed(start_time)` - Print the execution time since you called `start_time = pdc.start_timer()` - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.print_time_elapsed) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.print_time_elapsed)
<br></br>
  
> 💡 Tip:  You can use this stopwatch anywhere in your Python code.
> 
> ```python
> from pandas_checks import print_elapsed_time, start_timer
> 
> start_time = start_timer()
> ...
> print_elapsed_time(start_time)
> ```
        
### Visualize data
- `.check.hist()` - A histogram - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.hist) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.hist)
- `.check.plot()` - An arbitrary plot you can customize - [DataFrame](https://cparmet.github.io/pandas-checks/API%20reference/DataFrameChecks/#pandas_checks.DataFrameChecks.DataFrameChecks.plot) | [Series](https://cparmet.github.io/pandas-checks/API%20reference/SeriesChecks/#pandas_checks.SeriesChecks.SeriesChecks.plot)

## Giving feedback and contributing

If you run into trouble or have questions, I'd love to know. Please open an issue.

Contributions are appreciated! Please see [more details](https://cparmet.github.io/pandas-checks/#giving-feedback-and-contributing).

## License

Pandas Checks is licensed under the [BSD-3 License](https://github.com/cparmet/pandas-checks/blob/main/LICENSE).

🐼🩺
