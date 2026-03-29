from typing import Dict, Tuple
from werkzeug.datastructures import ImmutableMultiDict

class Parser:
    def __init__(self, data: ImmutableMultiDict):
        self.data = data
    
    def parse(self) -> Tuple[Dict[float, int], Dict[float, int]]:
        """
        Парсит входные данные, проверяя их корректность. 
        Возвращает 2 словаря с длинами и количествами (склад и заказ).
        """
        try:
            stock = self._make_dict("stock")
            demand = self._make_dict("demand")
        except ValueError:
            raise

        return stock, demand
    
    def _make_dict(self, prefix: str) -> Dict[float, int]:
        lengths = self.data.getlist(f"{prefix}_lengths[]")
        quantities = self.data.getlist(f"{prefix}_quantities[]")
        result = {}

        try:
            for str_l, str_q in zip(lengths, quantities):
                # проверяем корректность
                self._check_value(str_l)
                self._check_value(str_q)
                l, q = float(str_l), int(str_q)
                if l and q: # игнорируем нули
                    result[float(str_l)] = int(str_q)
            # проверяем, остались ли ненулевые значения
            self._check_dict(result, prefix)

        except ValueError:
            raise

        return result

    def _check_value(self, value: str):
        """Проверяет корректность значения поля."""
        # проверяем заполнение поля
        if not value:
            raise ValueError("Все поля должны быть заполнены!")
        
        # проверяем на отрицательность
        if float(value) < 0:
            raise ValueError("Введенные числа не должны быть отрицательными!")

    def _check_dict(self, map: Dict[float, int], prefix: str):
        """Проверяет словарь на заполненность."""
        if not map and prefix == "stock":
            raise ValueError("На складе пусто!")
        if not map and prefix == "demand":
            raise ValueError("Заказ пуст!")