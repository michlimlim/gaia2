## How to run two clusters with devices

Run these on 4 separate terminals. You are running two clusters, each with its own cluster head, and where each cluster head knows each other. 
```
python main.py -me localhost:5000 -leader localhost:5000 -them localhost:5001 -otherleaders localhost:5002
```
```
python main.py -me localhost:5001 -leader localhost:5000 -them localhost:5000
```
```
python main.py -me localhost:5002 -leader localhost:5002 -them localhost:5003 -otherleaders localhost:5000
```
```
python main.py -me localhost:5003 -leader localhost:5002 -them localhost:5002
```