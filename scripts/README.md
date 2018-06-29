# The SCRIPTS

## How to remove flowcells

```
bash fcs_rm.bash <(bash fcs_ls.bash /mnt/hds/proj/bioinfo/DEMUX/ 2018-03-01)
```

`bash fcs_ls.bash /mnt/hds/proj/bioinfo/DEMUX/ 2018-03-01` will list all demux dirs that are younger than 2018-03-01.

`bash fcs_rm.bash` will delete all flowcells provided to it. It will skip flowcells that have samples that are actively being analyzed.

