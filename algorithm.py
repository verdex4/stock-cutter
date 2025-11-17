import pulp as lp
from collections import namedtuple
from itertools import combinations

class Solver:
    def __init__(self, user_input):
        (self._stock_lengths, self._stock_quantities, 
        self._demand_length, self._demand_quantity) = self._parse_input(user_input)
        print(self._stock_lengths, self._stock_quantities, 
        self._demand_length, self._demand_quantity)
    
    def solve(self):
        message = self._validate_data()
        if message != "OK":
            return message
        self._patterns = self._make_cutting_patterns()
        print(self._patterns)
        min_waste = self._find_min_waste()
        if min_waste == -1:
            return "Раскрой невозможен, недостаточно профиля на складе"
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
            if qty < 0:
                message = "Не должно быть отрицательных чисел"
                return message
            elif qty > 0:
                new_stock_lengths.append(l)
                new_stock_quantities.append(qty)
        self._stock_lengths = new_stock_lengths
        self._stock_quantities = new_stock_quantities
            
        if self._demand_length == 0:
            message = "Не должно быть отрицательных чисел"
            return message
        if self._demand_quantity == 0:
            message = "Заказ пустой"
            return message
        return message
    
    def _make_cutting_patterns(self):
        Pattern = namedtuple("Pattern", ['pieces_count', 'waste'])
        patterns = []
        for i in range(len(self._stock_lengths)):
            profile_patterns = []
            pieces_count = 1
            waste = self._stock_lengths[i] - self._demand_length
            while waste >= 0:
                profile_patterns.append(Pattern(pieces_count, waste))
                pieces_count += 1
                waste -= self._demand_length
            patterns.append(profile_patterns)
        return patterns

    def _find_min_waste(self):
        """
        Решает задачу линейного целочисленного программирования 
        и возвращает минимально возможный остаток при раскрое.

        Задача: минимизировать функцию остатков.

        Целевая функция: сумма полученных остатков.

        Ограничения:
            1. Количество полученных профилей для разреза должно быть целым, 
            больше или равно 0.
            2. Мы не можем использовать больше профилей, чем на складе.
            3. Полученное количество отрезков должно быть равно заказанному количеству.
        
        Используемые переменные:
            1. self._patterns - варианты раскроя для каждого профиля, 
            где элемент self._patterns[i][j] - одна комбинация, кортеж вида 
            (количество_полученных_отрезков, остаток).
            Размерность 2.
            Количество строк - количество профилей.
            Количество столбцов - не фиксировано, зависит от профиля.
            2. x - таблица с целыми числами, 
            где x[i][j] - количество комбинации self._patterns[i][j] в решении
            Размер совпадает с self._patterns
        """
        x = [[] for i in range(len(self._patterns))]
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                x[i].append(lp.LpVariable(
                    name=f"x{i}{j}",
                    lowBound=0,
                    upBound=self._stock_quantities[i],
                    cat=lp.LpInteger)) # ПЕРВОЕ ОГРАНИЧЕНИЕ
                
        problem = lp.LpProblem("Waste_minimization", lp.LpMinimize)

        # ЦЕЛЕВАЯ ФУНКЦИЯ
        total_waste = 0
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                total_waste += self._patterns[i][j].waste * x[i][j]

        problem += total_waste

        # ВТОРОЕ ОГРАНИЧЕНИЕ
        for i in range(len(x)):
            used_profiles = lp.lpSum(x[i])
            problem += used_profiles <= self._stock_quantities[i]

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
        if lp.LpStatus[problem.status] == "Optimal":
            print(f"Минимальный остаток: {min_waste}")
            for i in range(len(x)):
                for j in range(len(x[i])):
                    print(f"x{i}{j} = {lp.value(x[i][j])}")
            return min_waste
        elif lp.LpStatus[problem.status] == "Infeasible":
            return -1

    def _find_uniform_solution(self, min_waste):
        """
        Решает задачу линейного программирования 
        и возвращает самое равномерное решение с минимальными остатками.
        Решает ту же задачу, но с условием остатка, равному минимальному (min_waste).

        Задача: минимизировать функцию разброса.
        Целевая функция: средняя дистанция между всеми элементами
        Ограничения:
            1. Количество полученных профилей для разреза должно быть целым, 
            больше или равно 0.
            2. Мы не можем использовать больше профилей, чем на складе.
            3. Полученное количество отрезков должно быть равно заказанному количеству.
            4. Полученный остаток должен быть равен минимальному.
        
        Используемые переменные:
            1. self._patterns - варианты раскроя для каждого профиля, 
            где элемент self._patterns[i][j] - одна комбинация, кортеж вида 
            (количество_полученных_отрезков, остаток).
            Размерность 2.
            Количество строк - количество профилей.
            Количество столбцов - не фиксировано, зависит от профиля.
            2. x - таблица с целыми числами, 
            где x[i][j] - количество комбинации self._patterns[i][j] в решении
            Размер совпадает с self._patterns
            3. distances - список дистанций между всеми возможными парами профилей.
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
                
        problem = lp.LpProblem("Waste_minimization", lp.LpMinimize)

        # ВТОРОЕ ОГРАНИЧЕНИЕ
        for i in range(len(x)):
            used_profiles = lp.lpSum(x[i])
            problem += used_profiles <= self._stock_quantities[i]

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
        used_profiles = [lp.lpSum(x[i]) for i in range(len(x))]
        # Находим все возможные пары использованных профилей (в индексах)
        pairs = combinations(range(len(used_profiles)), 2)
        distances = []
        for i, j in pairs:
            d = lp.LpVariable(f"d{i}{j}")
            distances.append(d)
            # Дистанция: |x1 - x2|, но модуль нелинейная функция
            # |x1 - x2| = max(x1 - x2, x2 - x1)
            # Т.к. мы минимизируем функцию, d = max(x1 - x2, x2 - x1)
            problem += d >= used_profiles[i] - used_profiles[j]
            problem += d >= used_profiles[j] - used_profiles[i]

        avg_distance = lp.lpSum(distances) / len(used_profiles)
        problem += avg_distance

        # РЕШЕНИЕ
        status = problem.solve()

        # ВЫВОД ЗНАЧЕНИЙ
        if lp.LpStatus[problem.status] == lp.LpStatusOptimal:
            print(f"Остатки: {min_waste}")
            print(f"Использованные профили: {used_profiles}")
            print(f"Среднее расстояние: {lp.value(problem.objective)}")
        elif lp.LpStatus[problem.status] == lp.LpStatusInfeasible:
            return -1

        # ВЫВОД В ПОНЯТНОМ ФОРМАТЕ
        output = "СХЕМА РАСКРОЯ ЗАГОТОВОК:\n\n"
        for i in range(len(x)):
            l = self._stock_lengths[i]
            cur_used = lp.value(used_profiles[i])
            if isinstance(cur_used, (int, float)) and cur_used > 0:
                output += f"Заготовка {l} м:\n"
            for j in range(len(x[i])):
                combination_qty = int(lp.value(x[i][j])) # Количество используемой комбинации
                print(f"x{i}{j} = {combination_qty}; profile: {self._stock_lengths[i]}")
                if combination_qty > 0:
                    # Количество заказанных профилей в комбинации
                    realised_profiles = self._patterns[i][j].pieces_count
                    combination = '['
                    for k in range(realised_profiles):
                        if k < realised_profiles - 1:
                            combination += f"{self._demand_length}, "
                            continue
                        combination += f"{self._demand_length}]" 
                    output += f"План раскроя: {combination}"
                    cur_waste = self._patterns[i][j].waste 
                    if cur_waste > 0:
                        output += f" | Обрезок: {cur_waste} м\n"
                    else:
                        output += '\n'
                    output += f"Количество повторений: {combination_qty}\n\n"
        output += f"Общие отходы: {min_waste} м "
        if min_waste > 0:
            total_used_length = sum(self._stock_lengths[i] * lp.value(used_profiles[i]) 
                                    for i in range(len(self._stock_lengths)))
            waste_part = min_waste / total_used_length * 100
            output += f"({waste_part:.2f}% от использованной длины)"

        return output
    