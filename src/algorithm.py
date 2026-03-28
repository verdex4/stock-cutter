import pulp as lp
from collections import namedtuple, defaultdict
from itertools import combinations
import numpy as np

class Solver:
    def __init__(self, user_input):
        (self._stock_lengths, self._stock_quantities, 
        self._demand_lengths, self._demand_quantities) = self._parse_input(user_input)
        print("after parse")
        print(f"stock lengths: {self._stock_lengths}")
        print(f"stock quantities: {self._stock_quantities}")
        print(f"demand lengths: {self._demand_lengths}")
        print(f"demand quantities: {self._demand_quantities}")
    
    def solve(self):
        message = self._validate_data()
        print("after validation")
        print(f"stock lengths: {self._stock_lengths}")
        print(f"stock quantities: {self._stock_quantities}")
        print(f"demand lengths: {self._demand_lengths}")
        print(f"demand quantities: {self._demand_quantities}")
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
        stock_lengths, stock_quantities, demand_lengths, demand_quantities = [], [], [], []
        for key, value in user_input.items():
            if key.startswith("stock_len"):
                stock_lengths.append(float(value))
            elif key.startswith("stock_qty"):
                stock_quantities.append(int(value))
            elif key.startswith("demand_len"):
                demand_lengths.append(float(value))
            elif key.startswith("demand_qty"):
                demand_quantities.append(int(value))
        return stock_lengths, stock_quantities, demand_lengths, demand_quantities
    
    def _validate_data(self):
        """Проверяет корректность входных данных, обновляет атрибуты класса"""
        new_stock = defaultdict(lambda: 0) # длина: количество
        new_demand = defaultdict(lambda: 0)

        # проверяем склад
        for stock_len, stock_qty in zip(self._stock_lengths, self._stock_quantities):
            if stock_len < 0 or stock_qty < 0:
                message = "Не должно быть отрицательных чисел"
                return message
            # нули принимаются как за несуществующую заготовку
            if stock_qty > 0:
                new_stock[stock_len] += stock_qty

        # проверяем отрезки
        for demand_len, demand_qty in zip(self._demand_lengths, self._demand_quantities):
            if demand_len < 0 or demand_qty < 0:
                message = "Не должно быть отрицательных чисел"
                return message
            # нули принимаются как за несуществующий отрезок
            if demand_qty > 0:
                new_demand[demand_len] = demand_qty
        
        if len(new_stock) == 0:
            message = "На складе пусто. Введите хотя бы одно количество, большее нуля"
            return message
        if len(new_demand) == 0:
            message = "Заказ пуст. Введите хотя бы одно количество, большее нуля"
            return message

        for length in new_demand.keys():
            if length > max(new_stock.keys()):
                message = f"Нельзя получить отрезки длины {length} м. при текущих исходных материалах"
                return message
        
        self._stock_lengths, self._stock_quantities = list(new_stock.keys()), list(new_stock.values())
        self._demand_lengths, self._demand_quantities = list(new_demand.keys()), list(new_demand.values())
        
        return "OK"
    
    def _make_cutting_patterns(self):
        Pattern = namedtuple("Pattern", ['piece_quantities', 'waste'])
        all_patterns = []
        for stock_len in self._stock_lengths:
            item_patterns = []
            iterables = []
            for demand_len in self._demand_lengths:
                iterables.append(range(int(stock_len//demand_len) + 1))
            for piece_quantities, waste in self.product_iterative(iterables, stock_len):
                item_patterns.append(Pattern(piece_quantities, waste))
            all_patterns.append(item_patterns)
            print(f"added item patterns: {item_patterns}")
        return all_patterns
    
    def product_iterative(self, iterables, stock_len, repeat=1):
        print(f"CURRENT ITEM: {stock_len}")
        print(f"iterables: {iterables}")
        pools = [tuple(pool) for pool in iterables] * repeat
        n = len(pools)
        
        if n == 0:
            raise ValueError("Empty iterables!")
        
        indices = [0] * (n - 1) + [1] # начинаем с индексов [0, 0, ..., 1]
        lengths = [len(pool) for pool in pools]
        
        while True:
            # генерируем текущую комбинацию
            # кортеж вида (кол-во первого заказанного отрезка, кол-во второго отрезка и т.д.)
            piece_quantities = tuple(pools[i][indices[i]] for i in range(n))
            print(f"Generated combination: {piece_quantities}")
            
            # проверяем валидность комбинации (сумма длин отрезков должна быть меньше stock_len)
            combo_sum = 0
            problem_idx = None
            for idx, (l, qty) in enumerate(zip(self._demand_lengths, piece_quantities)):
                combo_sum += l * qty
                if combo_sum > stock_len:
                    problem_idx = idx
                    break
            if problem_idx is None:
                # комбинация подходит
                waste = stock_len - combo_sum
                start = n - 1
                print(f"Combination is returned")
                yield piece_quantities, waste
            else:
                # комбинация НЕ подходит
                print(f"Combination is NOT returned")
                start = problem_idx - 1
            
            # ищем разряд для увеличения справа налево
            for i in range(start, -1, -1):
                if indices[i] < lengths[i] - 1:
                    indices[i] += 1
                    # обнуляем все индексы справа
                    for j in range(i+1, n):
                        indices[j] = 0
                    break
            else:
                # цикл завершен без break -> все комбинации рассмотрены
                return
    
    def _sum_piece_quantities(self):
        if not self._patterns:
            return []

        n = len(self._demand_quantities)
        result = [0] * n

        for stock_patterns in self._patterns:
            for pattern in stock_patterns:
                quantities = pattern.piece_quantities
                for i in range(n):
                    result[i] += quantities[i]
        
        return result

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
            3. Каждое полученное количество отрезков должно совпадать с заказанном количеством.
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
        n = len(self._demand_quantities)
        total_quantities = [0] * n

        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                quantities = self._patterns[i][j].piece_quantities
                for k in range(n):
                    total_quantities[k] += quantities[k] * x[i][j]
        print(f"total quantities: {total_quantities}")
        for total, required in zip(total_quantities, self._demand_quantities):
            problem += total == required

        # РЕШЕНИЕ
        status = problem.solve()

        # ПОЛУЧЕНИЕ РЕЗУЛЬТАТОВ
        min_waste = lp.value(problem.objective)
        if status == lp.LpStatusOptimal:
            print(f"Problem is solved!")
            print(f"Minimal waste: {min_waste}")
            for i in range(len(x)):
                for j in range(len(x[i])):
                    print(f"x{i}{j} = {lp.value(x[i][j])}; item: {self._stock_lengths[i]}")
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
            3. Каждое полученное количество отрезков должно совпадать с заказанном количеством.
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
        n = len(self._demand_quantities)
        total_quantities = [0] * n

        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                quantities = self._patterns[i][j].piece_quantities
                for k in range(n):
                    total_quantities[k] += quantities[k] * x[i][j]
        print(f"total quantities: {total_quantities}")
        for total, required in zip(total_quantities, self._demand_quantities):
            problem += total == required

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
                print(f"x{i}{j} = {combination_qty}; item: {self._stock_lengths[i]}")
                if combination_qty > 0:
                    combination = self._make_str_combination(self._patterns[i][j])
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
    
    def _make_str_combination(self, cur_pattern):
        quantities_to_print = []
        demand_to_use = []
        for l, qty in zip(self._demand_lengths, cur_pattern.piece_quantities):
            if qty == 0:
                continue
            quantities_to_print.append(qty)
            demand_to_use.append(l)
            
        combination = '['
        for i, (demand_len, qty) in enumerate(zip(demand_to_use, quantities_to_print)):
            if i == len(quantities_to_print) - 1:
                combination += f"{demand_len} x {qty}"
            else:
                combination += f"{demand_len} x {qty} + "
        combination += ']'
        return combination
    
    def _clean_float(self, num, max_precision=15):
        """
        Находит минимальную точность, убирает лишние цифры.
        Пример: 0.33999999999999986 -> 0.34
        """
        for precision in range(1, max_precision + 1):
            rounded = round(num, precision)
            if abs(num - rounded) < 1e-10:
                return rounded
        return round(num, max_precision)
    