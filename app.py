from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cadastrodecliente")
def cadastrodecliente():
    return render_template("cadastrodecliente.html")

@app.route("/cadastrodeveiculos")
def cadastrodeveiculos():
    return render_template("cadastrodeveiculos.html")

@app.route("/controledeestoque")
def controledeestoque():
    return render_template("controledeestoque.html")

@app.route("/controledeordensdeservico")
def controledeordensdeservico():
    return render_template("controledeordensdeservico.html")

@app.route("/relatorios")
def relatorios():
    return render_template("relatorios.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/item")
def item():
    return render_template("item.html")

@app.route("/pagamento")
def pagamento():
    return render_template("pagamento.html")

if __name__ == "__main__":
    app.run(debug=True)