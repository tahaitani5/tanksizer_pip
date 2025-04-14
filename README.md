# Pip Installation Template
Generator project which can be used to generate a new Python project file structure.

## Project Structure
This project has the following structure:
- `template/` - Template files which will be copied and updated using Chevron
  - `example/` - Example directory
    - `recipe/` - Conda Build recipe directory
      - `meta.yaml` - template conda-build recipe file for the repository
    - `src/` - Source directory
      - `modelnamegoeshere/` - template module directory
    - `tests/` - Tests directory
      - `modelnamegoeshere/` - template module directory
    - `.gitignore` - template ignore file
    - `.gitlab-ci.yml` - template ci file
    - `.pypirc_cicd` - template ci twine submission file
    - `.pypirc.template` - template twine submission file
    - `create_conda_package.sh` - Script used to create an Anaconda package from the repository using Docker
    - `create_pip_package.sh` - Script used to create a Pip-installable package from the repository using Docker
    - `LICENSE` - template license file
    - `pyproject.toml` - template pip-installation configuration file; some contents replaced
    - `pytest.ini` - template pytest file
    - `README.md` - template readme; some contents replaced
    - `requirements.txt` - template requirements file
- `.gitignore` - Ignore file
- `build.sh` - The builder
- `pytest.ini` - Generator Pytest configuration file
- `README.md` - This file
- `requirements.txt` - Pip requirements file

## Setup New Project in GitLab
You can follow these steps to setup a new repository in GitLab:
- Create a new project in GitLab:
  1. Click `New Project`
  1. Click `Create blank project`
  1. Name your project
  1. Uncheck `Initialize repository with a README`
  1. Click `Create project`


## Setup and Run the Builder
On the command line with access to Python:
```
# Create a virtual environment for local usage
python -m venv venv

# Activate the environment
source venv/bin/activate

# Install the package requirements
pip install -r requirements.txt

# Copy the builder_config.template.json over to builder_config.json
cp builder_config.template.json builder_config.json

# Edit the values in builder_config.json for your project

# After copying builder_config and setting your values, you can run the builder with:  
./build.sh
```

## Example Config:
Here is an example of the contents of the `builder_config.json` file:
```
{
  "AUTHOR_EMAIL": "john.smith@nowhere.com",
  "AUTHOR_NAME": "John Smith",
  "INSTALLATION_PATH": "C:/Users/john.smith/Documents/test",
  "MAINTAINER_EMAIL": "john.smith@nowhere.com",
  "MAINTAINER_NAME": "John Smith",
  "MODULE_NAME": "test",
  "PROJECT_DESCRIPTION": "John Smith's test project",
  "PROJECT_GITLAB_URL": "http://www.gitlab.com/john.smith/test",
  "PROJECT_VERSION": "0.0.1"
}
```


## After Builder Run Steps
You'll need to perform the following after running `build.sh`:
- Put your code files in the `src/MODELNAMEHERE` directory
- Add any classes, functions, etc. that you wish to be exposed by the plugin to `src/MODELNAMEHERE/__init__.py`
- Add any tests to `tests/MODELNAMEHERE`
- Update the `.gitlab-ci.yml` file to add or remove any build templates or custom build commands
- Commit your code to GitLab


## Committing Initial Code to GitLab
In your created project root directory on the command line:
```
git init --initial-branch=main
git remote add origin PATH_TO_THE_PROJECT_YOU_CREATED_HERE_EITHER_SSH_OR_HTTPS
git add .
git commit -m "feat: Initial commit"
git push --set-upstream origin main
```

You should see your code in GitLab after a refresh of the page


## Pip Installation Template Project Structure
This project has the following structure:
- `template/` - Template files which will be copied and updated using Chevron
  - `example/` - Example directory
    - `recipe/` - Conda Build recipe directory
      - `meta.yaml` - template conda-build recipe file for the repository
    - `src/` - Source directory
      - `modelnamegoeshere/` - template module directory
        - `__init__.py` - Initial init file
    - `tests/` - Tests directory
      - `modelnamegoeshere/` - template module directory
        - `__init__.py` - Initial init file
      - `__init__.py` - Initial init file
    - `.gitignore` - template ignore file
    - `.gitlab-ci.yml` - template ci file
    - `.pypirc_cicd` - template ci twine submission file
    - `.pypirc.template` - template twine submission file
    - `LICENSE` - template license file
    - `pyproject.toml` - template pip-installation configuration file; some contents replaced
    - `pytest.ini` - template pytest file
    - `README.md` - template readme; some contents replaced
    - `requirements.txt` - template requirements file
- `.gitignore` - Ignore file
- `build.sh` - The builder
- `builder_config.template.json` - Template config file to copy over to `builder_config.json` for your project config
- `pytest.ini` - Generator Pytest configuration file
- `README.md` - This file
- `requirements.txt` - Pip requirements file


## Generated Project Structure
- `recipe/` - Conda Build recipe directory
  - `meta.yaml` - conda-build recipe file for the repository
- `src/` - Source directory
  - `modelnamegoeshere/` - module directory
    - `__init__.py` - init file
- `tests/` - Tests directory
  - `modelnamegoeshere/` - test module directory
    - `__init__.py` - init file
  - `__init__.py` - init file
- `.gitignore` - ignore file
- `.gitlab-ci.yml` - ci file
- `.pypirc_cicd` - ci twine submission file
- `.pypirc.template` - twine submission file
- `LICENSE` - license file
- `pyproject.toml` - pip-installation configuration file
- `pytest.ini` - pytest file
- `README.md` - readme
- `requirements.txt` - requirements file


## Authors
- [Russell Quick](russell.r.quick@nasa.gov)
