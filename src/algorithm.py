import pulp as lp
from collections import namedtuple
from itertools import combinations
from typing import Dict
import logging

logger = logging.getLogger(__name__)

Pattern = namedtuple("Pattern", ['piece_quantities', 'waste'])

class Solver:
    def __init__(self, stock: Dict[float, int], demand: Dict[float, int]):
        self.stock = stock
        self.demand = demand
        self._patterns = self._make_cutting_patterns()
    
    def solve(self) -> str:
        """Решает задачу и возвращает результат в виде текста."""
        try:
            result = self._find_uniform_solution()
        except (ValueError, RuntimeError):
            raise

        return result
    
    def _make_cutting_patterns(self):
        """Создает все возможные комбинации разрезов.
        
        Каждая комбинация - паттерн с двумя полями:

        * piece_quantities - кортеж с количеством каждого заказанного отрезка (i-тый элемент соответствует i-тому заказанному отрезку)
        * waste - остаток при раскрое

        Пример для заготовки длины 1 и заказанных отрезков длины 0.3 и 0.5.
        Мы можем получить следующие комбинации:

        * 1 отрезок длины 0.3 и 0 отрезков длины 0.5: остаток 0.7
        * 1 отрезок длины 0.3 и 1 отрезок длины 0.5: остаток 0.2
        * 2 отрезка длины 0.3 и 0 отрезков длины 0.5: остаток 0.4
        * 3 отрезка длины 0.3 и 0 отрезков длины 0.5: остаток 0.1
        
        Поэтому получаем паттерны [Pattern((1, 0), 0.7), Pattern((1, 1), 0.2), Pattern((2, 0), 0.4), Pattern((3, 0), 0.1)]
        """
        all_patterns = [] # все паттерны, список списков
        for stock_len in self.stock:
            item_patterns = [] # паттерны заготовки длины stock_len
            quantity_ranges = [] # список диапазонов с возможными количествами отрезков при распиле
            for demand_len in self.demand:
                quantity_ranges.append(range(int(stock_len//demand_len) + 1))

            # генерируем комбинации
            for piece_quantities, waste in self._product_iterative(quantity_ranges, stock_len):
                item_patterns.append(Pattern(piece_quantities, waste))

            all_patterns.append(item_patterns) # добавляем паттерны текущей заготовки
            logger.debug(f"patterns for item {stock_len}: {item_patterns}")
        return all_patterns
    
    def _product_iterative(self, iterables, max_sum, repeat=1):
        """Генератор комбинаций раскроя, использующий итеративный подход.
        
        Генерирует комбинации из заданных итерируемых объектов (длин отрезков) 
        с учетом ограничения суммы (max_sum).

        Args:
            iterables (list): итерируемые объекты (числа), из которых будут генерироваться комбинации
            max_sum (float): предел суммы длин отрезков из полученной комбинации
            repeat (int, optional): сколько раз брать список итерируемых объектов. Defaults to 1.
        """
        pools = [tuple(pool) for pool in iterables] * repeat
        n = len(pools)
        
        indices = [0] * (n - 1) + [1] # начинаем с индексов [0, 0, 0, ..., 1]
        lengths = [len(pool) for pool in pools]
        
        while True:
            # генерируем текущую комбинацию
            # кортеж вида (кол-во первого заказанного отрезка, кол-во второго отрезка и т.д.)
            piece_quantities = tuple(pools[i][indices[i]] for i in range(n))
            
            # проверяем сумму комбинации (должна быть не больше max_sum)
            combo_sum = 0
            problem_idx = None
            for idx, (l, qty) in enumerate(zip(self.demand, piece_quantities)):
                combo_sum += l * qty
                if combo_sum > max_sum:
                    problem_idx = idx
                    break
            if problem_idx is None: # комбинация подходит
                waste = max_sum - combo_sum
                start = n - 1
                yield piece_quantities, waste
            else: # комбинация НЕ подходит
                start = problem_idx - 1
            
            # ищем разряд для увеличения справа налево
            for i in range(start, -1, -1):
                if indices[i] < lengths[i] - 1:
                    indices[i] += 1
                    # обнуляем все индексы справа
                    for j in range(i + 1, n):
                        indices[j] = 0
                    break
            else:
                # цикл завершен без break -> все комбинации рассмотрены
                return

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
        stock_lengths = list(self.stock.keys())
        stock_quantities = list(self.stock.values())
        demand_quantities = list(self.demand.values())
        problem = lp.LpProblem("Waste_minimization", lp.LpMinimize)

        x = [[] for _ in range(len(self._patterns))]
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                x[i].append(lp.LpVariable(
                    name=f"x{i}{j}",
                    lowBound=0,
                    upBound=stock_quantities[i],
                    cat=lp.LpInteger)) # ПЕРВОЕ ОГРАНИЧЕНИЕ

        # ЦЕЛЕВАЯ ФУНКЦИЯ
        total_waste = 0
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                total_waste += self._patterns[i][j].waste * x[i][j]

        problem += total_waste

        # ВТОРОЕ ОГРАНИЧЕНИЕ
        for i in range(len(x)):
            used_amounts = lp.lpSum(x[i])
            problem += used_amounts <= stock_quantities[i]

        # ТРЕТЬЕ ОГРАНИЧЕНИЕ
        n = len(demand_quantities)
        total_quantities = [0] * n

        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                quantities = self._patterns[i][j].piece_quantities
                for k in range(n):
                    total_quantities[k] += quantities[k] * x[i][j]

        for total, required in zip(total_quantities, demand_quantities):
            problem += total == required

        # РЕШЕНИЕ
        status = problem.solve()

        # ПОЛУЧЕНИЕ РЕЗУЛЬТАТОВ
        min_waste = lp.value(problem.objective)
        if status == lp.LpStatusOptimal:
            logger.info(f"Minimal waste is found: {min_waste}")
            for i in range(len(x)):
                for j in range(len(x[i])):
                    p = self._patterns[i][j]
                    comb = self._make_str_combination(p)
                    debug_str = (
                        f"x{i}{j} = {lp.value(x[i][j])}; " + 
                        f"item: {stock_lengths[i]}; " +
                        f"combination: {comb}; " + 
                        f"waste: {self._clean_float(p.waste)}"
                    )
                    logger.debug(debug_str)
            return min_waste
        elif lp.LpStatus[problem.status] == "Infeasible":
            # решения нет только в случае нехватки исходного материала
            raise ValueError("Раскрой невозможен, недостаточно заготовок на складе!")

    def _find_uniform_solution(self) -> str:
        """
        Решает задачу линейного программирования 
        и возвращает самое равномерное решение с минимальными остатками.
        Использует решение задачи нахождения минимального остатка (find_min_waste()).

        Задача: минимизировать функцию разброса.
        
        Целевая функция: среднее расстояние между всеми элементами.
        
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
            6. distances - список расстояний между всеми возможными парами заготовок.
        
        Ограничения:
            1. Количество комбинаций x[i][j] >= 0, целое.
            2. Мы не можем использовать больше заготовок, чем на складе.
            3. Каждое полученное количество отрезков должно совпадать с заказанном количеством.
            4. Полученный остаток должен быть равен минимальному.
        """
        try:
            min_waste = self._find_min_waste()
        except ValueError:
            raise

        stock_lengths = list(self.stock.keys())
        stock_quantities = list(self.stock.values())
        demand_quantities = list(self.demand.values())
        problem = lp.LpProblem("Uniform_solution", lp.LpMinimize)

        x = [[] for _ in range(len(self._patterns))]
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                x[i].append(lp.LpVariable(
                    name=f"x{i}{j}",
                    lowBound=0,
                    upBound=stock_quantities[i],
                    cat=lp.LpInteger)) # ПЕРВОЕ ОГРАНИЧЕНИЕ

        # ВТОРОЕ ОГРАНИЧЕНИЕ
        for i in range(len(x)):
            used_amounts = lp.lpSum(x[i])
            problem += used_amounts <= stock_quantities[i]

        # ТРЕТЬЕ ОГРАНИЧЕНИЕ
        n = len(demand_quantities)
        total_quantities = [0] * n

        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                quantities = self._patterns[i][j].piece_quantities
                for k in range(n):
                    total_quantities[k] += quantities[k] * x[i][j]

        for total, required in zip(total_quantities, demand_quantities):
            problem += total == required

        # ЧЕТВЕРТОЕ ОГРАНИЧЕНИЕ
        total_waste = 0
        for i in range(len(self._patterns)):
            for j in range(len(self._patterns[i])):
                total_waste += self._patterns[i][j].waste * x[i][j]
        problem += total_waste == min_waste

        # ЦЕЛЕВАЯ ФУНКЦИЯ
        # количества использованных заготовок
        used_amounts = [lp.lpSum(x[i]) for i in range(len(x))] 
        # находим все возможные пары использованных заготовок (в индексах)
        pairs = combinations(range(len(used_amounts)), 2)
        distances = [] # расстояния между длинами
        for i, j in pairs:
            d = lp.LpVariable(f"d{i}{j}")
            distances.append(d)
            # Дистанция: |x1 - x2|, но модуль нелинейная функция
            # |x1 - x2| = max(x1 - x2, x2 - x1)
            # Т.к. мы минимизируем функцию, d = max(x1 - x2, x2 - x1)
            problem += d >= used_amounts[i] - used_amounts[j]
            problem += d >= used_amounts[j] - used_amounts[i]

        avg_distance = lp.lpSum(distances) / len(used_amounts)
        problem += avg_distance

        # РЕШЕНИЕ
        status = problem.solve()

        # ПОЛУЧЕНИЕ РЕЗУЛЬТАТА
        if status == lp.LpStatusOptimal:
            logger.info(f"Uniform solution with waste = {min_waste} found! Mean distance = {lp.value(problem.objective)}")
            for i in range(len(x)):
                for j in range(len(x[i])):
                    p = self._patterns[i][j]
                    comb = self._make_str_combination(p)
                    debug_str = (
                        f"x{i}{j} = {lp.value(x[i][j])}; " + 
                        f"item: {stock_lengths[i]}; " +
                        f"combination: {comb}; " + 
                        f"waste: {self._clean_float(p.waste)}"
                    )
                    logger.debug(debug_str)

        elif lp.LpStatus[problem.status] == lp.LpStatusInfeasible:
            raise RuntimeError("Равномерное решение не найдено!")

        # ВЫВОД В ПОНЯТНОМ ФОРМАТЕ
        output = "СХЕМА РАСКРОЯ ЗАГОТОВОК:\n\n"
        for i in range(len(x)):
            l = stock_lengths[i]
            cur_used = lp.value(used_amounts[i])
            if isinstance(cur_used, (int, float)) and cur_used > 0:
                output += f"Заготовка {l} м:\n"
            for j in range(len(x[i])):
                combination_qty = int(lp.value(x[i][j])) # количество используемой комбинации
                if combination_qty > 0:
                    comb = self._make_str_combination(self._patterns[i][j])
                    waste = self._clean_float(self._patterns[i][j].waste)
                    output += f"План раскроя: {comb} | Обрезок: {waste} м\n"
                    output += f"Количество повторений: {combination_qty}\n\n"
        min_waste = self._clean_float(min_waste) # преобразуем в читаемый формат
        output += f"Общие отходы: {min_waste} м "
        if min_waste > 0:
            # выводим процент остатка от использованной длины
            total_used_length = sum(stock_lengths[i] * lp.value(used_amounts[i]) 
                                    for i in range(len(stock_lengths)))
            waste_part = min_waste / total_used_length * 100
            output += f"({waste_part:.2f}% от использованной длины)"

        return output
    
    def _make_str_combination(self, pattern: Pattern):
        """Создает строковое представление комбинации из паттерна."""
        quantities_to_print = []
        demand_to_use = []
        for l, qty in zip(self.demand, pattern.piece_quantities):
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
    