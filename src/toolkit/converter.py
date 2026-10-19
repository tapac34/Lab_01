def converter(value: float, from_unit: str, to_unit: str) -> float:

    try:  # проверяем float ли наше значение
        value = float(value)
    except ValueError:
        raise Exception("Значение - не число")
    from_unit = str(from_unit)
    to_unit = str(to_unit)

    unit1 = ""  # тип данных входа
    unit2 = ""  # тип данных выхода

    # проверяем работаем ли мы с длиной и переводим в метры если да
    if from_unit == "mm":
        value /= 1000
        unit1 = "lenght"
    elif from_unit == "cm":
        value /= 100
        unit1 = "lenght"
    elif from_unit == "m":
        unit1 = "lenght"
    elif from_unit == "km":
        value *= 1000
        unit1 = "lenght"

    # проверяем работаем ли мы с массой и переводим в килограммы если да
    elif from_unit == "g":
        value /= 1000
        unit1 = "mass"
    elif from_unit == "kg":
        unit1 = "mass"

    # проверяем работаем ли мы с температурой и переводим в кельвины если да
    elif from_unit == "c":
        value += 273.15
        unit1 = "temperature"
    elif from_unit == "f":
        value = (value - 32) / 1.8 + 273.15
        unit1 = "temperature"
    elif from_unit == "k":
        unit1 = "temperature"

    else:  # если поддерживаемые единицы не подошли, то выводим ошибку
        raise Exception("Неизвестная единица измерения входных данных")

    # если температура, то проверяем не ниже ли абсолютного 0
    if unit1 == "temperature":
        if value < 0:
            raise Exception("Температура ниже абсолютного 0")

    # переводим в нужные нам единицы
    if to_unit == "mm":
        value *= 1000
        unit2 = "lenght"
    elif to_unit == "cm":
        value *= 100
        unit2 = "lenght"
    elif to_unit == "m":
        unit2 = "lenght"
    elif to_unit == "km":
        value /= 1000
        unit2 = "lenght"

    elif to_unit == "g":
        value *= 1000
        unit2 = "mass"
    elif to_unit == "kg":
        unit2 = "mass"

    elif to_unit == "c":
        unit2 = "temperature"
        value -= 273.15
    elif to_unit == "f":
        value = (value - 273.15) * 1.8 + 32
        unit2 = "temperature"
    elif to_unit == "k":
        unit2 = "temperature"

    else:  # выводим ошибку, если единицы не поддерживаются
        raise Exception("Неизвестная единица измерения данных выхода")

    if unit1 != unit2:  # проверяем не одинаковый ли тип данных
        raise Exception("Несовместимые единицы измерения")
    if from_unit == to_unit:  # проверяем не одинаковые ли единицы измерения
        raise Exception("Одинаковые единицы измерения")

    return value  # если всё ок - выводим
