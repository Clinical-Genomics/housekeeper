# Housekeeper
![Housekeeper tests][github-url] [![Coverage Status][coveralls-image]][coveralls-url] [![CodeFactor][codefactor-image]][codefactor-url] [![Code style: black][black-image]][black-url]

### Store, tag, fetch, and archive files with ease 🗃

**Housekeeper** is a tool that aims to provide:

- a backend for storing versioned bundles of files
- different interfaces (Python, CLI, REST) for fetching files based on tags
- a way to backup and retrieve bundles from long-term storage

## Installation

Housekeeper written in Python 3.6+ and is available on the [Python Package Index][pypi] (PyPI).

```bash
poetry install
```

If you would like to install the latest development version:

```bash
git clone https://github.com/Clinical-Genomics/housekeeper
cd housekeeper
poetry install
```

## Contributing

Housekeeper is using GitHub flow branching model as described in our [development manual][development manual].

## Documentation

### Command line interface

#### Config file

Housekeeper supports a basic YAML config. The following options are supported:

```yaml
---
database: mysql+pymysql://userName:passWord@domain.com/database
root: /path/to/root/dir
```

The `root` option is used to store files within the Housekeeper context.

#### Command: `init`

Setup (or reset) the database. It will simply setup all the tables in the database. You can reset an existing database by using the `--reset` option.

```bash
housekeeper --database "sqlite:///hk.sqlite3" init
Success! New tables: bundle, file, file_tag_link, tag, version
```

#### Command: `include`

Include (hard-link) all files of an existing bundle version into Housekeeper and the `root` path.

```bash
housekeeper myBundle
```

This will only work if the bundle only has a single version which can be "imported". If you want to import a specific version of a bundle you can use the `--version` option.

#### Command: `delete files`

Delete files that are not on disk anymore like his:
`housekeeper delete files --tag fastq --notondisk`

Remove all bam files before a certain date:
`housekeeper delete files --tag bam --before 2017-06-15`

Remove fastq files from a flowcell:
`housekeeper delete files --tag fastq --tag H0HKKALXX`

It'll always ask for confirmation, unless you add --yes:
`housekeeper delete files --bundle sillyfish --yes`

If you do not provide a --tag or --bundle, essentially deleting everything, the function will not let you do that.

[pypi]: https://pypi.python.org/pypi/housekeeper/
[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/housekeeper
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/housekeeper.svg?style=flat-square
[github-url]: https://github.com/Clinical-Genomics/housekeeper/workflows/Housekeeper%20tests/badge.svg
[development manual]: http://www.clinicalgenomics.se/development/dev/githubflow/
[codefactor-image]: https://www.codefactor.io/repository/github/clinical-genomics/housekeeper/badge
[codefactor-url]: https://www.codefactor.io/repository/github/clinical-genomics/housekeeper
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black