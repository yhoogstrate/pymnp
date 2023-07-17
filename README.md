pymnp - python API to access the MolecularNeuropathology web portal
-------------------------------------------------------------------

Python API for batch downloading reports present in the (brain)
classifier portal at https://www.molecularneuropathology.org/mnp/

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
