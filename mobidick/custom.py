import sys
import os
import logging

from mobidick.generator import Generator
from mobidick.utils import memoized, configuration


logger = logging.getLogger(__name__)


class SampleGenerator(Generator):

    def stems(self, words):
        stems = super(SampleGenerator, self).stems(words)
        size = self.config['sample_size']
        logger.info("Filter first {} stems".format(size))
        return dict(list(stems.items())[0:size])


class DictFallbackGenerator(SampleGenerator):

    def definitions(self, words):
        words = super(DictFallbackGenerator, self).definitions(words)
        self.config['dictd_hostname'] = self.config['fallback_dictd_hostname']
        self.config['dictd_database'] = self.config['fallback_dictd_database']
        not_found = {s: w for s, w in words.items() if not w['definitions']}
        import pdb; pdb.set_trace()
        words.update(super(DictFallbackGenerator, self).definitions(not_found))
        return words


class MemoizedGenerator(Generator):

    def __init__(self, config):
        super(MemoizedGenerator, self).__init__(config)
        for idx, arg in enumerate(sys.argv):
            if arg in ['-f', '--forget']:
                value = None
                try:
                    value = sys.argv[idx + 1]
                except IndexError:
                    pass
                values = ['templates', 'definitions', 'stems']
                if value in values:
                    values = [value]
                for value in values:
                    os.remove('/tmp/{}.pickle'.format(value))
                
    @memoized('/tmp/stems.pickle')
    def stems(self, words):
        return super(MemoizedGenerator, self).stems(words)

    @memoized('/tmp/definitions.pickle')
    def definitions(self, words):
        return super(MemoizedGenerator, self).definitions(words)

    @memoized('/tmp/templates.pickle')
    def templates(self, entries):
        return super(MemoizedGenerator, self).templates(entries)
