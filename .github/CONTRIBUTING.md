# Contributing to this Repository

The `dti-jupyter` application is intended for training and prototyping use by the DTI research community.

Quick Start describes the basic contribution guidelines.  Additional details on types of contributions, recommende d development environment, and other details can be found below.

## Quick Start

### Contributing to a C3 DTI Development Tag

Each tag on the c3 deployment has an associated branch of the same name.  the procedure of to developing on a particular development tag is as follows:

1) Create a branch _from_ the tag-branch.  For example, if developing on the `tc01d` tag, create a branch `my_dev_branch` from the `tc01d` branch.
2) Push changes to your new branch.
3) Create a pull request to the `tc01d` branch.
4) Merge the pull request.

Provisioning to the target development branch will be triggered, in this case, by the pull request to the `tc01d` branch. If the provisioning fails, the merge will be blocked until additional commits are pushed to the `my_dev_branch` branch that resolve the errors.

<h2><details><summary>Recommended Development Environment</summary></h2>

We recommend the following tools and configuration before cloning and developing:
* VSCode with the C3 developer experience extension.
* A working python environment, preferably via Anaconda, with some DTI and C3 tools installed (see below)

Example Python environment setup using Anaconda:
```
conda create -n c3py-3.9 python=3.9
conda activate c3py-3.9
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
</details>

## Types of Contributions
Contributions to the `dti-jupyter` C3 application are generally accepted in the form of pull requests with the base branch being the assigned development tag (see quick start above).

Use the following guidelines to ensure your pull request is accepted:
* Ensure the code you are submitting is tested and provisions without errors to one of the development tags.
* Check the Github action status of the pull request to ensure it is passing all checks.  The dti-jupyter C3 application uses Github actions to provision the proposed changes to the target tag.

Merged pull requests to development tag branches will be automatically deployed to the production `tc01` tag upon automated migration to main on a regular schedule.

### C3 Types and Methods 

Use the following procedure to contribute a new package for prototyping:

1) Add a new directory <package-name> to the `training` directory.
2) Add a `package.json` file to the new directory.
3) List the new package asa dependency in `training/dti-jupyter/package.json`
4) Follow procedure in Quick start for pushing the changes and opening a pull request to the correct development branch.

### Seeded Jupyter Notebooks

Use the `c3py` command line utility to download the json seed data for a Notebook that has been saved to a tag in the dti ecosystem:

See the [c3python]() repo for more information.

