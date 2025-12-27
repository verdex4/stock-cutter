import pulp as lp
from collections import namedtuple
from itertools import combinations

class Solver:
    def __init__(self, user_input):
        (self._stock_lengths, self._stock_quantities, 
        self._demand_length, self._demand_quantity) = self._parse_input(user_input)
        print("after parse")
        print(f"stock lengths: {self._stock_lengths}")
        print(f"stock quantities: {self._stock_quantities}")
        print(f"demand length: {self._demand_length}")
        print(f"demand quantity: {self._demand_quantity}")
    
    def solve(self):
        message = self._validate_data()
        if message != "OK":
            return message
        self._patterns = self._make_cutting_patterns()
        print(f"cutting patterns: {self._patterns}")
        min_waste = self._find_min_waste()
        if min_waste == -1:
            return "Раскрой невозможен, недостаточно заготовок на складе"
        result = self._find_uniform_solution(min_waste)
        return result

        

    def _parse_input(self, user_input):
        """Преобразует входные данные"""
        stock_lengths, stock_quantities, demand_length, demand_quantity = [], [], 0, 0
        for key, value in user_input.items():
            if key.startswith("len"):
                stock_lengths.append(float(value))
            elif key.startswith("qty"):
                stock_quantities.append(int(value))
            elif key.startswith("demand_len"):
                demand_length = float(value)
            elif key.startswith("demand_qty"):
                demand_quantity = int(value)
        return stock_lengths, stock_quantities, demand_length, demand_quantity
    
    def _validate_data(self):
        """Проверяет на наличие отрицательных чисел и убирает нули"""
        message = "OK"
        new_stock_lengths = []
        new_stock_quantities = []
        for l, qty in zip(self._stock_lengths, self._stock_quantities):
            if l < 0 or qty < 0:
                message = "Не должно быть отрицательных чисел"
                return message
            # нули принимаются как за несуществующую заготовку
            elif qty > 0:
                new_stock_lengths.append(l)
                new_stock_quantities.append(qty)
        
        if len(new_stock_lengths) == 0:
            message = "На складе пусто. Введите хотя бы одно количество, большее нуля"
            return message
        
        self._stock_lengths = new_stock_lengths
        self._stock_quantities = new_stock_quantities
            
        if self._demand_length < 0 or self._demand_quantity < 0:
            message = "Не должно быть отрицательных чисел"
            return message
        if self._demand_length == 0 or self._demand_quantity == 0:
            message = "Заказ пуст. Введите количество больше нуля"
            return message
        return message
    
    def _make_cutting_patterns(self):
        Pattern = namedtuple("Pattern", ['pieces_count', 'waste'])
        all_patterns = []
        for i in range(len(self._stock_lengths)):
            item_patterns = []
            pieces_count = 1
            waste = self._stock_lengths[i] - self._demand_length
            while waste >= 0:
                item_patterns.append(Pattern(pieces_count, waste))
                pieces_count += 1
                waste -= self._demand_length
            all_patterns.append(item_patterns)
        return all_patterns

    def _find_min_waste(self):
        """
        Решает задачу линейного целочисленного программирования 
        и возвращает минимально возможный остаток при раскрое.

        Задача: минимизировать функцию остатков.

        Целевая функция: сумма полученных остатков.

        Используемые переменные:
            1. self._patterns - варианты раскроя для каждой заготовки, 
            где элемент self._patterns[i][j] - одна комбинация, кортеж вида 
            (количество_полученных_отрезков, остаток).
            Размерность 2.
            Количество строк - количество заготовок.
            Количество столбцов - не фиксировано, зависит от заготовки.
            2. x - таблица с целыми числами, 
            где x[i][j] - количество комбинации self._patterns[i][j] в решении
            Размер совпадает с self._patterns
            3. item - заготовка на складе
            4. piece - полученная заготовка в результате разреза
            5. waste - отходы

        Ограничения:
            1. Количество комбинаций x[i][j] >= 0, целое.
            2. Мы не можем использовать больше заготовок, чем на складе.
            3. Полученное количество отрезков должно быть равно заказанному количеству.
        """
        problem = lp.LpProblem("Waste_minimization", lp.LpMinimize)

        x = [[] for i in range(len(self._patterns))]
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                x[i].append(lp.LpVariable(
                    name=f"x{i}{j}",
                    lowBound=0,
                    upBound=self._stock_quantities[i],
                    cat=lp.LpInteger)) # ПЕРВОЕ ОГРАНИЧЕНИЕ

        # ЦЕЛЕВАЯ ФУНКЦИЯ
        total_waste = 0
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                total_waste += self._patterns[i][j].waste * x[i][j]

        problem += total_waste

        # ВТОРОЕ ОГРАНИЧЕНИЕ
        for i in range(len(x)):
            used_items = lp.lpSum(x[i])
            problem += used_items <= self._stock_quantities[i]

        # ТРЕТЬЕ ОГРАНИЧЕНИЕ
        total_pieces = 0
        for i in range(len(x)):
            for j in range(len(x[i])):
                total_pieces += self._patterns[i][j].pieces_count * x[i][j]
        problem += total_pieces == self._demand_quantity

        # РЕШЕНИЕ
        status = problem.solve()

        # ПОЛУЧЕНИЕ РЕЗУЛЬТАТОВ
        min_waste = lp.value(problem.objective)
        if status == lp.LpStatusOptimal:
            print(f"Problem is solved!")
            print(f"Minimal waste: {min_waste}")
            for i in range(len(x)):
                for j in range(len(x[i])):
                    print(f"x{i}{j} = {lp.value(x[i][j])}")
            return min_waste
        elif lp.LpStatus[problem.status] == "Infeasible":
            print(f"No solution found!")
            return -1

    def _find_uniform_solution(self, min_waste):
        """
        Решает задачу линейного программирования 
        и возвращает самое равномерное решение с минимальными остатками.
        Решает ту же задачу, но с условием остатка, равному минимальному (min_waste).

        Задача: минимизировать функцию разброса.
        
        Целевая функция: средняя дистанция между всеми элементами
        
        Используемые переменные:
            1. self._patterns - варианты раскроя для каждой заготовки, 
            где элемент self._patterns[i][j] - одна комбинация, кортеж вида 
            (количество_полученных_отрезков, остаток).
            Размерность 2.
            Количество строк - количество заготовок.
            Количество столбцов - не фиксировано, зависит от заготовки.
            2. x - таблица с целыми числами, 
            где x[i][j] - количество комбинации self._patterns[i][j] в решении
            Размер совпадает с self._patterns
            3. item - заготовка на складе
            4. piece - полученная заготовка в результате разреза
            5. waste - отходы
            6. distances - список дистанций между всеми возможными парами заготовок.
        
        Ограничения:
            1. Количество комбинаций x[i][j] >= 0, целое.
            2. Мы не можем использовать больше заготовок, чем на складе.
            3. Полученное количество отрезков должно быть равно заказанному количеству.
            4. Полученный остаток должен быть равен минимальному.
        """
        problem = lp.LpProblem("Uniform_solution", lp.LpMinimize)

        x = [[] for i in range(len(self._patterns))]
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                x[i].append(lp.LpVariable(
                    name=f"x{i}{j}",
                    lowBound=0,
                    upBound=self._stock_quantities[i],
                    cat=lp.LpInteger)) # ПЕРВОЕ ОГРАНИЧЕНИЕ

        # ВТОРОЕ ОГРАНИЧЕНИЕ
        for i in range(len(x)):
            used_items = lp.lpSum(x[i])
            problem += used_items <= self._stock_quantities[i]

        # ТРЕТЬЕ ОГРАНИЧЕНИЕ
        total_pieces = 0
        for i in range(len(x)):
            for j in range(len(x[i])):
                total_pieces += self._patterns[i][j].pieces_count * x[i][j]
        problem += total_pieces == self._demand_quantity

        # ЧЕТВЕРТОЕ ОГРАНИЧЕНИЕ
        total_waste = 0
        for i in range(len(self._patterns)):
            row_sum = 0
            for j in range(len(self._patterns[i])):
                total_waste += self._patterns[i][j].waste * x[i][j]
        problem += total_waste == min_waste

        # ЦЕЛЕВАЯ ФУНКЦИЯ
        used_items = [lp.lpSum(x[i]) for i in range(len(x))]
        # Находим все возможные пары использованных заготовок (в индексах)
        pairs = combinations(range(len(used_items)), 2)
        distances = []
        for i, j in pairs:
            d = lp.LpVariable(f"d{i}{j}")
            distances.append(d)
            # Дистанция: |x1 - x2|, но модуль нелинейная функция
            # |x1 - x2| = max(x1 - x2, x2 - x1)
            # Т.к. мы минимизируем функцию, d = max(x1 - x2, x2 - x1)
            problem += d >= used_items[i] - used_items[j]
            problem += d >= used_items[j] - used_items[i]

        avg_distance = lp.lpSum(distances) / len(used_items)
        problem += avg_distance

        # РЕШЕНИЕ
        status = problem.solve()

        # ВЫВОД ЗНАЧЕНИЙ
        if status == lp.LpStatusOptimal:
            print(f"Problem is solved!")
            print(f"Waste: {min_waste}")
            print(f"Used pieces: {used_items}")
            print(f"Mean distance: {lp.value(problem.objective)}")
        elif lp.LpStatus[problem.status] == lp.LpStatusInfeasible:
            print(f"No solution found!")
            return -1

        # ВЫВОД В ПОНЯТНОМ ФОРМАТЕ
        output = "СХЕМА РАСКРОЯ ЗАГОТОВОК:\n\n"
        for i in range(len(x)):
            l = self._stock_lengths[i]
            cur_used = lp.value(used_items[i])
            if isinstance(cur_used, (int, float)) and cur_used > 0:
                output += f"Заготовка {l} м:\n"
            for j in range(len(x[i])):
                combination_qty = int(lp.value(x[i][j])) # Количество используемой комбинации
                print(f"x{i}{j} = {combination_qty}; piece: {self._stock_lengths[i]}")
                if combination_qty > 0:
                    # Количество заказанных отрезков в комбинации
                    pieces_count = self._patterns[i][j].pieces_count
                    combination = f"[{self._demand_length} x {pieces_count}]"
                    cur_waste = self._patterns[i][j].waste
                    cur_waste = self._clean_float(cur_waste) # Преобразуем в читаемый формат
                    output += f"План раскроя: {combination} | Обрезок: {cur_waste} м\n"
                    output += f"Количество повторений: {combination_qty}\n\n"
        min_waste = self._clean_float(min_waste) # Преобразуем в читаемый формат
        output += f"Общие отходы: {min_waste} м "
        if min_waste > 0:
            total_used_length = sum(self._stock_lengths[i] * lp.value(used_items[i]) 
                                    for i in range(len(self._stock_lengths)))
            waste_part = min_waste / total_used_length * 100
            output += f"({waste_part:.2f}% от использованной длины)"

        return output
    
    def _clean_float(self, num, max_precision=15):
        """
        Находит минимальную точность, убирает лишние цифры.
        Пример: 0.33999999999999986 -> 0.34
        """
        print(f"num: {num}")
        for precision in range(1, max_precision + 1):
            rounded = round(num, precision)
            if abs(num - rounded) < 1e-10:
                print(f"rounded: {rounded}")
                return rounded
        return round(num, max_precision)
    