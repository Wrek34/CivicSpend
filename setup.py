from setuptools import setup, find_packages

setup(
    name="gnit",
    version="0.1.0-dev",
    packages=find_packages(),
    install_requires=[
        "duckdb>=0.9.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.3.0",
        "requests>=2.31.0",
        "click>=8.1.0",
        "rapidfuzz>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gnit=gnit.cli.main:cli",
        ],
    },
    python_requires=">=3.11",
)
