from setuptools import setup, find_namespace_packages

setup(
    name="agc-research",
    version="0.1",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src", include=["*", "data_collection.*"]),
    install_requires=[
        "click",
        "pandas",
        "python-dotenv",
        "requests",
        "pyyaml"
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'agc-collect=src.cli:main',
        ],
    }
)