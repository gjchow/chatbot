from flask import Flask, render_template, request
from response import chatbot_response
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    response = ["Send a message to get started"]
    message = ''
    if request.method == 'POST':
        req = request.form
        message = req.get('msg')
        response = chatbot_response(message)

    return render_template('index.html', response=response, message=message)


if __name__ == '__main__':
    app.run(debug=True)
