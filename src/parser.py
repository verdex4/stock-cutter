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
        for v in self.data.values():
            self._check_value(v)

        stock = self._make_dict("stock")
        demand = self._make_dict("demand")

        return stock, demand

    def _check_value(self, value):
        """Проверяет корректность значения поля."""
        # проверяем заполнение поля
        if not value:
            raise ValueError("Все поля должны быть заполнены!")
        
        # проверяем на отрицательность
        if float(value) < 0:
            raise ValueError("Введенные числа не должны быть отрицательными!")

    def _make_dict(self, prefix) -> Dict[float, int]:
        lengths = self.data.getlist(f"{prefix}_lengths[]")
        quantities = self.data.getlist(f"{prefix}_quantities[]")

        return {float(l): int(q) for l, q in zip(lengths, quantities) if float(l) and int(q)}