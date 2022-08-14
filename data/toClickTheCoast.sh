if [ $# -eq 0 ]; then
    echo "No arguments provided - path to Click-The-Coast app needed"
    exit 1
fi
mkdir -p $1/data/output
cp -R output/web $1/data/output
