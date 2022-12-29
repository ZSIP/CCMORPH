OFF='\033[0m'
YELLOW='\033[0;33m'
base=`pwd`

source env/bin/activate

test_unzip=`unzip -v > /dev/null`
if [ $? -eq 127 ]
then
    echo $test_unzip
    echo "Install unzip command (eg. sudo apt install unzip)"
    exit
fi

if [ $# -ne 1 ] || [ "$1" != '--recount' ]
then
    echo -e "$YELLOW---> Example 2017: prepare input data$OFF"
    unzip -o example_2017_data.zip
    echo -e "$YELLOW---> Example 2017: prepare configs$OFF"
    cp example_2017_data/generator-py.config.json generator-py/config.json
    cp example_2017_data/shaper-py.config.json shaper-py/config.json
    cp example_2017_data/analyzer-py.config.json analyzer-py/config.json
fi
echo -e "$YELLOW---> Example 2017: run generator-py$OFF"; cd generator-py; python3 main.py &&
( echo -e "$YELLOW---> Example 2017: run shaper-py$OFF"; cd ../shaper-py; python3 main.py &&
( echo -e "$YELLOW---> Example 2017: run analyzer-py$OFF"; cd ../analyzer-py; python3 main.py ) )

cd $base