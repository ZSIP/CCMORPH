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

if [ "$1" != '--recount' ] && [ "$1" != '--analyse' ]
then
    echo -e "$YELLOW---> Example 2011: prepare input data$OFF"
    unzip -o example_2011_data.zip
    echo -e "$YELLOW---> Example 2011: prepare configs$OFF"
    mv example_2011_data/generator-py.config.json tools/generator-py/config.json
    mv example_2011_data/finder-py.config.json tools/finder-py/config.json
    mv example_2011_data/analyzer-py.config.json tools/analyzer-py/config.json
fi
if [ "$1" != '--analyse' ]
then
    echo -e "$YELLOW---> Example 2011: run generator-py$OFF"; cd tools/generator-py; python3 main.py
fi

if [ $? -eq 0 ] && [ "$1" != '--analyse' ]
then
    echo -e "$YELLOW---> Example 2011: run finder-py$OFF"; cd ../finder-py; python3 main.py
fi

if [ $? -eq 0 ]
then
    if [ "$base" != `pwd` ]
    then
        cd ..
    fi
    echo -e "$YELLOW---> Example 2011: run analyzer-py$OFF"; cd analyzer-py; python3 main.py
fi

cd $base