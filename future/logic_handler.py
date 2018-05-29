
"""
This library is a modified version of json_logic package 0.6.3 which itself is Python implementation
of the following jsonLogic JS library:
https://github.com/jwadhams/json-logic-js

Originall Author: nadir.izr
Home Page: https://github.com/nadirizr/json-logic-py
Keywords: json-logic
License: MIT
"""


import sys
from functools import reduce


def logic(tests, data=None):
    # You've recursed to a primitive, stop!
    if tests is None or type(tests) != dict:
        return tests

    data = data or {}

    op = list(tests.keys())[0]
    values = tests[op]
    operations = {
        "==": (lambda a, b: a == b),
        "===": (lambda a, b: a is b),
        "!=": (lambda a, b: a != b),
        "!==": (lambda a, b: a is not b),
        ">": (lambda a, b: a > b),
        ">=": (lambda a, b: a >= b),
        "<": (lambda a, b, c=None: a < b if (c is None) else (a < b) and (b < c)),
        "<=": (lambda a, b, c=None: a <= b if (c is None) else (a <= b) and (b <= c)),
        "!": (lambda a: not a),
        "%": (lambda a, b: a % b),
        "and": (lambda *args: reduce(lambda total, arg: total and arg, args, True)),
        "or": (lambda *args: reduce(lambda total, arg: total or arg, args, False)),
        "?:": (lambda a, b, c: b if a else c),
        "log": (lambda a: a if sys.stdout.write(str(a)) else a),
        "in": (lambda a, b: a in b if "__contains__" in dir(b) else False),
        "var": (lambda a, not_found=None:
                reduce(lambda data, key: (data.get(key, not_found) if type(data) == dict
                       else data[int(key)]
                           if (type(data) in [list, tuple] and
                               str(key).lstrip("-").isdigit())
                           else not_found),
                       str(a).split("."), data)),
        "cat": (lambda *args: "".join(args)),
        "+": (lambda *args: reduce(lambda total, arg: total + float(arg), args, 0.0)),
        "*": (lambda *args: reduce(lambda total, arg: total * float(arg), args, 1.0)),
        "-": (lambda a, b=None: -a if b is None else a - b),
        "/": (lambda a, b=None: a if b is None else float(a) / float(b)),
        "min": (lambda *args: min(args)),
        "max": (lambda *args: max(args)),
        "count": (lambda *args: sum(1 if a else 0 for a in args)),
        }

    if op not in operations:
        raise RuntimeError("Unrecognized operation %s" % op)

    # Easy syntax for unary operators, like {"var": "x"} instead of strict
    # {"var": ["x"]}
    if type(values) not in [list, tuple]:
        values = [values]

    # Recursion!
    values = map(lambda val: logic(val, data), values)

    return operations[op](*values)


logic_value1 = \
    {
        "and": [
            {"=": [2, 2]},
            {"and": [
                {">": [3, 1]},
                {"<": [1, 3]}]}
            ]
    }

logic_value2 = {"and": [
    {">": [3, 1]},
    {"<": [1, 3]}
  ]}

print(logic(logic_value1))

