# mobidick
Dictionary generator for Kindle

# Requirements

(All these instructions are given for Arch Linux.)

## dictd

```
yaourt -S dictd [dict-freedict-fra-en]
sudo systemctl start dictd
```

## aspell

```
sudo pacman -S aspell [aspell-fr]
```

## python

```
sudo pacman -S python virtualenv
```

## kindlegen

Download
[kindlegen](https://www.amazon.com/gp/feature.html?docId=1000765211)
from Kindle web page and add it to the PATH:

```
export PATH=$PATH:<kindlegen_path>
```

## virtualenv

```
sudo pacman -S virtualenv
cd <mobidick_path>
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Configuration

Create a configuration file for your dictionary:

```
{
    "language": "fr",
    "output": "dictionary.mobi",
    "language_from": "fr-fr",
    "language_to": "en-us"
}
```

You have this example file at config/example.json.

# Run

```
python mobidick.py --settings config/example.json
```

# Test

Add test words with some of their inflections to your dictionary file:

```
{
    "language": "fr",
    "output": "dictionary.mobi",
    "language_from": "fr-fr",
    "language_to": "en-us",
    "test_words": { 
	      "aimer": ["aime", "aimerais"],
	      "trancher": ["tranchait", "trancherait"],
	      "porter": ["portèrent", "porterait"]
    }
}
```

Run the tests:

```
python test_mobidick.py --settings config/example.json
```
