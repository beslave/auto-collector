from auto.parsers.ria import RiaNewParser, RiaUsedParser


def get_parsers(*args, **kwargs):
    return map(lambda Parser: Parser(*args, **kwargs), [
        RiaNewParser,
        RiaUsedParser,
    ])
