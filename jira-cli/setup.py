from setuptools import setup, find_packages

setup(
    name="jira-cli",
    version="1.0.0",
    description="Jira Ticket Management CLI",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'jira-cli=jira_cli.cli:main',
        ],
    },
    python_requires=">=3.8",
)
