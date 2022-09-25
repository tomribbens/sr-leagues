from .base import FormatGenerator


class Vanilla(FormatGenerator):
    @staticmethod
    def get_format(*args, **kwargs):
        return "V"
