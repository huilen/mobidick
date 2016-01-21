# mobidick
Dictionary generator for Kindle

# Requirements

## dictd

```
yaourt -S dictd [dict-freedict-fra-en]
```

## aspell

```
pacman -S aspell [aspell-fr]
```

## python

```
pacman -S python virtualenv
```

## kindlegen

Download from Kindle web page and put it in the path.

## virtualenv

```
pacman -S virtualenv
cd <mobidick_path>
virtualenv venv
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

You have an example file at config/example.json

# Run

```
python mobidick.py --settings fr_en.json
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
python test_mobidick.py --settings config/fr_en.json
```
