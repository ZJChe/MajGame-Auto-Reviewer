from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <h1>你好，世界！</h1>
    <p>这是一个 Flask 应用，已经可以被公网访问了。</p>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)