
import sys
assert(sys.version_info.major >= 3)
assert(sys.version_info.minor >= 6)
import subprocess
from typing import Iterable, Dict
from syntax import SyntaxTemplate


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


TALKERS: Dict[str, TalkerFn] = {}
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
    indent = ("body",)
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
        

if __name__ == "__main__":
    main = ProgramMain()
    main.includes = [SystemInclude("iostream")]

    words = "This is probably not the worst way to print something, but I think it is up there.\\n".split(" ")

    talkers = [Talker(word) for word in words]
    main.definitions = TALKERS.values()
    main.body = [talker.call for talker in talkers]

    with open("generated.cpp", "w") as outfile:
        outfile.write(str(main))
    subprocess.run(["g++", "generated.cpp"], check=True)
    subprocess.run(["./a.out"])
