import sys
from .calculator import tokenisation, validation, calculation
from .converter import converter

cmd = sys.argv[1]
arguments = sys.argv[2:]

try:
    if cmd == "calc":
        tokens = tokenisation(arguments[0])
        validation(tokens)
        print(calculation(tokens))
    elif cmd == "convert":
        value = arguments[0]
        from_unit = arguments[arguments.index("--from") + 1]
        to_unit = arguments[arguments.index("--to") + 1]
        print(converter(value, from_unit, to_unit))
    else:
        sys.exit(f"Неизвестная команда: {cmd}")
except Exception as error:
    print(f"Ошибка: {error}", file=sys.stderr)
    sys.exit(2)