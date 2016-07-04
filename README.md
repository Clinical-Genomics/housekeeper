# Housekeeper

Housekeeper is a tool to be used to keep track of **successful** analyses. It will keep track of various output files and metadata. It also provides archival functions. It's pipeline agnostic as far as possible.

## Concerns

1. Store access to analysis output files
2. Offer public API of known analyses
3. Keep track of status of analyses (active, archived, backed-up)
4. Offer option to retrieve archived files

## Proposed data flow

1. Analysis is completed successfully
2. Relay relevant output files to "housekeeper"
3. Ask "housekeeper" for access to info/files to e.g. upload to visualization
4. List analyses that have been completed with 'mip' pipeline in the last 7 days
5. Archive an analysis along with relevant files
6. Bring back already archived files from an analysis

## Analysis record

Will need to keep track and offer a general API into various analyses. This is an abstraction of a general analysis. An analysis can contain multiple samples.

1. Assets: CRAM (alignment, per sample), BCF (variants), archive (misc.)
2. Status: an analysis can be "active" or "archived"
3. Pipeline: how was data generated on a high level (and when)
4. Input: what input was used to start the analysis (samples + metadata)
5. Traceback + logging: store arbitrary files, logs, configs, data
6. Delivery: tar an archive containing all assets to deliver?

It's outside the scope of the tool to store results and provide detailed access to them. Housekeeper will only provide easy access to reading in the data by other tools.

**QUESTION**: should we allow for samples to belong to multiple analyses?

## API structure

This section will describe the implementation.

### Store

SQL(ite) database containing references to the analyses and in which state they belong. It should have a straight-forward API to query which analyses have been completed and e.g. which are archived.

Models:

- Analysis: keep track of essential files, metadata, status

### CLI

Likely the main entry point for accessing the API. However, it should to do the least possible. Abstract away anything that isn't directly concerning parsing command line arguments etc. Uses the Click-framework.

### Web interface

Built using the Flask-framework. Barebones. Should provide overviews for analyses in different states. Could additionally provide access to manually archiving/unarchiving analyses.

### Manage

This is the part that contains tools specific to each pipeline and which will gather all the necessary output and metadata to be stored in the new data structure.

The tool knows about assets in three levels:

1. Mandatory: special files that highly general across different pipelines
    - this is enforced on the "manage"-level for each pipeline
2. Known: special file types that are common across many pipelines
3. Misc.: any files that are specific on two a few pipelines

**Proposed flow**

1. You want me to store some files? Sure, what do you want to call the analysis?
2. What pipeline was used and which version? When was it run?
4. Which samples where included?
3. Tell me which files to (hard) link:
    1. File; what's the path and category?
    2. Does the file belong to a specific sample?
    3. Do you which to include this file when archiving the analysis?
    4. Here is the unique id you can use to refer to this asset in the future!

When we get confirmation that the take-over is complete we can go ahead and completely remove the analysis structure - but that's the scope of a different tool!

**Supported pipelines**:

- MIP

### Archive and _Un_archive

Will provide functions to archive analyses and bring back files that have been backed up. It will also contain the logic for automatically removing files that have been stored for "long enough". There should be an option to postpone this deadline in the API.

## File structure

This section describes how analysis output will be stored on the file system level. It's important that this is an implementation detail that won't be exposed to third-party tools.

The goal is to create as structure that is as flat as possible while still maintaining the original file names as far as possible.

```
root/
├── analysis_1/
│   ├── alignment.sample_1.bam
│   ├── variants.vcf
│   └── traceback.log
└── analysis_2/
    ├── alignment.sample_1.cram
    ├── alignment.sample_2.cram
    └── variants.vcf
```
