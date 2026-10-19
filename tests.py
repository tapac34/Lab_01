import unittest

from src.toolkit.calculator import tokenisation
from src.toolkit.calculator import validation
from src.toolkit.calculator import calculation
from src.toolkit.converter import converter

class TestTokenisation(unittest.TestCase):
    def test_simple_number(self):
        self.assertEqual(tokenisation("5"), ["5"])

    def test_decimal_number(self):
        self.assertEqual(tokenisation("3.14"), ["3.14"])

    def test_simple_operations(self):
        self.assertEqual(tokenisation("1+2"), ["1", "+", "2"])
        self.assertEqual(tokenisation("1-2"), ["1", "-", "2"])
        self.assertEqual(tokenisation("1*2"), ["1", "*", "2"])
        self.assertEqual(tokenisation("1/2"), ["1", "/", "2"])

    def test_brackets(self):
        self.assertEqual(tokenisation("(1+2)"), ["(", "1", "+", "2", ")"])

    def test_unary_minus(self):
        self.assertEqual(tokenisation("-5"), ["-", "5"])

    def test_unary_plus(self):
        self.assertEqual(tokenisation("+5"), ["+", "5"])

    def test_double_minus(self):
        # --5 -> +
        self.assertEqual(tokenisation("--5"), ["+", "5"])

    def test_triple_minus(self):
        # ---5 -> -
        self.assertEqual(tokenisation("---5"), ["-", "5"])

    def test_implicit_multiplication_brackets(self):
        # (2)(3) -> (2)*(3)
        self.assertEqual(tokenisation("(2)(3)"), ["(", "2", ")", "*", "(", "3", ")"])

    def test_implicit_multiplication_number_bracket(self):
        # 2(3) -> 2*(3)
        self.assertEqual(tokenisation("2(3)"), ["2", "*", "(", "3", ")"])

    def test_implicit_multiplication_bracket_number(self):
        # (2)3 -> (2)*3
        self.assertEqual(tokenisation("(2)3"), ["(", "2", ")", "*", "3"])

    def test_number_with_trailing_dot(self):
        # "5." -> "5" (точка в конце отбрасывается)
        self.assertEqual(tokenisation("5."), ["5"])

    def test_invalid_character(self):
        self.assertIn("Недопустимый символ", tokenisation("5a"))

    def test_empty_string(self):
        self.assertEqual(tokenisation(""), [])

    def test_spaces_ignored(self):
        self.assertEqual(tokenisation(" 1 + 2 "), ["1", "+", "2"])

    def test_unary_in_expression(self):
        self.assertEqual(tokenisation("3*-2"), ["3", "*", "-", "2"])

    def test_complex_expression(self):
        self.assertEqual(
            tokenisation("-(3+4)*2"),
            ["-", "(", "3", "+", "4", ")", "*", "2"]
        )


class TestValidation(unittest.TestCase):
    def test_valid_simple(self):
        tokens = tokenisation("1+2")
        # Не должно быть исключения
        validation(tokens)

    def test_valid_with_brackets(self):
        tokens = tokenisation("(1+2)*3")
        validation(tokens)

    def test_valid_decimal(self):
        tokens = tokenisation("3.14+2.5")
        validation(tokens)

    def test_valid_nested_brackets(self):
        tokens = tokenisation("((1+2)*3)")
        validation(tokens)

    def test_valid_unary_minus(self):
        tokens = tokenisation("-5+3")
        validation(tokens)

    # --- Ошибки ---

    def test_empty_expression(self):
        with self.assertRaises(Exception) as ctx:
            validation([])
        self.assertIn("Пустое выражение", str(ctx.exception))

    def test_invalid_character(self):
        tokens = tokenisation("5a")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Недопустимый символ", str(ctx.exception))

    def test_dot_without_number(self):
        tokens = tokenisation(".5")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Разделитель без числа", str(ctx.exception))

    def test_unbalanced_brackets_right(self):
        tokens = tokenisation("1+2)")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Неправильное положение скобок", str(ctx.exception))

    def test_unbalanced_brackets_left(self):
        tokens = tokenisation("(1+2")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Незакрывающиеся скобки", str(ctx.exception))

    def test_empty_brackets(self):
        tokens = tokenisation("()")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Пустые скобки", str(ctx.exception))

    def test_bracket_ends_with_operation(self):
        tokens = tokenisation("(1+)")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Скобочное выражение заканчивается операцией", str(ctx.exception))

    def test_ends_with_operation(self):
        tokens = tokenisation("1+")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Заканчивается операцией", str(ctx.exception))

    def test_two_operations_in_row(self):
        # 1+*2 - после tokenisation получится ["1", "+", "*", "2"]
        tokens = ["1", "+", "*", "2"]
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Две операции подряд", str(ctx.exception))

    def test_two_numbers_in_row(self):
        tokens = ["1", "2", "+", "3"]
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Два числа подряд", str(ctx.exception))

    def test_multiple_dots_in_number(self):
        tokens = ["1.2.3", "+", "1"]
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Несколько разделителей", str(ctx.exception))

    def test_no_operations(self):
        tokens = tokenisation("5")
        with self.assertRaises(Exception) as ctx:
            validation(tokens)
        self.assertIn("Нет операций", str(ctx.exception))

    def test_no_numbers(self):
        # Выражение только из операций и скобок
        tokens = ["(", ")", "+", "(", ")"]
        with self.assertRaises(Exception):
            validation(tokens)


class TestCalculation(unittest.TestCase):

    def test_simple_addition(self):
        self.assertEqual(calculation(tokenisation("1+2")), 3.0)

    def test_simple_subtraction(self):
        self.assertEqual(calculation(tokenisation("5-3")), 2.0)

    def test_simple_multiplication(self):
        self.assertEqual(calculation(tokenisation("4*3")), 12.0)

    def test_simple_division(self):
        self.assertEqual(calculation(tokenisation("10/2")), 5.0)

    def test_decimal_operations(self):
        self.assertAlmostEqual(calculation(tokenisation("1.5+2.5")), 4.0)
        self.assertAlmostEqual(calculation(tokenisation("0.1+0.2")), 0.3)

    def test_operator_precedence(self):
        # 2+3*4 = 14
        self.assertEqual(calculation(tokenisation("2+3*4")), 14.0)

    def test_operator_precedence_division(self):
        # 10-6/2 = 7
        self.assertEqual(calculation(tokenisation("10-6/2")), 7.0)

    def test_brackets(self):
        # (2+3)*4 = 20
        self.assertEqual(calculation(tokenisation("(2+3)*4")), 20.0)

    def test_nested_brackets(self):
        # ((2+3)*2)*2 = 20
        self.assertEqual(calculation(tokenisation("((2+3)*2)*2")), 20.0)

    def test_unary_minus(self):
        # -5+3 = -2
        self.assertEqual(calculation(tokenisation("-5+3")), -2.0)

    def test_unary_minus_in_multiplication(self):
        # 3*-2 = -6
        self.assertEqual(calculation(tokenisation("3*-2")), -6.0)

    def test_double_minus(self):
        # 5--3 = 8 (--3 -> +3)
        self.assertEqual(calculation(tokenisation("5--3")), 8.0)

    def test_division_by_zero(self):
        with self.assertRaises(Exception) as ctx:
            calculation(tokenisation("1/0"))
        self.assertIn("Деление на 0", str(ctx.exception))

    def test_division_by_zero_decimal(self):
        with self.assertRaises(Exception) as ctx:
            calculation(tokenisation("1/0.0"))
        self.assertIn("Деление на 0", str(ctx.exception))

    def test_division_by_zero_in_brackets(self):
        with self.assertRaises(Exception) as ctx:
            calculation(tokenisation("(1/0)+1"))
        self.assertIn("Деление на 0", str(ctx.exception))

    def test_complex_expression(self):
        # (1+2)*(3+4) = 21
        self.assertEqual(calculation(tokenisation("(1+2)*(3+4)")), 21.0)

    def test_implicit_multiplication(self):
        # 2(3+4) = 14
        self.assertEqual(calculation(tokenisation("2(3+4)")), 14.0)

    def test_negative_result(self):
        self.assertEqual(calculation(tokenisation("2-5")), -3.0)

    def test_zero_result(self):
        self.assertEqual(calculation(tokenisation("5-5")), 0.0)

    def test_multiplication_chain(self):
        # 2*3*4 = 24
        self.assertEqual(calculation(tokenisation("2*3*4")), 24.0)

    def test_division_chain(self):
        # 24/2/3 = 4
        self.assertEqual(calculation(tokenisation("24/2/3")), 4.0)

    def test_mixed_chain(self):
        # 2*3/2 = 3
        self.assertEqual(calculation(tokenisation("2*3/2")), 3.0)

    def test_leading_unary_plus(self):
        self.assertEqual(calculation(tokenisation("+5+3")), 8.0)

    def test_multiple_brackets(self):
        # (1+1)+(2+2) = 6
        self.assertEqual(calculation(tokenisation("(1+1)+(2+2)")), 6.0)


class TestIntegration(unittest.TestCase):

    def _evaluate(self, expression):
        tokens = tokenisation(expression)
        validation(tokens)
        return calculation(tokens)

    def test_full_pipeline_simple(self):
        self.assertEqual(self._evaluate("1+2"), 3.0)

    def test_full_pipeline_complex(self):
        self.assertAlmostEqual(
            self._evaluate("(1+2)*(3.5-1.5)/2"),
            3.0
        )

    def test_full_pipeline_with_negatives(self):
        self.assertEqual(self._evaluate("-(2+3)*4"), -20.0)

    def test_full_pipeline_nested(self):
        self.assertEqual(self._evaluate("((1+2)*(3+4))-5"), 16.0)

    def test_full_pipeline_invalid_char(self):
        with self.assertRaises(Exception):
            self._evaluate("1+x")

    def test_full_pipeline_unbalanced(self):
        with self.assertRaises(Exception):
            self._evaluate("(1+2")

    def test_full_pipeline_division_by_zero(self):
        with self.assertRaises(Exception):
            self._evaluate("1/(2-2)")








class TestConverterLength(unittest.TestCase):

    def test_mm_to_cm(self):
        self.assertAlmostEqual(converter(10, "mm", "cm"), 1.0)

    def test_mm_to_m(self):
        self.assertAlmostEqual(converter(1000, "mm", "m"), 1.0)

    def test_mm_to_km(self):
        self.assertAlmostEqual(converter(1_000_000, "mm", "km"), 1.0)

    def test_cm_to_mm(self):
        self.assertAlmostEqual(converter(1, "cm", "mm"), 10.0)

    def test_cm_to_m(self):
        self.assertAlmostEqual(converter(100, "cm", "m"), 1.0)

    def test_cm_to_km(self):
        self.assertAlmostEqual(converter(100_000, "cm", "km"), 1.0)

    def test_m_to_mm(self):
        self.assertAlmostEqual(converter(1, "m", "mm"), 1000.0)

    def test_m_to_cm(self):
        self.assertAlmostEqual(converter(1, "m", "cm"), 100.0)

    def test_m_to_km(self):
        self.assertAlmostEqual(converter(1000, "m", "km"), 1.0)

    def test_km_to_m(self):
        self.assertAlmostEqual(converter(1, "km", "m"), 1000.0)

    def test_km_to_cm(self):
        self.assertAlmostEqual(converter(1, "km", "cm"), 100_000.0)

    def test_km_to_mm(self):
        self.assertAlmostEqual(converter(1, "km", "mm"), 1_000_000.0)

    def test_length_decimal(self):
        self.assertAlmostEqual(converter(1.5, "m", "cm"), 150.0)

    def test_length_zero(self):
        self.assertAlmostEqual(converter(0, "m", "cm"), 0.0)

    def test_length_negative(self):
        # Отрицательные длины не запрещены кодом
        self.assertAlmostEqual(converter(-1, "m", "cm"), -100.0)


class TestConverterMass(unittest.TestCase):

    def test_g_to_kg(self):
        self.assertAlmostEqual(converter(1000, "g", "kg"), 1.0)

    def test_kg_to_g(self):
        self.assertAlmostEqual(converter(1, "kg", "g"), 1000.0)

    def test_g_to_kg_decimal(self):
        self.assertAlmostEqual(converter(500, "g", "kg"), 0.5)

    def test_kg_to_g_decimal(self):
        self.assertAlmostEqual(converter(0.5, "kg", "g"), 500.0)

    def test_mass_zero(self):
        self.assertAlmostEqual(converter(0, "kg", "g"), 0.0)

    def test_mass_negative(self):
        self.assertAlmostEqual(converter(-1, "kg", "g"), -1000.0)


class TestConverterTemperature(unittest.TestCase):

    def test_c_to_k(self):
        self.assertAlmostEqual(converter(0, "c", "k"), 273.15)

    def test_c_to_f(self):
        self.assertAlmostEqual(converter(0, "c", "f"), 32.0)
        self.assertAlmostEqual(converter(100, "c", "f"), 212.0)
        self.assertAlmostEqual(converter(-40, "c", "f"), -40.0)

    def test_k_to_c(self):
        self.assertAlmostEqual(converter(273.15, "k", "c"), 0.0)

    def test_k_to_f(self):
        self.assertAlmostEqual(converter(273.15, "k", "f"), 32.0)

    def test_f_to_c(self):
        self.assertAlmostEqual(converter(32, "f", "c"), 0.0)
        self.assertAlmostEqual(converter(212, "f", "c"), 100.0)

    def test_f_to_k(self):
        self.assertAlmostEqual(converter(32, "f", "k"), 273.15)

    def test_absolute_zero_c(self):
        # ровно -273.15 °C = 0 K — допустимо (не ниже нуля)
        self.assertAlmostEqual(converter(-273.15, "c", "k"), 0.0)

    def test_absolute_zero_f(self):
        # -459.67 °F = 0 K
        self.assertAlmostEqual(converter(-459.67, "f", "k"), 0.0, places=5)

    def test_below_absolute_zero_c(self):
        with self.assertRaises(Exception) as ctx:
            converter(-300, "c", "k")
        self.assertIn("ниже абсолютного 0", str(ctx.exception))

    def test_below_absolute_zero_f(self):
        with self.assertRaises(Exception) as ctx:
            converter(-500, "f", "k")
        self.assertIn("ниже абсолютного 0", str(ctx.exception))

    def test_below_absolute_zero_k(self):
        with self.assertRaises(Exception) as ctx:
            converter(-1, "k", "c")
        self.assertIn("ниже абсолютного 0", str(ctx.exception))

    def test_temperature_decimal(self):
        self.assertAlmostEqual(converter(36.6, "c", "k"), 309.75)


class TestConverterValueInput(unittest.TestCase):

    def test_value_as_string(self):
        # float("5") работает — должно приниматься
        self.assertAlmostEqual(converter("5", "m", "cm"), 500.0)

    def test_value_as_string_decimal(self):
        self.assertAlmostEqual(converter("1.5", "m", "cm"), 150.0)

    def test_value_as_int(self):
        self.assertAlmostEqual(converter(5, "m", "cm"), 500.0)

    def test_value_not_a_number(self):
        with self.assertRaises(Exception) as ctx:
            converter("abc", "m", "cm")
        self.assertIn("не число", str(ctx.exception))

    def test_value_empty_string(self):
        with self.assertRaises(Exception) as ctx:
            converter("", "m", "cm")
        self.assertIn("не число", str(ctx.exception))


class TestConverterErrors(unittest.TestCase):

    def test_unknown_from_unit(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "xyz", "m")
        self.assertIn("Неизвестная единица измерения входных данных", str(ctx.exception))

    def test_unknown_to_unit(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "m", "xyz")
        self.assertIn("Неизвестная единица измерения данных выхода", str(ctx.exception))

    def test_uppercase_unit_rejected(self):
        # Код сравнивает строки без .lower() — "M" не равно "m"
        with self.assertRaises(Exception) as ctx:
            converter(5, "M", "cm")
        self.assertIn("Неизвестная единица", str(ctx.exception))

    def test_incompatible_length_to_mass(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "m", "kg")
        self.assertIn("Несовместимые единицы", str(ctx.exception))

    def test_incompatible_mass_to_length(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "kg", "m")
        self.assertIn("Несовместимые единицы", str(ctx.exception))

    def test_incompatible_length_to_temperature(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "m", "c")
        self.assertIn("Несовместимые единицы", str(ctx.exception))

    def test_incompatible_temperature_to_mass(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "c", "kg")
        self.assertIn("Несовместимые единицы", str(ctx.exception))

    def test_same_unit_length(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "m", "m")
        self.assertIn("Одинаковые единицы", str(ctx.exception))

    def test_same_unit_mass(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "kg", "kg")
        self.assertIn("Одинаковые единицы", str(ctx.exception))

    def test_same_unit_temperature(self):
        with self.assertRaises(Exception) as ctx:
            converter(5, "c", "c")
        self.assertIn("Одинаковые единицы", str(ctx.exception))

if __name__ == "__main__":
    unittest.main(verbosity=2)