# Contributing to this Repository

The `dti-jupyter` application is intended for training and prototyping use by the DTI research community.

## Getting Started

### Recommended Development Environment
We recommend the following tools and configuration before cloning and developing:
* VSCode with the C3 developer experience extension.
* A working python environment, preferably via Anaconda, with some DTI and C3 tools installed (see below)

Example Python environment setup using Anaconda:
```
conda create -n c3py-3.9 python=3.9
conda install pytest jupyter
pip install git+https://github.com/c3aidti/c3python
```
Install the C3 command line application:
```
mkdir c3cli
cd c3cli
c3py get-c3cli
tar xzf cli.tar.gz
./c3 install
```

## Types of Contributions
Contributions to the `dti-jupyter` C3 application are generally accepted in the form of pull requests with the base branch being `main`.

Use the following guidelines to ensure your pull request is accepted:
* Ensure the code you are submitting is tested and provisions without errors to one of the development tags.
* Check the Github action status of the pull request to ensure it is passing all checks.  The dti-jupyter C3 application uses Github actions to provision the proposed changes to the `tc02` tag.
* Merged pull requests will be automatically deployed to the `tc01` tag.

### Seeded Jupyter Notebooks

Use the `c3py` command line utility to download the json seed data for a Notebook that has been saved to a tag in the dti ecosystem:

See the [c3python]() repo for more information.

### C3 Types and Methods 
