# Housekeeper [![Build Status][travis-image]][travis-url] [![Coverage Status][coveralls-image]][coveralls-url]

### Store, tag, fetch, and archive files with ease 🗃

**Housekeeper** is a tool that aims to provide:

- a backend for storing versioned bundles of files
- different interfaces (Python, CLI, REST) for fetching files based on tags
- a way to backup and retrieve bundles from long-term storage

### Todo

- [ ] re-implement the archive/encryption interface [@ingkebil]
- [ ] handle clean up of expired bundles [@robinandeer]
- [ ] expand the CLI with `get` command etc. [@robinandeer]

## Installation

Housekeeper written in Python 3.6+ and is available on the [Python Package Index][pypi] (PyPI).

```bash
pip install housekeeper
```

If you would like to install the latest development version:

```bash
git clone https://github.com/Clinical-Genomics/housekeeper
cd housekeeper
pip install --editable .
```

## Documentation

### Command line interface

#### Config file

Housekeeper supports a very simple YAML config. The following options are supported:

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
Success! New tables: bundle, file, file_tag_link, tag, user, version
```

#### Command: `include`

Include (hard-link) all files of an existing bundle version into Housekeeper and the `root` path.

```bash
housekeeper myBundle
```

This will only work if the bundle only has a single version which can be "imported". If you want to import a specific version of a bundle you can use the `--version` option.

[pypi]: https://pypi.python.org/pypi/trailblazer/

[travis-url]: https://travis-ci.org/Clinical-Genomics/housekeeper
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/housekeeper.svg?style=flat-square
[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/housekeeper
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/housekeeper.svg?style=flat-square
