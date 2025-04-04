from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Renders the file templates/index.html
    return render_template('index.html')

if __name__ == '__main__':
    # 8111 is just an example port; you can use 5000 or any open port.
    app.run(host='0.0.0.0', port=8111, debug=True, use_reloader=False)

