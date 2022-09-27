from .base import FormatGenerator


class Colony(FormatGenerator):
    def get_format(*args, **kwargs):
        return "W"
