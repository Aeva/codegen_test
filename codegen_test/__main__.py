
import sys
assert(sys.version_info.major >= 3)
assert(sys.version_info.minor >= 6)
import subprocess
from typing import Iterable
from syntax import SyntaxTemplate, indent


class SystemInclude(SyntaxTemplate):
    template = "#include <「include」>"


class TalkerFn(SyntaxTemplate):
    template = \
"""
inline void 「name」()
{
    std::cout << "「message」";
}
""".strip()


class TalkerCall(SyntaxTemplate):
    template = "「name」();"


TALKERS = {}
def get_talker(message: str) -> TalkerFn:
    global TALKERS
    count = len(TALKERS.keys())
    if message in TALKERS:
        return TALKERS[message]
    else:
        name = f"Talker{count}"
        TALKERS[message] = TalkerFn(name=name, message=message)
        return TALKERS[message]


class Talker:
    def __init__(self, message):
        self.definition = get_talker(" " + message)
        self.call = TalkerCall(self.definition["name"])


class ProgramMain(SyntaxTemplate):
    template = \
"""
「includes」
「definitions」
int main()
{
「body」
\treturn 0;
}
"""


def fill_and_join(iterable: Iterable[SyntaxTemplate]) -> str:
    return "\n".join([i.fill() for i in iterable])
        

if __name__ == "__main__":
    includes = [SystemInclude("iostream")]

    words = "This is probably not the worst way to print something, but I think it is up there.\\n".split(" ")

    talkers = [Talker(word) for word in words]
    definitions = TALKERS.values()
    body = [talker.call for talker in talkers]

    main = ProgramMain(
        includes = fill_and_join(includes),
        definitions = fill_and_join(definitions),
        body = indent(fill_and_join(body)))

    with open("generated.cpp", "w") as outfile:
        outfile.write(main.fill())
    subprocess.run(["g++", "generated.cpp"], check=True)
    subprocess.run(["./a.out"])