from flask import Flask, render_template, request, redirect, url_for, flash, session
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
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        conexao = conectar_banco()
        if not conexao:
            flash('Erro ao conectar ao banco de dados', 'danger')
            return redirect(url_for('cadastro'))

        try:
            cursor = conexao.cursor(dictionary=True)      
            
            # 1. Verifica se o e-mail já existe
            cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
            user = cursor.fetchone()

            if user:
                flash('Este e-mail já está cadastrado!', 'danger')
                return redirect(url_for('cadastro'))

            # 2. Insere o novo usuário
            # DICA: Em produção, use generate_password_hash(senha) aqui
            cursor.execute(
                'INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)',
                (nome, email, senha)
            )
            conexao.commit()
            flash('Usuário registrado com sucesso!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"Erro detalhado: {e}") # Isso vai te mostrar o erro no terminal
            flash('Erro interno ao cadastrar usuário.', 'danger')
        
        finally:
            cursor.close()
            conexao.close()

    return render_template('cadastro.html') # Verifique se o nome do arquivo está correto


def is_user_logged_in():
    """Verifica se o usuário está autenticado na sessão"""
    from flask import session
    return 'user_id' in session


from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
   
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se a chave 'user_id' existe na sessão do navegador
        if 'user_id' not in session:
            flash('Acesso negado! Por favor, faça login para continuar.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')



@app.route('/servicos', methods=['GET', 'POST'])
def gerenciar_os():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    
    try:
        if request.method == 'POST':
            cliente_id = request.form.get('cliente_id')
            veiculo_id = request.form.get('veiculo_id')
            status = request.form.get('status', 'ABERTA')
            problema = request.form.get('problema')
            diagnostico = request.form.get('diagnostico')
            
            # Se for salvar o nome do mecanico como texto, o banco deve ter essa coluna
            # Se for ID, precisa mudar para mecanico_id no SQL abaixo
            mecanico = request.form.get('mecanico') 

            v_peca = float(request.form.get('valor_peca') or 0)
            v_servico = float(request.form.get('valor_servico') or 0)
            v_total = v_peca + v_servico

            sql_insert = """
                INSERT INTO servicos 
                (cliente_id, veiculo_id, status, problema_relatado, 
                 diagnostico_oficina, valor_total_pecas, valor_total_servicos, 
                 valor_total_geral) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (cliente_id, veiculo_id, status, problema, 
                                       diagnostico, v_peca, v_servico, v_total))
            conexao.commit()
            flash('OS aberta com sucesso!', 'success')
            return redirect(url_for('gerenciar_os'))

        # --- BLOCO GET ---
        # Busca ordens com nomes de clientes e modelos de veículos
        query = """
            SELECT s.*, c.nome AS c_nome, v.modelo AS v_mod, v.placa
            FROM servicos s
            LEFT JOIN clientes c ON s.cliente_id = c.id
            LEFT JOIN veiculos v ON s.veiculo_id = v.id
            ORDER BY s.id DESC
        """
        cursor.execute(query)
        ordens = cursor.fetchall()

        # Busca para os selects do Modal
        cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
        clientes = cursor.fetchall()

        cursor.execute("SELECT id, modelo, placa FROM veiculos ORDER BY modelo")
        veiculos = cursor.fetchall()

        return render_template('gerenciar_os.html', 
                               ordens=ordens, 
                               clientes=clientes, 
                               veiculos=veiculos)

    except Exception as e:
        print(f"Erro na Rota Servicos: {e}")
        flash(f"Erro: {e}", "danger")
        return redirect(url_for('gerenciar_os'))
    finally:
        cursor.close()
        conexao.close()


  
# 


@app.route('/login', methods=['POST', 'GET'])
def login_usuario():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        conexao = conectar_banco()
        # É boa prática tratar a falha de conexão aqui
        if not conexao:
            flash('Erro de conexão com o banco.', 'danger')
            return redirect(url_for('index'))

        cursor = conexao.cursor(dictionary=True)
        
        try:
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            usuario = cursor.fetchone()

            if usuario and usuario["senha"] == senha:
                session['user_id'] = usuario['id']
                session['user_nome'] = usuario['nome']
                session['user_email'] = usuario['email']
                flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('E-mail ou senha incorretos!', 'danger')
                return redirect(url_for('index'))

        except Exception as e:
            print(f"Erro no login: {e}")
            flash('Ocorreu um erro durante o login.', 'danger')
            return redirect(url_for('index'))
         
        finally:
            # Fechar cursor e conexão com segurança
            if cursor: cursor.close()
            if conexao: conexao.close()

    # --- O ERRO ESTAVA AQUI ---
    # Este return deve estar FORA do "if request.method == 'POST'"
    # Ele serve para carregar a página quando o usuário clica no link de login (GET)
    return render_template('login.html') 


# ------------------- PÁGINAS PRINCIPAIS -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def Logout():
    session.clear()  # Limpa todas as variáveis de sessão
    flash('Você saiu da sua conta com sucesso!', 'info')
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Se quiser passar dados dinâmicos para os cards, faça aqui
    return render_template('dashboard.html', nome=session.get('user_nome'))


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
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    documento = request.form.get('documento') # O 'name' no HTML deve ser 'documento'
    endereco = request.form.get('endereco')

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        # O erro 1054 acontece EXATAMENTE nesta linha se 'documento' não estiver no banco
        sql = "INSERT INTO clientes (nome, telefone, email, documento, endereco) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (nome, telefone, email, documento, endereco))
        conexao.commit()
        return redirect('/clientes')
    except Exception as e:
        print(f"Erro ao cadastrar: {e}")
        return f"Erro ao cadastrar: {e}", 500
    finally:
        cursor.close()
        conexao.close()

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
        cursor.execute('SELECT os.*, c.nome as c_nome, v.modelo as v_mod FROM servicos os JOIN clientes c ON os.cliente_id = c.id JOIN veiculos v ON os.veiculo_id = v.id')
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
            'INSERT INTO servicos (cliente_id, veiculo_id, descricao, valor) VALUES (%s, %s, %s, %s)',
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
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM servicos WHERE id = %s", (id,))
        conexao.commit()
        flash('Ordem de Serviço excluída!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir: {e}', 'danger')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('gerenciar_os'))



# ------------------- ESTOQUE -------------------
@app.route('/estoque')
def estoque():
    conexao = conectar_banco()
    if conexao is None:
        return "Erro: Não foi possível conectar ao banco de dados", 500
        
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM estoque')
        items = cursor.fetchall()
        return render_template('estoque.html', estoque=items)
    except Exception as e:
        # Isso imprimirá o erro real no console para você ler
        print(f"Erro ao executar query: {e}")
        return f"Erro no banco de dados: {e}", 500
    finally:
        cursor.close()
        conexao.close()


# @app.route('/estoque')
# def estoque_lista():
#     conexao = conectar_banco()
#     cursor = conexao.cursor(dictionary=True)
#     # Busca tudo da tabela estoque
#     cursor.execute("SELECT * FROM estoque")
#     dados_estoque = cursor.fetchall() 
#     cursor.close()
#     conexao.close()
#     # O nome 'estoque' aqui deve ser o mesmo do {% for item in estoque %}
#     return render_template('estoque.html', estoque=dados_estoque)


@app.route('/add_estoque', methods=['POST'])
def add_estoque():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        # 1. Pegamos os dados do formulário HTML (usando os 'names' corretos)
        nome_peca = request.form.get('peca')
        qtd = request.form.get('quantidade')
        preco = request.form.get('valor_venda') # Captura o preço digitado pelo usuário

        # 2. Ajustamos o INSERT para usar a variável 'preco' em vez de 0.00
        sql = "INSERT INTO estoque (nome, quantidade_estoque, valor_venda) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nome_peca, qtd, preco)) 
        
        conexao.commit()
        flash('Item adicionado ao estoque!', 'success')
        
    except Exception as e:
        print(f"Erro ao salvar no banco: {e}")
        flash('Erro ao salvar no banco.', 'danger')
    finally:
        cursor.close()
        conexao.close()
    
    # 3. CORREÇÃO DO BUILDERROR: Redireciona para o nome correto da função
    return redirect(url_for('estoque_lista')) 



@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')
    # conexao = conectar_banco()
    # cursor = conexao.cursor(dictionary=True)
    # try:
    #     # A query deve usar o nome EXATO que está no banco
    #     query = "SELECT SUM(valor) AS total_vendas, COUNT(*) AS total_os FROM ordens_servico"
    #     cursor.execute(query)
    #     relatorio = cursor.fetchone()
        
        
    # except Exception as e:
    #     print(f"Erro ao gerar relatório: {e}")
    #     return f"Erro: {e}", 500
    # finally:
    #     cursor.close()
    #     conexao.close()

#

@app.route('/add_item_os/<int:os_id>', methods=['POST'])
def add_item_os(os_id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        produto_id = request.form.get('produto_id')
        quantidade = int(request.form.get('quantidade') or 1)

        # 1. Busca os detalhes da peça no estoque
        cursor.execute("SELECT nome, preco_venda FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()

        if produto:
            # 2. Insere a peça na tabela de itens da OS
            sql_item = """
                INSERT INTO itens_os (os_id, descricao, quantidade, valor_unitario) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_item, (os_id, produto['nome'], quantidade, produto['preco_venda']))
            
            # 3. Atualiza o Valor Total Geral da OS
            valor_item = quantidade * float(produto['preco_venda'])
            cursor.execute("UPDATE servicos SET valor_total_geral = valor_total_geral + %s WHERE id = %s", (valor_item, os_id))
            
            conexao.commit()
            flash('Peça adicionada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao adicionar peça: {e}', 'danger')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('detalhes_os', id=os_id))

@app.route('/os/add_servico/<int:os_id>', methods=['POST'])
def adicionar_servico_detalhado(os_id): # Nome alterado para evitar o AssertionError
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        # 1. Captura os dados do formulário
        descricao = request.form.get('descricao')
        horas = float(request.form.get('horas') or 1)
        # Trata a vírgula caso o usuário digite 10,50
        valor_raw = request.form.get('valor', '0').replace(',', '.')
        valor_hora = float(valor_raw)
        
        # 2. Insere na tabela de serviços detalhados
        # Certifique-se que o nome da tabela no banco é 'servicos_detalhados'
        sql_insert = "INSERT INTO servicos_detalhados (os_id, descricao, horas, valor_hora) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_insert, (os_id, descricao, horas, valor_hora))
        
        # 3. ATUALIZA O TOTAL DA OS (Soma o novo serviço ao valor_total_geral)
        subtotal = horas * valor_hora
        sql_update_total = "UPDATE servicos SET valor_total_geral = valor_total_geral + %s WHERE id = %s"
        cursor.execute(sql_update_total, (subtotal, os_id))
        
        conexao.commit()
        flash('Serviço adicionado com sucesso!', 'success')
        
    except Exception as e:
        print(f"Erro ao adicionar serviço: {e}")
        flash(f'Erro ao adicionar serviço: {e}', 'danger')
    finally:
        cursor.close()
        conexao.close()
        
    return redirect(url_for('detalhes_os', id=os_id))


# Exemplo de como deve ficar sua rota de detalhes corrigida:
@app.route('/detalhes_os/<int:id>')
def detalhes_os(id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        # Busca a OS
        cursor.execute("SELECT s.*, c.nome as cliente_nome, v.modelo as veiculo_modelo, v.placa FROM servicos s JOIN clientes c ON s.cliente_id = c.id JOIN veiculos v ON s.veiculo_id = v.id WHERE s.id = %s", (id,))
        os_data = cursor.fetchone()

        # Busca ITENS PARA O MODAL (Puxando das tabelas que criamos acima)
        cursor.execute("SELECT * FROM produtos ORDER BY nome")
        produtos = cursor.fetchall()

        cursor.execute("SELECT * FROM servicos_lista ORDER BY nome")
        servicos_base = cursor.fetchall()

        # Busca itens JÁ LANÇADOS nesta OS para mostrar na tabela da página
        cursor.execute("SELECT * FROM itens_os WHERE os_id = %s", (id,))
        pecas_na_os = cursor.fetchall()

        return render_template('detalhes_os.html', 
                               os=os_data, 
                               produtos_estoque=produtos, 
                               servicos_base=servicos_base,
                               pecas=pecas_na_os)
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



# Rota para EXIBIR a lista e também RECEBER o formulário (POST)
@app.route('/estoque', methods=['GET', 'POST'])
def estoque_lista():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            # Estes nomes vêm do 'name' que está no seu HTML acima
            nome = request.form.get('peca')
            qtd = request.form.get('quantidade')
            valor = request.form.get('valor_venda')

            # Salva no banco (Certifique-se de que as colunas no MySQL são essas)
            sql = "INSERT INTO estoque (nome, quantidade_estoque, valor_venda) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nome, qtd, valor))
            conexao.commit()
            
            return redirect(url_for('estoque'))

        # Bloco GET (Listagem)
        cursor.execute("SELECT * FROM estoque ORDER BY nome ASC")
        dados = cursor.fetchall()
        return render_template('estoque.html', estoque=dados)
    finally:
        cursor.close()
        conexao.close()



# Rota para EXCLUIR
@app.route('/estoque/excluir/<int:id>')
def excluir_estoque(id): # Nome único 2
    conexao = conectar_banco()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM estoque WHERE id = %s", (id,))
        conexao.commit()
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('estoque'))

@app.route('/add_servico_os/<int:os_id>', methods=['POST'])
def add_servico_os(os_id):
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    try:
        servico_id = request.form.get('servico_id')
        horas = float(request.form.get('horas') or 1)

        # 1. Busca os detalhes do serviço na lista base
        cursor.execute("SELECT nome, preco FROM servicos_lista WHERE id = %s", (servico_id,))
        servico = cursor.fetchone()

        if servico:
            # 2. Insere o serviço na tabela de serviços detalhados da OS
            sql_serv = """
                INSERT INTO servicos_detalhados (os_id, descricao, horas, valor_hora) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_serv, (os_id, servico['nome'], horas, servico['preco']))
            
            # 3. Atualiza o Valor Total Geral da OS
            valor_servico = horas * float(servico['preco'])
            cursor.execute("UPDATE servicos SET valor_total_geral = valor_total_geral + %s WHERE id = %s", (valor_servico, os_id))
            
            conexao.commit()
            flash('Serviço registrado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao registrar serviço: {e}', 'danger')
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for('detalhes_os', id=os_id))




# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)