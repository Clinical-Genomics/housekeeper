# Deployment guide
This includes instructions for deploying Houskeeper in the Clinical Genomics :hospital: setting. General instructions for deployment is in the [development guide][development-guide]

## Steps
When all tests done and successful and PR is approved by codeowners, follow these steps:

1. Select "Squash and merge" to merge branch into default branch (master/main).
2. Append version increment value `( major | minor | patch )` in the commit message to specify what kind of release is to be created.
3. Review the details and merge the branch into master.
4. First deploy on stage so log into hasta and run:
    - `us`
    - `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-housekeeper-stage.sh master`
5. Deploy in productions by running the following commands:
    - `down`
    - `up`
    - `bash /home/proj/production/servers/resources/hasta.scilifelab.se/update-housekeeper-prod.sh`
6. Take a screenshot or copy log text and post as a comment on the PR. Screenshot should include environment and that it succeeded.
7. Great job :whale2:

[development-guide]: http://www.clinicalgenomics.se/development/publish/prod/
