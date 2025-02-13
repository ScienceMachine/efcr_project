from setuptools import setup

setup(
    name="backend",
    version="0.0.1",
    description="simple eCFR analysis app backend",
    author="Me",
    author_email="coolio@american-gladiator.net",
    packages=["backend"],
    install_requires=[
        "Flask",
        "flask-cors",
        "lxml",
        "psycopg2-binary",
        "requests",
        "SQLAlchemy",
    ],
)
