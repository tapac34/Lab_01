# TOKENISATION: разбивает выражение на токены, объединяет +-, опускает точку в конце чисел, ставит * между скобками
def tokenisation(expression: str) -> list:
    position = 0  # позиция которую мы считываем
    tokens = []
    expression = expression + " "

    while position < len(expression):  # продолжаем пока не пройдём по всему выражению
        start = position  # запоминаем старт для чисел и +-

        number = 0  # число ли токен
        unar = 0  # унарное значение ли токен
        sign = 0  # унарный знак

        for char in expression[start:]:  # идём по выражению добавляя токены

            # собираем идущие подряд + и - воедино
            if char in "+-" and number == 0:
                unar = 1
                if char in "-":
                    sign += 1
                position += 1
                continue
            elif unar == 1:
                if sign % 2 == 0:
                    tokens.append("+")
                else:
                    tokens.append("-")
                break

            # записываем числа с разделителями
            elif char.isdigit():
                number = 1
                position += 1
                continue
            elif char == ".":
                if number == 0:  # точка без числа записывается отдельно
                    tokens.append(char)
                else:
                    position += 1
                    continue
            elif number == 1:
                if expression[position - 1] == ".":  # если точка в конце, записываем без неё
                    tokens.append(expression[start : (position - 1)])
                else:
                    tokens.append(expression[start:position])
                break

            # записываем остальные символы
            elif char in "*/()":
                tokens.append(char)
            elif char.isspace() == 0:
                tokens.append("Недопустимый символ")
            position += 1
            break

    # расставляем * между скобками и числами
    i = 0
    while i < len(tokens) - 1:
        if tokens[i] in ")" and tokens[i + 1] in "(":
            tokens[(i + 1) : (i + 1)] = ["*"]
        if tokens[i][0].isdigit() and tokens[i + 1] in "(":
            tokens[(i + 1) : (i + 1)] = ["*"]
        if tokens[i] in ")" and tokens[i + 1][0].isdigit():
            tokens[(i + 1) : (i + 1)] = ["*"]
        i += 1
    return tokens


# VALIDATION: выводит ошибки (кроме деления на 0), ничего не меняет
def validation(tokens: list) -> list:
    in_brackets = 0  # в скобках ли мы
    numbers = 0  # количество чисел
    operations = 0  # количество операций

    if tokens == []:  # проверка на пустое выражение
        raise Exception("Пустое выражение")

    for i in range(len(tokens)):

        # обрабатываем лишние символы
        if tokens[i] == "Недопустимый символ":
            raise Exception("Недопустимый символ")
        elif tokens[i] in ".":
            raise Exception("Разделитель без числа")

        # проверяем положение скобок и их содержимое
        elif tokens[i] in "(":
            in_brackets += 1
        elif tokens[i] in ")":
            if in_brackets == 0:
                raise Exception("Неправильное положение скобок")
            else:
                in_brackets -= 1
            if tokens[i - 1] in "+-*/":
                raise Exception("Скобочное выражение заканчивается операцией")
            elif tokens[i - 1] in "(":
                raise Exception("Пустые скобки")

        # проверяем положение знаков операций
        elif tokens[i] in "+-*/":
            if i == len(tokens) - 1:
                raise Exception("Заканчивается операцией")
            elif tokens[i] in "+-*/" and tokens[i + 1] in "*/":
                raise Exception("Две операции подряд")
            operations += 1

        # проверяем разделители в числах и не идут ли числа подряд
        else:  # tokens[i] - число
            numbers += 1
            dots = 0
            for char in tokens[i]:
                if char == ".":
                    dots += 1
                if dots > 1:
                    raise Exception(f"Несколько разделителей в числе: {tokens[i]}")
            if i != len(tokens) - 1:
                if tokens[i][0].isdigit() and tokens[i + 1][0].isdigit():
                    raise Exception("Два числа подряд")

    # смотрим есть ли в выражении операции и числа, и закрыты ли все скобки
    if operations == 0:
        raise Exception("Нет операций")
    if numbers == 0:
        raise Exception("Нет чисел")
    if in_brackets > 0:
        raise Exception("Незакрывающиеся скобки")

    return tokens #убедившись, что ошибок нет, пропускаем токены дальше


# CALCULATION: вычисляет выражение, начиная со скобок, пока не получит ответ
def calculation(tokens: list) -> float:
    import math

    def calculate(expr: list) -> list:  # сюда входит выражение без скобок и выводится кго результат
        answer = []

        # разбиваем выражение на float и */ : -3+5*-2 -> [-3][5][*][-2]
        i = 0  # наша позиция
        while i < len(expr):
            if str(expr[i]) in "+":
                answer.append(float(expr[i + 1]))
                i += 2
            elif str(expr[i]) in "-":
                answer.append(-float(expr[i + 1]))
                i += 2
            elif str(expr[i]) in "*/":
                answer.append(expr[i])
                i += 1
            else:  # если число
                answer.append(float(expr[i]))
                i += 1

        # перемножаем числа, добавляем результат в answer, удаляем перемноженное
        i = 0  # наша позиция
        while "*" in answer or "/" in answer:
            if str(answer[i]) in "*":
                answer.insert(i - 1, answer[i - 1] * answer[i + 1])
                del answer[i : (i + 3)]
            elif str(answer[i]) in "/":
                if math.isclose(answer[i + 1], 0):  # проверка на 0
                    raise Exception("Деление на 0")
                answer.insert(i - 1, answer[i - 1] / answer[i + 1])
                del answer[i : (i + 3)]
            else:
                i += 1

        # складываем оставшееся
        while len(answer) > 1:
            answer[0] = answer[0] + answer[1]
            del answer[1]

        return answer[0]

    # будем считать результаты скобок пока они не кончатся
    pos = 0  # позиция
    while ")" in tokens:
        while tokens[pos] != ")":  # самая левая закрывающая скобка
            pos += 1
        end = pos  # конец выражения в скобках
        while tokens[pos] != "(":  # открывающая скобка соответсвующая нашей
            pos -= 1
        start = pos  # начало выражения в скобках

        # считаем выражение в скобках, удаляем его и вставляем на его место результат
        brackets = calculate(tokens[start + 1 : end])
        del tokens[start : end + 1]
        tokens.insert(pos, brackets)

    return calculate(tokens)  # когда скобок не осталось, выводим final answer)