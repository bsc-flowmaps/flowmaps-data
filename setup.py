import setuptools
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

root = os.path.dirname(os.path.realpath(__file__))
requirementPath = root + '/requirements.txt'
install_requires = []
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name="flowmaps_data",
    version="0.0.14",
    author="Javier del Valle Contreras",
    author_email="javier.delvalle@bsc.es",
    description="A tool for downloading Spanish COVID-19 and mobility data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://flowmaps.life.bsc.es/flowboard/data",
    packages=setuptools.find_packages('.'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
    entry_points={
        'console_scripts': ['flowmaps-data=flowmaps_data:main'],
    }
)
