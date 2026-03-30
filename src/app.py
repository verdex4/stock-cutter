from flask import Flask, render_template, request, jsonify
from parser import Parser
from algorithm import Solver
import logging

logging.basicConfig(level=logging.INFO, format='%(filename)s: %(lineno)d | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница."""
    return render_template('index.html')

@app.route("/process", methods=['POST'])
def process():
    """Решение задачи."""
    user_input = request.form
    parser = Parser(user_input)

    try:
        stock, demand = parser.parse()
        logger.info(f"parsed input: {stock, demand}")

        solver = Solver(stock, demand)
        result = solver.solve()
        logger.info(f"result output: {result}")
        return jsonify({'result': result}), 200 # ожидаем поле result
    
    except (ValueError, RuntimeError) as e:
        logger.error(e)
        return jsonify({'result': str(e)}), 400 # ожидаем поле result

if __name__ == '__main__':
    app.run()