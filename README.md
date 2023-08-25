# The audio game creation template

## Running from source

Pipenv is a tool that helps manage Python dependencies. To install Pipenv, you can use pip:

```sh
pip install pipenv
```

Once Pipenv is installed, you can install the dependencies for this project by running:

```sh
pipenv install
```

This will install all of the dependencies specified in the Pipfile.

To play the game, run the command below in the root folder of this repository on a Windows machine:

```sh
pipenv run python game.py
```

This will run the game using the dependencies installed in the virtual environment.

## Build the game.

First, please edit libs/version.py, changing the version to something compatible with semantic versioning, by changing the major, miner or patch arguments for the initializer you'll find there. 

now, commit the change you have just made to that file.

Next, tag the release:

```sh
git tag X.Y.Z -am "Release X.Y.Z"
```

Where `X`, `Y`, and `Z` are the major, minor, and patch numbers, respectively.
