from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_mysqldb import MySQL
import mysql.connector
from dotenv import load_dotenv
import os

# ------------------- CONFIGURAÇÃO APP -------------------
app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY', '1234')

# ------------------- CONFIGURAÇÃO BANCO -------------------
def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'minha_oficina'),
        auth_plugin="mysql_native_password"
    )

# mysql = MySQL(app)
# app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'localhost')
# app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
# app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '')
# app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'minha_oficina')


# ------------------- AUTENTICAÇÃO -------------------
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        conexao = conectar_banco() # Abre conexão
        cursor = conexao.cursor(dictionary=True)      
        
        cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            conexao.close()
            flash('Este e-mail já está cadastrado!', 'danger')
            return redirect(url_for('cadastro'))

        # Note que usei 'senha_hash' para bater com o SQL acima
        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s,%s,%s)',
            (nome, email, senha)
        )
        conexao.commit() # Salva no banco usando a conexao aberta
        
        cursor.close()
        conexao.close() # Sempre feche
        
        flash('Usuário registrado com sucesso!', 'success') 
        return redirect(url_for('login'))

    return render_template('cadastro.html')


@app.route('/login', methods=['POST', 'GET'])
def login_usuario():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()

            # Verifica se usuário existe e se a senha coincide
            if usuario and usuario['senha_hash'] == senha:
                # Aqui você pode adicionar session['user_id'] = usuario['id'] futuramente
                flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('E-mail ou senha incorretos!', 'danger')
                
        finally:
            cursor.close()
            conexao.close()

    return render_template('login.html')

# ------------------- PÁGINAS PRINCIPAIS -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Se quiser passar dados dinâmicos para os cards, faça aqui
    return render_template('dashboard.html')


# ------------------- CLIENTES -------------------
@app.route('/clientes')
def clientes():
    conexao = conectar_banco() # ESSENCIAL: Abrir a conexão antes de tudo
    cursor = conexao.cursor(dictionary=True) # dictionary=True para usar o.nome no HTML
    
    try:
        cursor.execute('SELECT * FROM clientes ORDER BY nome ASC')
        lista = cursor.fetchall()
        return render_template('clientes.html', clientes=lista)
    
    except Exception as e:
        return f"Erro no banco: {e}"
        
    finally:
        # ESSENCIAL: Fechar sempre para não travar o MySQL
        cursor.close()
        conexao.close()
@app.route('/add_cliente', methods=['POST'])
def add_cliente():
    # 1. Abre a conexão e o cursor
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # 2. Executa o comando
        cursor.execute(
            'INSERT INTO clientes (nome, telefone, documento, email, endereco) VALUES (%s,%s,%s,%s,%s)',
            (
                request.form['nome'], 
                request.form['tel'], 
                request.form['doc'], 
                request.form['email'], 
                request.form['end']
            )
        )
        # 3. Salva as alterações (ESSENCIAL)
        conexao.commit()
        flash('Cliente cadastrado!', 'success')
    except Exception as e:
        flash(f'Erro ao cadastrar: {e}', 'danger')
    finally:
        # 4. Fecha tudo para liberar o banco (OBRIGATÓRIO no PythonAnywhere)
        cursor.close()
        conexao.close()

    return redirect(url_for('clientes.html'))


# @app.route('/deletar_veiculo/<int:id>')
# def deletar_veiculo(id):
#     conexao = conectar_banco() # Adicione isso
#     cursor = conexao.cursor()
#     cursor.execute('DELETE FROM veiculos WHERE id = %s', (id,))
#     conexao.commit()
#     cursor.close()
#     conexao.close()
#     flash('Veículo removido!', 'danger')
#     return redirect(url_for('veiculos'))



# ------------------- VEÍCULOS -------------------
@app.route('/veiculos')
def veiculos():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    
    try:
        # Busca veículos com o nome do dono (JOIN)
        cursor.execute('SELECT v.*, c.nome as dono FROM veiculos v JOIN clientes c ON v.cliente_id = c.id')
        v_lista = cursor.fetchall()
        
        # Busca lista de clientes para preencher o <select> no formulário de adição
        cursor.execute('SELECT id, nome FROM clientes')
        c_lista = cursor.fetchall()
        
        return render_template('veiculos.html', veiculos=v_lista, clientes=c_lista)
    
    except Exception as e:
        return f"Erro ao carregar veículos: {e}"
    
    finally:
        # Essencial para não travar o servidor do PythonAnywhere
        cursor.close()
        conexao.close()

@app.route('/add_veiculo', methods=['POST'])
def add_veiculo():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO veiculos (modelo, placa, cliente_id) VALUES (%s,%s,%s)',
            (request.form['modelo'], request.form['placa'], request.form['cliente_id'])
        )
        conexao.commit()
        flash('Veículo registrado!', 'success')
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('veiculos.html'))

@app.route('/deletar_veiculo/<int:id>')
def deletar_veiculo(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM veiculos WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Veículo removido!', 'danger')
    return redirect(url_for('veiculos'))

# ------------------- SERVIÇOS -------------------
@app.route('/item')
def item():
    conexao = conectar_banco()
    # O segredo está no buffered=True
    cursor = conexao.cursor(dictionary=True, buffered=True)
    
    try:
        # 1. Busca as Ordens de Serviço
        cursor.execute('SELECT os.*, c.nome as c_nome, v.modelo as v_mod FROM ordens_servico os JOIN clientes c ON os.cliente_id = c.id JOIN veiculos v ON os.veiculo_id = v.id')
        oss = cursor.fetchall()
        
        # 2. Busca a lista de Clientes (agora funciona!)
        cursor.execute('SELECT id, nome FROM clientes')
        cs = cursor.fetchall()
        
        # 3. Busca a lista de Veículos
        cursor.execute('SELECT id, modelo, placa FROM veiculos')
        vs = cursor.fetchall()
        
        return render_template('os.html', ordens=oss, clientes=cs, veiculos=vs)
    
    finally:
        cursor.close()
        conexao.close()



@app.route('/add_os', methods=['POST'])
def add_os():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    try:
        # Capturando os dados do formulário
        cliente_id = request.form['cliente_id']
        veiculo_id = request.form['veiculo_id']
        descricao = request.form['descricao']
        valor = request.form['valor']

        # Executando o INSERT
        cursor.execute(
            'INSERT INTO ordens_servico (cliente_id, veiculo_id, descricao, valor) VALUES (%s, %s, %s, %s)',
            (cliente_id, veiculo_id, descricao, valor)
        )
        
        # Salvando no banco
        conexao.commit()
        flash('Ordem de Serviço aberta com sucesso!', 'success')
        
    except Exception as e:
        conexao.rollback() # Cancela a operação em caso de erro
        flash(f'Erro ao abrir OS: {e}', 'danger')
        
    finally:
        # OBRIGATÓRIO fechar no PythonAnywhere
        cursor.close()
        conexao.close()
        
    return redirect(url_for('ordensservico.html'))

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
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM estoque')
        items = cursor.fetchall()
        return render_template('estoque.html', estoque=items)
    finally:
        cursor.close()
        conexao.close()

@app.route('/add_estoque', methods=['POST'])
def add_estoque():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            'INSERT INTO estoque (peca, quantidade) VALUES (%s,%s)',
            (request.form['peca'], request.form['quantidade'])
        )
        conexao.commit()
        flash('Item adicionado ao estoque!', 'success')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('estoque'))

# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(debug=True)