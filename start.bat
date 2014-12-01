echo "Starting gateway..."
python py/gateway.py 80 >> gateway.log 
#
echo "Starting photo..."
python py/photo.py 81 >> photo.log 