from setuptools import setup

setup(
    name="cwc_cartes",
    version="1.0",
    packages=["cwc_cartes"],
    url="",
    license="MIT",
    author="Aubustou",
    author_email="survivalfr@yahoo.fr",
    description=(
        "Create helper cards for Cold War Commander from list of units and " "pictures"
    ),
    python_requires=">=3.9",
    install_requires=[
        "setuptools==65.5.1",
        "Pillow==9.3.0",
        "apischema==0.14.7",
        "requests==2.25.1",
    ],
)
