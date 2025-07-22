Awesome Indexer
===============

Generate little search engines and indexes of useful resources like:

- [Awesome Lists](https://github.com/sindresorhus/awesome/blob/main/awesome.md)
- [Zotero Collections]()
- [Zenodo Groups]()

## Usage

_TBA_

## Development setup

- Requires Python 3.11+

### Linux/WSL2

```bash
sudo apt install python3.11
sudo apt install python3.11-venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install .

awindex test-config.yml
```

Then open `test.html` in a browser.

Or to run from source rather than the installed version (during development):

```bash
python -m awindex.cli
```