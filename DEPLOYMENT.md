# Deployment guide
This includes instructions for deploying Houskeeper in the Clinical Genomics :hospital: setting. General instructions for deployment is in the [development guide][development-guide]

## Steps
When all tests are done and successful and the PR is approved by codeowners, follow these steps:

1. Select "Squash and merge" to merge branch into default branch (master/main).
2. Append version increment value `( major | minor | patch )` in the commit message to specify what kind of release is to be created.
3. Review the details and merge the branch into master.
4. Deploy the latest version to stage and production with `housekeeper-deploy`.
5. Apply any migrations against the stage and prod databases with alembic.
    - Ensure that you have the latest revisions in your branch.
    - Ensure that you have the correct tunnels open against Hasta.
        ```bash
        ssh -fN -L 18002:localhost:18002 first_name.last_name@hasta.scilifelab.se # Stage
        ssh -fN -L 19002:localhost:19002 first_name.last_name@hasta.scilifelab.se # Production
        ```
    - Ensure that you point to the correct alembic config when you apply the revisions with `alembic --config <config path> upgrade head`
6. Take a screenshot or copy log text and post as a comment on the PR. Screenshot should include environment and that it succeeded.
7. Great job :whale2:

[development-guide]: http://www.clinicalgenomics.se/development/publish/prod/
