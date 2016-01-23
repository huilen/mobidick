import sys
import logging
import unittest

from mobidick.generator import Generator

from mobidick.utils import configuration

from lxml import html


logger = logging.getLogger('mobidick.test')


class TestMobidick(unittest.TestCase):

    def test_words(self):
        entries = self._entries()
        logger.info("Checking test words")
        for word, inflections in config['test_words'].items():
            logger.info("Checking word '%s'", word)
            word = [w for w in entries.values() if word in w['inflections']][0]
            logger.info("Checking that word exists")
            self.assertTrue(word)
            logger.info("Checking inflections")
            intersection = set(inflections).intersection(word['inflections'])
            self.assertEqual(intersection, set(inflections))
            logger.info("Checking definition")
            self.assertTrue(word['definitions'])

    def test_template(self):
        entries = self._entries()
        opf_doc, html_doc = self._templates(entries)
        html_doc = html_doc.replace('idx:entry', 'idxentry')
        html_doc = html_doc.replace('idx:infl', 'idxinfl')
        html_doc = html_doc.replace('idx:iform', 'idxiform')
        html_doc = html_doc.replace('idx:orth', 'idxorth')

        logger.info("Checking <idx:entry>")        
        dom = html.fromstring(html_doc)
        idxentries = dom.xpath('//idxentry')
        self.assertEqual(len(idxentries), len(config['test_words']))

        logger.info("Checking <idx:iform>")
        inflection_groups = []
        for idxentry in idxentries:
            idxiforms = idxentry.xpath('idxorth/idxinfl//idxiform')
            inflections = []
            inflections.extend([f.values()[0] for f in idxiforms])
            inflection_groups.append(inflections)
        inflection_groups = sorted([sorted(g) for g in inflection_groups])
        expected_groups = sorted([sorted(g['inflections'])
                                  for g in entries.values()])
        self.assertEqual(inflection_groups, expected_groups)

    def _entries(self):
        generator = Generator(config)
        entries = generator.words()
        entries = generator.stems(entries)
        entries = {k: v for k, v in entries.items()
                 if set(v['inflections']).intersection(config['test_words'])}
        entries = generator.definitions(entries)
        return entries

    def _templates(self, entries):
        generator = Generator(config)
        return generator.templates(entries)


if __name__ == '__main__':
    config = configuration(sys.argv[1:])
    logging.basicConfig(level=getattr(logging, config['logging_level']))
    sys.argv = sys.argv[2:]
    unittest.main()
