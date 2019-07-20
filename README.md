# Wiktionary Reader

The goal of this repository is to load Wiktionary in Python classes.

### Prerequisites
Python 3.6 was used to create this project. It might work with older versions of Python.

#### Python modules

A number of external modules need to be installed, which are listed in **requirements.txt**.
Depending on how you installed Python, you can probably install the requirements using one of following commands:
```bash
pip install -r requirements.txt
```

#### Resources
A number of GitHub repositories need to be cloned. This can be done calling:
```bash
bash install.sh
```

## How to use

1. `bash extract.sh` (takes hours) to extract the information from Wiktionary for the languages
you're interested in.
2. configure a config file (see example `config/en_it_du.json`)
3. load output into Python classes using `load_wiktionary.py'''
Perform the following call for more information about usage
```
python load_wiktionary.py -h
```
4. Check `how_to_use.py` for an example of how to use

## TODO
* the extractor seems to only capture translations from English to other languages, not from other languages to English.
* extend part of speech tagset (now only nouns, verbs, and adjectives are used)
    
## Authors
* **Marten Postma** (m.c.postma@vu.nl)

## License
This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
