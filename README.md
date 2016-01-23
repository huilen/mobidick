# mobidick #

Dictionary generator for Kindle

## Requirements ##

(All these instructions are given for Arch Linux.)

### dictd ###

```
yaourt -S dictd [dict-freedict-fra-eng]
sudo systemctl start dictd
```

### aspell ###

```
sudo pacman -S aspell [aspell-fr]
```

### python ###

```
sudo pacman -S python virtualenv
```

### kindlegen ###

Download
[kindlegen](https://www.amazon.com/gp/feature.html?docId=1000765211)
from Kindle web page and configure its path in your configuration file
(see below):

### virtualenv ###

```
sudo pacman -S virtualenv
cd <mobidick_path>
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration ##

Create a configuration file for your dictionary:

```
{
    "title": "French-English Dictionary",
    "output": "/tmp/dictionary.mobi",
    "language_from": "fr-fr",
    "language_to": "en-us",
    "dictd_hostname": "localhost",
    "dictd_port": 2628,
    "dictd_database": "fra-eng",
    "snowball_language": "french",
    "aspell_language": "fr",
    "generator_cls": "mobidick.generator.Generator",
    "kindlegen_path": "<kindlegen_path>/kindlegen",
    "logging_level": "INFO"
}
```

You have this example file at config/example.json.

## Run ##

```
python mobidick.py --settings config/example.json
```

## Test ##

Add test words with some of their inflections to your dictionary file:

```
{
...
    "test_words": { 
	    "aimer": ["aime", "aimerais"],
    	"trancher": ["tranchait", "trancherait"],
	    "porter": ["portèrent", "porterait"]
    }
...
}
```

Run the tests:

```
python test_mobidick.py --settings config/example.json
```

## Extend Generator ##

You can extend from Generator class if you want to change the default
behavior. All you need to know is that there are four steps in
dictionary generation corresponding to the following Generator methods
that you can override:

1. words (get words from aspell)
2. stems (group words by stem using snowball)
3. definitions (add definitions from dictd)
4. templates (compile .opf and .html required templates)
5. mobi (call kindle generator)

You can, for example, override definitions if you want to lookup at
Wikipedia those words that are not found on dictd. Or you can override
words if you want to get words from other source than aspell.

You just need to extend Generator as it is shown at mobidick/custom.py
example:

```
from mobidick.generator import Generator


class SampleGenerator(Generator):

    def stems(self, words):
        stems = super(SampleGenerator, self).stems(words)
        return dict(list(stems.items())[0:25000])
```

And configure your class in your configuration file:

```
{
...
    "generator_cls": "mobidick.custom.SampleGenerator",
...
}
```

Then run the generator as always.

### Custom Generators ###

You can configure any of these generators through your configuration
file:

```
{
...
    "generator_cls": "mobidick.custom.<custom_generator>",
...
}
```

Of course, you can also extend from these generators as from the
Generator base class, if you want a more specific behavior.

##### MemoizedGenerator #####

Use this generator if you want to memoize steps. This is specially
useful for development.
