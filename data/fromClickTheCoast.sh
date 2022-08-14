if [ $# -eq 0 ]; then
    echo "No arguments provided - path to Click-The-Coast app needed"
    exit 1
fi
cp $1/data/output/web/results/manual.csv output/web/results
