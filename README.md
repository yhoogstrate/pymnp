MolecularNeuropathology batch downloader
----------------------------------------

## Installation & usage

```
git clone https://github.com/yhoogstrate/MolecularNeuropathology-batch-downloader.git
cd MolecularNeuropathology-batch-downloader

virtualenv -p python3 .venv
source .venv/bin/activate

pip install tqdm requests

cp config.txt.example config.txt

# change to appropriate credentials:
nano config.txt



# usage
python run.py

ls cache
```
