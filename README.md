# Housekeeper [![Build Status][travis-image]][travis-url] [![Coverage Status][coveralls-image]][coveralls-url]

Housekeeper is a tool for keeping track of **successful** analysis runs. It will manage various output files and metadata. It also provides archival functions. As far as possible, it's pipeline agnostic.

## Concerns

1.  store analysis output files _per_ run
2.  offer stable API to files and listing completed analyses
3.  keep track of status of analysis runs and files (active, archived, cleaned up)

It's outside the scope of the tool to store results and provide detailed access to them. Housekeeper will only provide easy access to reading in the data by other tools.

## Usage guide

### 1. Setup

The first thing to do is set up a root folder and database.

```bash
$ housekeeper --database sqlite:///path/to/store.sqlite3 init /path/to/analyses
```

If successful it will store the location of the root analyses folder in the database so no need for a separate config file - just keep pointing to the database.

### 2. Adding new analysis runs

Housekeeper can store files from completed analyses. Supported pipelines include:

-   MIP

```bash
$ housekeeper add /path/to/familyId_config.yaml
```

This command will do some pre-processing and collect assets to be linked. In the case of MIP it will pre-calculate the mapping rate since it isn't available in the main QC metrics file.

Housekeeper will create an analysis id in the format of `[customerId]-[familyId]`.

### 3. Deleting an existing analysis run

You can of course delete an analysis run you've stored in the database. It will remove the reference to the run along with all the links to the assets. It will keep a reference to the case, however.

```bash
$ housekeeper delete customer-family
Are you sure? [Y/n]
```

### 4. Getting files

This is where the fun starts! Since we have control over all the assets and how they relate to analyses and samples we can hand back information to you.

Say you wanted to know the path to the raw BCF file for a given analysis. Let's ask Housekeeper!

```bash
$ housekeeper get --\case customer-family --category bcf-raw
/path/to/root/analyses/customer-family/all.variants.bcf
```

Note that it will print to console without new line so you can just as well do:

```bash
$ ls -l $(housekeeper get --\case customer-family --category bcf-raw)
-rw-r--r--  2 robinandeer  staff    72K Jul 27 14:33 /path/to/root/analyses/customer-family/all.variants.bcf
```

> If multiple files match the query it will simply print them on one line separated by a single space.

### 5. Archiving analysis runs

When you add a new analysis you tell Housekeeper which files are eventually to be archived by assigning a "archive type": data or result. The archive process will take these files and bundle and compress them into two separate `tar.gz` archives that are places under the case directory (see below).

The database is also updated with checksums for the archives and paths to where archives are stored.

```bash
$ housekeeper archive customer-family
Are you sure? [Y/n]
```

### 6. Restoring an archive

```bash
$ housekeeper restore data /path/to/2016-04-12.data.tar.gz
```

When the archives were created, they were grouped with a special `meta.yaml` file which contains information about the run. This information will help out in putting the files back in place and updating the status in the database.

### 7. Cleaning up an analysis run

```bash
$ housekeeper clean customer-family
Are you sure? [Y/n]
```

This command will remove the whole run directory with all files similar to "delete". However, this command will keep the reference to the run in the database. The only thing which is lost are the references to files that weren't marked with an "archive_type".

This means that you can restore files from these runs using the command above.

Housekeeper will be careful about which runs it cleans up and check that they have been archived and delivered. To override this, supply the `--force` flag.

### 8. Postponing the date for clean up

Housekeeper provides a way to store a date (default 90 days after addition) for each run after which you could automate clean up of the files. If you want to manually extend the time before this happens you can run:

```bash
$ housekeeper postpone customer-family
```

## API structure and architecture

This section will describe the implementation.

### Store

SQL(ite) database containing references to the analyses and in which state they belong. It should have a straight-forward API to query which analyses have been completed and e.g. which are archived.

### CLI

Likely the main entry point for accessing the API. However, it should to do the least possible. Abstract away anything that isn't directly concerning parsing command line arguments etc. Uses the Click-framework.

## File structure

This section describes how analysis output will be stored on the file system level. It's important that this is an implementation detail that won't be exposed to third-party tools.

The goal is to create as structure that is as flat as possible while still maintaining the original file names as far as possible.

```
root/
├── housekeeper.yaml
├── store.sqlite3
└── analyses/
    └── analysis_1/
        └── 2016-04-12
            ├── alignment.sample_1.bam
            ├── variants.vcf
            └── traceback.log
```


[travis-url]: https://travis-ci.org/Clinical-Genomics/housekeeper
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/housekeeper.svg?style=flat-square

[coveralls-url]: https://coveralls.io/r/Clinical-Genomics/housekeeper
[coveralls-image]: https://img.shields.io/coveralls/Clinical-Genomics/housekeeper.svg?style=flat-square
