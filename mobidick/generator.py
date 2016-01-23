import shutil
import re
import os
import logging
import os
import sys
import subprocess
import socket
import html

from datetime import datetime
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
from jinja2 import Environment, FileSystemLoader

from mobidick.utils import memoized, print_progress, configuration, load_class


logger = logging.getLogger(__name__)


class Generator(object):

    def __init__(self, config):
        self.config = config

    def words(self):
        logger.info("Finding words")
        cmd = 'aspell -l {lang} dump master'
        aspell = subprocess.Popen(cmd.format(lang=self.config['aspell_language']),
                                  shell=True, stdout=subprocess.PIPE)
        output = aspell.stdout.read().decode()
        words = output.split('\n')[:-1]
        logger.info("{} words found".format(len(words)))
        return words

    @memoized('/tmp/stems.pickle')
    def stems(self, words):
        language = self.config['snowball_language']
        stems = defaultdict(lambda: {'inflections': []})
        stemmer = SnowballStemmer(language)
        logger.info("Finding stems")
        for idx, word in enumerate(words, start=1):
            message = "{} stems found".format(len(stems))
            print_progress(idx, len(words), message)
            stem = stemmer.stem(word)
            stems[stem]['inflections'].append(word)
        logger.info(message)
        return dict(stems)

    @memoized('/tmp/definitions.pickle')
    def definitions(self, words):
        logger.info("Finding definitions")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.config['dictd_hostname'],
                      self.config['dictd_port']))
        def read():
            buffer = ''
            while True:
                buffer += sock.recv(1000).decode()
                match = re.match(r'(.*)^(220|552|250|550)[^\r\n]*\r\n', buffer,
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
        for idx, stem in enumerate(sorted(words), start=1):
            message = "{} definitions found".format(count)
            print_progress(idx, len(words), message)
            words[stem]['definitions'] = []
            words[stem]['words'] = []
            for word in sorted(words[stem]['inflections']):
                cmd ='d {database} {word}\n'.format(
                    word=word, database=self.config['dictd_database'])
                sock.send(cmd.encode())
                code, response = read()
                if code == 552:
                    logger.debug("Definition not found %s", word)
                elif code == 250:
                    count += 1
                    definition = parse_definition(stem, word, response)
                    words[stem]['definitions'].append(definition)
                    words[stem]['words'].append(word)
                    continue
                elif code == 550:
                    raise Exception("Invalid dictd database")
        sock.close()
        logger.info(message)
        return words

    @memoized("/tmp/templates.pickle")
    def templates(self, entries):
        logger.info("Compiling dictionary templates")
        env = Environment(loader=FileSystemLoader('templates'))
        template_opf = env.get_template('dictionary.opf')
        template_html = env.get_template('dictionary.html')
        entries = sorted(entries.items(), key=lambda e: e[0])
        entries = map(lambda e: e[1], entries)
        entries = filter(lambda e: e['definitions'], entries)
        variables = {'entries': entries,
                     'date': datetime.now().strftime('%d/%m/%Y'),
                     'default_text': self.config['title']}
        variables.update(self.config)
        opf = template_opf.render(variables)
        html = template_html.render(variables)
        return opf, html

    def mobi(self, opf, html):
        logger.info("Generating mobi file")
        with open('/tmp/dictionary.opf', 'w') as opf_file:
            opf_file.write(opf)
        with open('/tmp/dictionary.html', 'w') as html_file:
            html_file.write(html)
        cmd = [self.config['kindlegen_path'],
               html_file.name,
               opf_file.name,
               '-verbose',
               '-o', 'dictionary.mobi']
        shutil.copyfile('templates/style.css', '/tmp/style.css')
        kindlegen = subprocess.call(cmd)
        os.rename('/tmp/dictionary.mobi', self.config['output'])
        logger.info("Created at {}".format(self.config['output']))

    def generate(self):
        self.mobi(
            *self.templates(
                self.definitions(
                    self.stems(
                        self.words()))))


if __name__ == '__main__':
    config = configuration(sys.argv[1:])
    logging.basicConfig(level=getattr(logging, config['logging_level']))
    logger.info("Loading generator class {}".format(config['generator_cls']))
    generator_cls = load_class(config['generator_cls'])
    generator = generator_cls(config)
    generator.generate()
