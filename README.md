pymnp - python API to access the MolecularNeuropathology web portal
-------------------------------------------------------------------

Python API for accessing: https://www.molecularneuropathology.org/mnp/
 - Plus proxy-server with new all-sample all-status interface, allowing re-running, killing and starting new jobs (`./scripts/pymnp-proxy-server.sh`).
 - Plus executable downloading and caching all completed jobs (`./bin/api_example_download_all.py`).

![pymnp](https://github.com/yhoogstrate/pymnp/raw/master/static/screenshot_01.png)


## Installation & usage

```
git clone https://github.com/yhoogstrate/pymnp.git
cd pymnp

virtualenv -p python3 .venv
source .venv/bin/activate

pip install -r requirements.txt -U .
```


# change to appropriate credentials:
```
cp config.txt.example config.txt

nano config.txt
```


# usage web server

1. install (see above)
2. configure credentials (see above)
3. run the proxy server:

```
virtualenv -p python 3 .venv
source .venv/bin/activate

./scripts/pymnp-proxy-server.sh
```

4. go to your browser and open: http://127.0.0.1:5000/
5. press the `[update-all-data]`-button
6. press `[f5]`


# usage downloader

1. ensure you have completed jobs
2. install (see above)
3. configure credentials (see above)
4. run the batch downloader:

```
virtualenv -p python 3 .venv
source .venv/bin/activate

./bin/api_example_download_all.py

ls ./cache
```
