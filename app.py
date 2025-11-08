from flask import Flask, render_template, request, jsonify
from profile_cutter import Cutter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/process", methods=['POST'])
def process():
    user_input = request.form
    print(f"input: {user_input}")

    error_message = _validate_input(user_input)
    if error_message:
        return jsonify({'result': error_message})

    cutter = Cutter(user_input)
    print(f"stock: {cutter._stock}")
    print(f"demand: {cutter._demand}")
    
    result = cutter.calculate()
    print(f"result: {result}")
    
    return jsonify({'result': result})

def _validate_input(user_input):
    for key, value in user_input.items():
        if len(value) == 0:
            return "Заполните все поля!"
    return None

if __name__ == '__main__':
    app.run()