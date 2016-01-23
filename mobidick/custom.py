import logging

from mobidick.generator import Generator


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
