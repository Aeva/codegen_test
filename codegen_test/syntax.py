
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
    indent: Tuple[str, ...] = tuple()

    def __init__(self, *args, **kwargs) -> None:
        if len(self.params) == 1 and len(args) > 0:
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
        param = self._dict[key]
        def resolve(param):
            if issubclass(type(param), SyntaxTemplate):
                return param.fill()
            else:
                assert(type(param) is str)
                return param
        if not type(param) is str:
            param = "\n".join(map(resolve, param))
        if key in self.indent:
            return indent(param)
        else:
            return param

    def __setitem__(self, key: str, value: str) -> str:
        if not key in self.params:
            raise KeyError(f"key \"{key}\" is not valid for {type(self).__name__}")
        self._dict[key] = value
        return value

    def __getattr__(self, name):
        if name in self.params:
            return self[name]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self.params:
            self[name] = value
        else:
            object.__setattr__(self, name, value)
        return value

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self._dict}>"

    def fill(self) -> str:
        resolved = {}
        for key in self.params:
            resolved[key] = self[key]
        return self.template.format(**resolved)

    def __str__(self) -> str:
        return self.fill()
