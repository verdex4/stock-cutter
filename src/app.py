from flask import Flask, render_template, request, jsonify
from parser import Parser
from algorithm import Solver

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=['POST'])
def process():
    user_input = request.form
    parser = Parser(user_input)

    try:
        clean_input = parser.parse()
        solver = Solver(clean_input)
        result = solver.solve()
        return jsonify({'result': result})
    
    except ValueError as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run()