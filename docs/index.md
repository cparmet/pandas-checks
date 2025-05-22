---
title: About
---

<img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/pandas-check-gh-social.jpg" alt="Banner image for Pandas Checks" style="max-height: 200px; width: auto;">  
  
[TOC]

## What is it?

**Pandas Checks** is a Python package for data science and data engineering. It adds non-invasive health checks for [Pandas](https://github.com/pandas-dev/pandas/) method chains.  

## What are method chains?
Method chains are one of the [coolest features](https://tomaugspurger.net/posts/method-chaining/) of the Pandas library! They allow you to write more functional code with fewer intermediate variables and fewer side effects. If you're familiar with R, method chains are Python's version of [dplyr pipes](https://style.tidyverse.org/pipes.html).

## Why use Pandas Checks?

Pandas Checks adds the ability to inspect and validate your Pandas data at any point in the method chain, without modifying the underlying data. Think of Pandas Checks as a drone you can send up to check on your pipeline, whether it's in exploratory data analysis, prototyping, or production.

That way you don't need to chop up a method chain, or create intermediate variables, every time you need to diagnose, treat, or prevent problems with your data processing pipeline.

As Fleetwood Mac says, you would never break the chain.

<a href="https://www.youtube.com/watch?v=xwTPvcPYaOo"><img src="https://raw.githubusercontent.com/cparmet/pandas-checks/main/static/fleetwood-mac-the-chain.jpg" alt="Fleetwood Mac YouTube video for The Chain" target="_blank"></a>
  

## Giving feedback and contributing

If you run into trouble or have questions, I'd love to know. Please [open an issue](https://github.com/cparmet/pandas-checks/issues).

Contributions are appreciated! Please open an [issue](https://github.com/cparmet/pandas-checks/issues) or submit a [pull request](https://github.com/cparmet/pandas-checks/pulls). To run the tests, run `uv run --group dev nox`
  
## Acknowledgments
 
Pandas Checks uses the following wonderful libraries:

- [uv](https://github.com/astral-sh/uv) for package and dependency management
- [nox](https://nox.thea.codes/en/stable/) for test automation
- [mkdocs](https://www.mkdocs.org/) for...making docs!
- [pre-commit hooks](https://pre-commit.com/)
- [black](https://black.readthedocs.io/en/stable/) for code formatting

## License

Pandas Checks is licensed under the [BSD-3 License](https://github.com/cparmet/pandas-checks/blob/main/LICENSE).

🐼🩺
