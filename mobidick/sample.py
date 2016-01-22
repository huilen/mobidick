from mobidick import Generator


class SampleGenerator(Generator):

    def stems(self, words):
        stems = super(SampleGenerator, self).stems(words)
        return dict(list(stems.items())[0:10000])
