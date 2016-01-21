import pickle
import re
import os
import logging
import json
import os
import sys
import getopt
import subprocess
import socket
import html

from datetime import datetime
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
from jinja2 import Environment, FileSystemLoader


logger = logging.getLogger('mobidick')
logging.basicConfig(level=logging.INFO)


def memoized(path_pattern):
    def memoize(fn):
        def memoize_wrapper(*args, **kwargs):
            try:
                path = path_pattern.format(**kwargs)
                with open(path, 'rb') as file:
                    logger.info("Loading pickle %s", path)
                    data = pickle.load(file)
            except (FileNotFoundError, EOFError):
                data = fn(*args, **kwargs)
                with open(path, 'wb') as file:
                    pickle.dump(dict(data), file)
            return data
        return memoize_wrapper
    return memoize


def configuration(argv):
    opts, args = getopt.getopt(
        argv, 's:', ['settings='])
    for opt, arg in opts:
        if opt in ('-s', '--settings'):
            with open(arg) as config:
                return json.load(config)
    raise ValueError("Must specify --settings")


def words(lang='en'):
    cmd = 'aspell -l {lang} dump master | aspell -l {lang} expand'
    aspell = subprocess.Popen(cmd.format(lang=lang),
                              shell=True, stdout=subprocess.PIPE)
    output = aspell.stdout.read().decode()
    return output.split('\n')[:-1]


@memoized('/tmp/stems_{lang}.pickle')
def stems(words, lang='en'):
    language = lang_from_code(lang)
    stems = defaultdict(lambda: {'inflections': []})
    stemmer = SnowballStemmer(language)
    logger.info("Finding stems")
    for idx, word in enumerate(words, start=1):
        stem = stemmer.stem(word)
        stems[stem]['inflections'].append(word)
        show_progress(idx, len(words))
    logger.info("{} stems found".format(len(stems)))
    return stems


@memoized('/tmp/definitions_{lang}.pickle')
def definitions(words, lang='en', hostname='localhost', port=2628):
    logger.info("Finding definitions")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hostname, port))
    def read():
        buffer = ''
        while True:
            buffer += sock.recv(1000).decode()
            match = re.match(r'(.*)^(220|552|250)[^\r\n]*\r\n', buffer,
                             re.MULTILINE|re.DOTALL)
            if match:
                response = match.group(1)
                code = int(match.group(2))
                return code, response
    def parse_definition(stem, word, response):
        definition = '\n'.join(l for l in response.split('\r\n')
                               if (not l.startswith('150') and
                                   not l.startswith('151')))
        definition = html.escape(definition)
        return definition
    code, _ = read()  # skip first line.
    assert code == 220
    count = 0
    for idx, stem in enumerate(words, start=1):
        for word in words[stem]['inflections']:
            cmd ='d {word}\n'.format(word=word)
            sock.send(cmd.encode())
            code, response = read()
            words[stem]['definitions'] = []
            if code == 552:
                logger.debug("Definition not found %s", word)
            elif code == 250:
                count += 1
                definition = parse_definition(stem, word, response)
                words[stem]['definitions'].append(definition)
                break
        show_progress(idx, len(words))
    sock.close()
    logger.info("{} definitions found".format(count))
    return words


def lang_from_code(code):
    if code == 'en': return 'english'
    if code == 'fr': return 'french'
    if code == 'it': return 'italian'
    if code == 'es': return 'spanish'
    raise NotImplementedError


def show_progress(completed, total):
    if completed != total:
        if completed % 1000 != 0:
            return
    percentage = completed / total * 100
    sys.stdout.write("\r{completed}/{total} ({percentage}%)".format(
        completed=completed, total=total, percentage=int(percentage)))
    sys.stdout.flush()
    if completed == total:
        sys.stdout.write('\r')
        sys.stdout.flush()


def templates(entries, config):
    logger.info("Compiling dictionary templates")
    env = Environment(loader=FileSystemLoader('templates'))
    template_opf = env.get_template('dictionary.opf')
    template_html = env.get_template('dictionary.html')
    language = lang_from_code(config['language']).capitalize()
    variables = {'entries': [e for e in entries.values() if 'definitions' in e],
                 'date': datetime.now().strftime('%d/%m/%Y'),
                 'default_text': '{} Dictionary'.format(language)}
    variables.update(config)
    opf = template_opf.render(variables)
    html = template_html.render(variables)
    return opf, html


def mobi(opf, html, output):
    logger.info("Generating mobi file")
    with open('/tmp/dictionary.opf', 'w') as opf_file:
        opf_file.write(opf)
    with open('/tmp/dictionary.html', 'w') as html_file:
        html_file.write(html)
    cmd = ['kindlegen',
           html_file.name,
           opf_file.name,
           '-verbose',
           '-o', output]
    kindlegen = subprocess.call(cmd)
    logger.info("Created at {}".format(output))


def generate(config):
    lang = config['language']
    output = config['output']
    mobi(
        *templates(
            definitions(
                stems(
                    words(lang),
                    lang=lang),
                lang=lang),
            config),
        output)
    logger.info("Dictionary created at {}".format(output))


if __name__ == '__main__':
    config = configuration(sys.argv[1:])
    generate(config)
