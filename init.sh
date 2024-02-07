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

echo -e "$YELLOW---> Prepare demo data$OFF"
cat demo/sample_1/input/dem/sample_1.tif_* > demo/sample_1/input/dem/sample_1.tif
cat demo/sample_2/input/dem/sample_2.tif_* > demo/sample_2/input/dem/sample_2.tif
cat demo/sample_3/input/dem/sample_3.tif_* > demo/sample_3/input/dem/sample_3.tif
cat demo/sample_4/input/dem/sample_4.tif_* > demo/sample_4/input/dem/sample_4.tif
cat demo/sample_5/input/dem/sample_5.tif_* > demo/sample_5/input/dem/sample_5.tif
rm demo/sample_1/input/dem/sample_1.tif_*
rm demo/sample_2/input/dem/sample_1.tif_*
rm demo/sample_3/input/dem/sample_1.tif_*
rm demo/sample_4/input/dem/sample_1.tif_*
rm demo/sample_5/input/dem/sample_1.tif_*
