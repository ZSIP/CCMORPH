# example_2011: 
# ./ctc-download.sh example_2011_data/output/web/results

APP="ccmorph-ctc"
OFF='\033[0m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m' 

source env/bin/activate

if [ ! -d "$1" ]
then
    echo "The first argument should be the path to the local directory where results from the web application are to be saved (e.g.: ./docker.sh example_2011_data/output/web/results) "
    exit
fi

docker cp "$APP:/var/www/html/data/web/results/manual.csv" "$1"
