shopt -s expand_aliases
source ~/.bashrc

# get all cases
# check if a case is in TB
# if not -> delete
# if yes -> delete through TB

read -a CASES <<< $(housekeeper runs -o case -l 1000 --before 2017-07-24 --after 2017-07-13)

for CASE in "${CASES[@]}"; do
    [[ ! $CASE =~ cust ]]  && continue
    [[ $CASE =~ cust000 ]] && continue

    echo -n $CASE

    FOUND=$(trailblazer list $CASE 2>&1)
    if [[ $FOUND =~ sorry ]]; then
        echo " skipping ..."
        #CUST=${CASE%%-*}
        #FAM=${CASE#*-}
        #CASEDIR="/mnt/hds/proj/bioinfo/MIP_ANALYSIS/customers/${CUST}/${FAM}/"

        #ls -l ${CASEDIR}
        #read -p "rm -rf ${CASEDIR}? " yn
        #case $yn in
        #    [Yy] ) rm -rf ${CASEDIR};;
        #    * ) echo 'Skipping ...';;
        #esac
    else
        trailblazer delete --yes $CASE
    fi
done
