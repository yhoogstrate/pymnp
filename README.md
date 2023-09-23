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

1. configure credentials (see above)

```
virtualenv -p python 3 .venv
source .venv/bin/activate

pip install --no-cache-dir -U .

./scripts/pymnp-server.sh
```


# usage downloader

1. configure credentials (see above)

```
virtualenv -p python 3 .venv
source .venv/bin/activate

pip install --no-cache-dir -U .

./bin/api_example_download_all.py

ls ./cache
```
