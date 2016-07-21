from auto.parsers.ria import Parser as RiaParser


def get_parsers(*args, **kwargs):
    return map(lambda Parser: Parser(*args, **kwargs), [
        RiaParser,
    ])
