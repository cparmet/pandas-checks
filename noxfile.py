from nox_poetry import Session, session


@session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session: Session) -> None:
    """Run the test suite."""

    session.install(".")  # Install pandas-vet
    session.install(
        "pytest", "pytest-cases", "pyarrow", "openpyxl"
    )  # Install test packages

    session.run("pytest")
