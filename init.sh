OFF='\033[0m'
YELLOW='\033[0;33m'  

echo -e "$YELLOW---> Create and activate a virtual Python environment$OFF"
python3 -m venv env
source env/bin/activate

echo -e "$YELLOW---> Install binary packages (gdal & rtree)$OFF"
sudo apt install gdal-bin libgdal-dev python3-rtree

echo -e "$YELLOW---> Install requirements (Python libraries)$OFF"
GV=`gdalinfo --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+"`
echo "GDAL==$GV" | cat requirements - > requirements.txt
pip install -r requirements.txt
