
import re
from typing import Iterable, Tuple


def rewrite(template: str) -> str:
    """
    Alternate template syntax for string.format.  This uses 「angle quotes」 instead of
    {squiggly braces} for substitutions, so that {squiggly braces} do not need to be
    escaped.
    """
    return template.replace("{", "{{").replace("}", "}}").replace("「", "{").replace("」", "}")


def indent(text: str) -> str:
    """
    Indent each line in a string.
    """
    lines = text.replace("\r", "").split("\n")
    new_lines = []
    for line in lines:
        if len(line.strip()) == 0:
            new_lines.append("")
        else:
            new_lines.append("\t" + line)
    return "\n".join(new_lines)


class SyntaxTemplateMeta(type):
    def __new__(cls, name, bases, dct):
        newclass = super().__new__(cls, name, bases, dct)
        if newclass.template:
            newclass.params = tuple(sorted(set(re.findall(r"「([a-zA-Z]\w+)」", newclass.template))))
            newclass.template = rewrite(newclass.template)
        return newclass


class SyntaxTemplate(metaclass=SyntaxTemplateMeta):
    template = ""
    params: Tuple[str, ...] = tuple()

    def __init__(self, *args, **kwargs) -> None:
        if len(self.params) == 1:
            assert(len(args) != len(kwargs.keys()))
            if len(args) == 1:
                kwargs[self.params[0]] = args[0]
        elif len(self.params) > 1 and len(args) > 0:
            raise NameError(f"{type(self)} has more than one parameter, so init values have to be passed in as keyword arguments")
        self._dict = dict(zip(self.params, ["" for p in self.params]))
        for key, value in kwargs.items():
            self[key] = value

    def __getitem__(self, key: str) -> str:
        if not key in self.params:
            raise KeyError(f"key \"{key}\" is not valid for {type(self)}")
        return self._dict[key]

    def __setitem__(self, key: str, value: str) -> str:
        if not key in self.params:
            raise KeyError(f"key \"{key}\" is not valid for {type(self)}")
        self._dict[key] = value
        return value

    def fill(self) -> str:
        return self.template.format(**self._dict)
