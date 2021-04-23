# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

About changelog [here](https://keepachangelog.com/en/1.0.0/)

Please add a new candidate release at the top after changing the latest one. Feel free to copy paste from the "squash and commit" box that gets generated when creating PRs

## [x.x.x]

### Added
### Changed
### Fixed

## [3.2.1]

### Changed
- Replace ruamel.yaml with pyyaml for consistency in prod environment
- Deleted unused Pipfile and Pipfile.lock since they trigger dependabots


## [3.2.0]

### Added
- Adds option `--compact` or `-c` to concatenate filenames with subsequent integer name suffixes
### Changed
### Fixed

## [3.1.0]

### Added

- Adds Dockerfile
- Add workflow for automatic publish to docker-hub
- Add __main__ script to run housekeeper without installing

## [3.0.1]

### Changed
- Removed weird clean flowcell scripts from scripts/ folder

## [3.0]
### Changed
- Reworks the CLI for complete API functionality

## [2.7.5]
### Added
- Automatic publish to pypi
