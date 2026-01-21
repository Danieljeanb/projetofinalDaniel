from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'chave_minha_oficina_2025'

# CONFIGURAÇÃO BANCO
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'minha_oficina'

mysql = MySQL(app)

# ------------------- AUTENTICAÇÃO -------------------

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user:
        flash('Este e-mail já está cadastrado!', 'danger')
        return redirect(url_for('cadastro'))

    cursor.execute(
        'INSERT INTO usuarios (nome, email, senha) VALUES (%s,%s,%s)',
        (nome, email, senha)
    )
    mysql.connection.commit()
    flash('Usuário registrado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/login_usuario', methods=['POST'])
def login_usuario():
    if not request.form or 'email' not in request.form or 'senha' not in request.form:
        flash('Por favor, preencha todos os campos!', 'danger')
        return redirect(url_for('login'))
    email = request.form['email']
    senha = request.form['senha']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM usuarios WHERE email = %s AND senha = %s', (email, senha))
    user = cursor.fetchone()

    if user:
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('E-mail ou senha inválidos!', 'danger')
        return redirect(url_for('login'))

# ------------------- PÁGINAS PRINCIPAIS -------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('base.html')

# ------------------- CLIENTES -------------------

@app.route('/clientes')
def clientes():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM clientes ORDER BY nome ASC')
    lista = cursor.fetchall()
    return render_template('clientes.html', clientes=lista)

@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT INTO clientes (nome, telefone, documento, email, endereco) VALUES (%s,%s,%s,%s,%s)',
        (request.form['nome'], request.form['tel'], request.form['doc'], request.form['email'], request.form['end'])
    )
    mysql.connection.commit()
    flash('Cliente cadastrado!', 'success')
    return redirect(url_for('clientes'))

@app.route('/deletar_cliente/<int:id>')
def deletar_cliente(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Cliente e dados vinculados removidos!', 'danger')
    return redirect(url_for('clientes'))

# ------------------- VEÍCULOS -------------------

@app.route('/veiculos')
def veiculos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT v.*, c.nome as dono FROM veiculos v JOIN clientes c ON v.cliente_id = c.id')
    v_lista = cursor.fetchall()
    cursor.execute('SELECT id, nome FROM clientes')
    c_lista = cursor.fetchall()
    return render_template('veiculos.html', veiculos=v_lista, clientes=c_lista)

@app.route('/add_veiculo', methods=['POST'])
def add_veiculo():
    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT INTO veiculos (modelo, placa, cliente_id) VALUES (%s,%s,%s)',
        (request.form['modelo'], request.form['placa'], request.form['cliente_id'])
    )
    mysql.connection.commit()
    flash('Veículo registrado!', 'success')
    return redirect(url_for('veiculos'))

@app.route('/deletar_veiculo/<int:id>')
def deletar_veiculo(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM veiculos WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Veículo removido!', 'danger')
    return redirect(url_for('veiculos'))

# ------------------- SERVIÇOS -------------------

@app.route('/servicos')
def servicos():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT os.*, c.nome as c_nome, v.modelo as v_mod FROM ordens_servico os JOIN clientes c ON os.cliente_id = c.id JOIN veiculos v ON os.veiculo_id = v.id')
    oss = cursor.fetchall()
    cursor.execute('SELECT id, nome FROM clientes')
    cs = cursor.fetchall()
    cursor.execute('SELECT id, modelo, placa FROM veiculos')
    vs = cursor.fetchall()
    return render_template('os.html', ordens=oss, clientes=cs, veiculos=vs)

@app.route('/add_os', methods=['POST'])
def add_os():
    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT INTO ordens_servico (cliente_id, veiculo_id, descricao, valor) VALUES (%s,%s,%s,%s)',
        (request.form['cliente_id'], request.form['veiculo_id'], request.form['descricao'], request.form['valor'])
    )
    mysql.connection.commit()
    flash('OS Aberta!', 'success')
    return redirect(url_for('servicos'))

@app.route('/deletar_os/<int:id>')
def deletar_os(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM ordens_servico WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('OS excluída!', 'warning')
    return redirect(url_for('servicos'))

# ------------------- ESTOQUE -------------------

@app.route('/estoque')
def estoque():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM estoque')
    items = cursor.fetchall()
    return render_template('estoque.html', estoque=items)

@app.route('/add_estoque', methods=['POST'])
def add_estoque():
    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT INTO estoque (peca, quantidade) VALUES (%s,%s)',
        (request.form['peca'], request.form['quantidade'])
    )
    mysql.connection.commit()
    flash('Item adicionado ao estoque!', 'success')
    return redirect(url_for('estoque'))

# ------------------- MAIN -------------------

if __name__ == '__main__':
    app.run(debug=True)