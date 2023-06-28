pymnp - python API to access the MolecularNeuropathology web portal
-------------------------------------------------------------------

Python API for batch downloading reports present in the (brain)
classifier portal at https://www.molecularneuropathology.org/mnp/

## Installation & usage

```
git clone https://github.com/yhoogstrate/MolecularNeuropathology-batch-downloader.git
cd MolecularNeuropathology-batch-downloader

virtualenv -p python3 .venv
source .venv/bin/activate

pip install -r requirements.txt -U .

cp config.txt.example config.txt

# change to appropriate credentials:
nano config.txt



# usage
python run.py

ls cache
```
