OFF='\033[0m'
YELLOW='\033[0;33m'  

SAMPLES="demo/sample_1 demo/sample_2 demo/sample_3 demo/sample_4 demo/sample_5"
TOOLS="generator finder analyzer"

for SAMPLE in $SAMPLES
do
    # copy configs
    for TOOL in $TOOLS
    do
        echo -e "$YELLOW[$SAMPLE] $TOOL $OFF"
        cp "$SAMPLE"/"$TOOL"_config.json tools/"$TOOL"-py/config.json
        cd tools/"$TOOL"-py/
        python3 ./main.py
        cd - > /dev/null 2> /dev/null
    done
    # run 
done