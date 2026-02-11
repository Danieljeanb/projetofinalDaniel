from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_mysqldb import MySQL
import mysql.connector
from dotenv import load_dotenv
import os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

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
        database=os.getenv('DB_NAME', 'sistema_oficina'),
        auth_plugin="mysql_native_password"
    )


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

def is_user_logged_in():
    """Verifica se o usuário está autenticado na sessão"""
    from flask import session
    return 'user_id' in session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Adicione sua lógica de autenticação aqui
        if not is_user_logged_in():  # sua função de validação
            return 'Acesso negado', 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')


@app.route('/servicos')
def gerenciar_os(): # Este nome deve bater com o url_for
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM ordens_servico")
        ordens = cursor.fetchall()
        sql_clientes = "SELECT * FROM clientes"
        cursor.execute(sql_clientes)
        clientes = cursor.fetchall()
        sql_veiculos = "SELECT * FROM veiculos"
        cursor.execute(sql_veiculos)
        veiculos = cursor.fetchall()
        return render_template('gerenciar_os.html', ordens=ordens, clientes=clientes, veiculos=veiculos)
    finally:
        cursor.close()
        conexao.close()
    
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

    return redirect(url_for('clientes'))


#
# ------------------- VEÍCULOS -------------------


@app.route('/deletar_veiculo/<int:id>')
def deletar_veiculo(id): # O NOME AQUI DEVE SER EXATAMENTE ESTE
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute('DELETE FROM veiculos WHERE id = %s', (id,))
        conexao.commit()
        flash('Veículo removido com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar: {e}', 'danger')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('veiculos'))


@app.route('/deletar_cliente/<int:id>')
def deletar_cliente(id): # O url_for procura este nome aqui
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute('DELETE FROM clientes WHERE id = %s', (id,))
        conexao.commit()
        flash('Cliente removido!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar: {e}', 'danger')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('clientes'))


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



@app.route('/ordensdeservico', methods=['POST'])
def add_ordem_servico():
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
    return redirect(url_for('ordensservico'))

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

@app.route('/relatorios')
def relatorios():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    
    try:
        # 1. Total faturado em OS Concluídas
        cursor.execute("SELECT SUM(valor) as total FROM ordens_servico WHERE status = 'CONCLUÍDA'")
        faturamento = cursor.fetchone()['total'] or 0

        # 2. Contagem de OS por Status (para o gráfico/resumo)
        cursor.execute("SELECT status, COUNT(*) as qtd FROM ordens_servico GROUP BY status")
        status_resumo = cursor.fetchall()

        # 3. Top Clientes (quem mais gastou na oficina)
        query_top = """
            SELECT c.nome, SUM(os.valor) as total_gasto 
            FROM ordens_servico os 
            JOIN clientes c ON os.cliente_id = c.id 
            WHERE os.status = 'CONCLUÍDA'
            GROUP BY c.id ORDER BY total_gasto DESC LIMIT 5
        """
        cursor.execute(query_top)
        top_clientes = cursor.fetchall()

        return render_template('relatorios.html', 
                               faturamento=faturamento, 
                               status_resumo=status_resumo, 
                               top_clientes=top_clientes)
    finally:
        cursor.close()
        conexao.close()

#

@app.route('/os/add_item/<int:os_id>', methods=['POST'])
@login_required
def add_item_os(os_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            'INSERT INTO itens_os (os_id, descricao, quantidade, valor_unitario) VALUES (%s, %s, %s, %s)',
            (os_id, request.form['descricao'], request.form['quantidade'], request.form['valor'].replace(',', '.'))
        )
        conexao.commit()
        flash('Item adicionado!', 'success')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('detalhes_os', id=os_id))

@app.route('/os/add_servico/<int:os_id>', methods=['POST'])
def add_servico_os(os_id):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            'INSERT INTO servicos_os (os_id, descricao, horas, valor_hora) VALUES (%s, %s, %s, %s)',
            (os_id, request.form['descricao'], request.form['horas'], request.form['valor'].replace(',', '.'))
        )
        conexao.commit()
        flash('Serviço adicionado!', 'success')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('detalhes_os', id=os_id))

@app.route('/os/detalhes/<int:id>')
@login_required
def detalhes_os(id):
    conexao = conectar_banco()
    # buffered=True é importante para realizar múltiplos SELECTs na mesma conexão
    cursor = conexao.cursor(dictionary=True, buffered=True)
    
    try:
        # 1. Busca os dados da OS, Cliente e Veículo (JOIN)
        query_os = """
            SELECT os.*, c.nome as cliente_nome, v.modelo as veiculo_nome, v.placa 
            FROM ordens_servico os
            JOIN clientes c ON os.cliente_id = c.id
            JOIN veiculos v ON os.veiculo_id = v.id
            WHERE os.id = %s
        """
        cursor.execute(query_os, (id,))
        os_data = cursor.fetchone()

        if not os_data:
            flash("Ordem de Serviço não encontrada!", "danger")
            return redirect(url_for('gerenciar_os'))

        # 2. Busca Peças vinculadas
        cursor.execute("SELECT * FROM itens_os WHERE os_id = %s", (id,))
        pecas = cursor.fetchall()
        
        # 3. Busca Serviços vinculados
        cursor.execute("SELECT * FROM servicos_os WHERE os_id = %s", (id,))
        servicos = cursor.fetchall()

        # 4. Cálculo do Total Geral para o card de destaque
        total_pecas = sum(p['quantidade'] * p['valor_unitario'] for p in pecas)
        total_servicos = sum(s['horas'] * s['valor_hora'] for s in servicos)
        total_geral = total_pecas + total_servicos

        return render_template('detalhes_os.html', 
                               os=os_data, 
                               pecas=pecas, 
                               servicos=servicos, 
                               total=total_geral)
    except Exception as e:
        flash(f"Erro ao carger detalhes: {e}", "danger")
        return redirect(url_for('gerenciar_os'))
    finally:
        cursor.close()
        conexao.close()

@app.route('/login')
def login(): # O nome desta função deve ser o mesmo que você usa no url_for
    return render_template('login.html')


@app.route('/ordens')
def listar_ordens():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    # 1. Busca Clientes para o Select
    cursor.execute("SELECT id, nome FROM clientes")
    lista_clientes = cursor.fetchall()

    # 2. Busca Veículos para o Select
    cursor.execute("SELECT id, modelo, placa FROM veiculos")
    lista_veiculos = cursor.fetchall()

    # 3. Busca Ordens com JOIN para pegar os nomes das colunas que você usou no HTML (o.c_nome e o.v_mod)
    query = """
        SELECT os.*, c.nome AS c_nome, v.modelo AS v_mod 
        FROM ordens_servico os
        JOIN clientes c ON os.cliente_id = c.id
        JOIN veiculos v ON os.veiculo_id = v.id
    """
    cursor.execute(query)
    lista_ordens = cursor.fetchall()

    cursor.close()
    conexao.close()

    # IMPORTANTE: Os nomes à esquerda (clientes=...) devem bater com o que está no {% for %}
    return render_template('ordens.html', 
                           clientes=lista_clientes, 
                           veiculos=lista_veiculos, 
                           ordens=lista_ordens)


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
        
    return redirect(url_for('veiculos'))




# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)