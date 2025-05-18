from nox import Session, options
from nox_uv import session

options.default_venv_backend = "uv"


@session(
    python=["3.9", "3.10", "3.11", "3.12", "3.13"],
    uv_groups=["test"],
)
def test(s: Session) -> None:
    """Run the test suite."""
    s.install(".")  # Install pandas-checks
    s.run("pytest")


# def tests(session: Session) -> None:

#     # session.install(
#     #     "pytest", "pytest-cases", "pyarrow", "openpyxl"
#     # )  # Install test packages

#     session.run("pytest")
