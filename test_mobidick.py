import sys
import logging
import unittest
import mobidick

from lxml import html


logger = logging.getLogger('mobidick.test')


class TestMobidick(unittest.TestCase):

    def test_words(self):
        words = self._words()
        logger.info("Checking test words")
        for word, inflections in config['test_words'].items():
            logger.info("Checking word '%s'", word)
            word = [w for w in words.values() if word in w['inflections']][0]
            logger.info("Checking that word exists")
            self.assertTrue(word)
            logger.info("Checking inflections")
            intersection = set(inflections).intersection(word['inflections'])
            self.assertEqual(intersection, set(inflections))
            logger.info("Checking definition")
            self.assertTrue(word['definitions'])

    def test_template(self):
        words = self._words()
        opf_doc, html_doc = mobidick.templates(words, config)
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
                                  for g in words.values()])
        self.assertEqual(inflection_groups, expected_groups)

    def _words(self):
        lang = config['language']
        words = mobidick.words(lang)
        words = mobidick.stems(words, lang=lang)
        words = {k: v for k, v in words.items()
                 if set(v['inflections']).intersection(config['test_words'])}
        words = mobidick.definitions(words, lang=lang)
        return words


if __name__ == '__main__':
    config = mobidick.configuration(sys.argv[1:])
    sys.argv = sys.argv[2:]
    unittest.main()
