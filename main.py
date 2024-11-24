import re
import sys
import toml

# Словарь для хранения глобальных переменных (констант)
variables = {}

# Функция для получения значения переменной или числа
def get_value(operand):
    """
    Возвращает значение переменной или преобразует операнд в число или строку.
    """
    # Проверка на число
    try:
        return int(operand)
    except ValueError:
        pass

    # Проверка на строку
    if operand.startswith('"') and operand.endswith('"'):
        return operand[1:-1]  # Возвращаем строку без кавычек

    # Если это переменная, возвращаем ее значение
    if operand in variables:
        return variables[operand]

    raise SyntaxError(f"Неизвестный операнд: {operand}")

# Функция для вычисления выражений в формате ?{операция операнд1 операнд2}
def evaluate_expression(expression):
    """
    Вычисляет выражение вида @{операнд1 операция операнд2} или @{операция(аргументы)}.
    Примеры: @{имя + 1}, @{max(3, 5)}, @{print("Hello")}
    """

    # Находим позиции символов @{ и }
    start_idx = expression.find("@{")  # Находим начало выражения
    end_idx = expression.find("}", start_idx)  # Находим конец выражения

    if start_idx == -1 or end_idx == -1:
        raise SyntaxError(f"Неверный синтаксис выражения: {expression}")

    # Извлекаем содержимое между @{ и }
    content = expression[start_idx + 2:end_idx].strip()

    if not content:
        raise SyntaxError(f"Пустое выражение: {expression}")

    # Попробуем вычислить выражение как константу
    try:
        # Преобразуем строку в Python-выражение и пытаемся выполнить
        result = eval(content, {}, {"print": print, "max": max})
        return result
    except Exception as e:
        raise SyntaxError(f"Ошибка при вычислении выражения: {content}. Ошибка: {e}")

# Функция для обработки значений (массивы, строки и выражения)
def parse_value(value):
    """
    Обрабатывает значение: массивы, строки, выражения и словари.
    """
    value = value.strip()

    # Проверяем, является ли это выражением
    start_idx = value.find("@{")  # Ищем начало выражения
    if start_idx != -1 and value.find("}", start_idx) != -1:  # Если есть @
        return evaluate_expression(value)

    # Если это массив, обрабатываем его элементы, но не вычисляем
    if value.startswith('(') and value.endswith(')'):  # Если это массив
        elements = re.findall(r'"[^"]*"|\S+', value[1:-1])  # Разделяем элементы массива
        return elements  # Просто возвращаем элементы массива, не вычисляя их

    # Если это строка, обрабатываем как строку в формате "строка"
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]  # Извлекаем строку между кавычками

    # Если это словарь в формате [имя => значение, имя => значение, ...]
    if value.startswith('[') and value.endswith(']'):
        # Извлекаем пары ключ-значение
        dict_elements = re.findall(r'"([^"]+)"\s*=>\s*([^,]+)', value[1:-1])  # Пары ключ-значение
        result_dict = {}
        for key, val in dict_elements:
            result_dict[key] = parse_value(val.strip())  # Рекурсивно обрабатываем значение
        return result_dict

    # Для всего остального — проверяем как простое значение
    return get_value(value)

# Функция для обработки конфигурационного текста
def process_config(config_text):
    """
    Обрабатывает строки конфигурации.
    Преобразует объявления переменных в объявления констант в стиле (define имя значение).
    """
    for line in config_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue  # Пропускаем пустые строки

        # Обрабатываем объявление константы (define)
        if line.startswith("define "):
            parts = line[7:].split(" = ")
            if len(parts) != 2:
                raise SyntaxError(f"Неверный синтаксис объявления константы: {line}")
            name, value = parts
            variables[name.strip()] = parse_value(value.strip())  # Записываем в глобальные переменные

        # Обрабатываем присваивание значения переменной
        else:
            name, value = line.split(" = ", 1)
            name = name.strip()
            value = value.strip()
            variables[name] = parse_value(value)  # Записываем в глобальные переменные

# Основная функция
def main():
    # Проверка аргументов командной строки
    if len(sys.argv) < 3:
        print("Ошибка: не указаны пути к входному и выходному файлам")
        sys.exit(1)

    # Пути к файлам: входной и выходной
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Чтение конфигурации из файла
    with open(input_file, 'r', encoding='utf-8') as file:
        config_text = file.read()

    # Обрабатываем конфигурацию
    process_config(config_text)

    # Записываем результат в файл в формате TOML
    with open(output_file, 'w', encoding='utf-8') as file:
        toml.dump(variables, file)

    print(f"Результат записан в файл: {output_file}")

if __name__ == "__main__":
    main()
