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
# CADASTRAR CLIENTE
@app.route('/add_cliente', methods=['POST'])
def add_clientes():
    dados = (request.form.get('nome'), request.form.get('telefone'), request.form.get('email'), 
             request.form.get('documento'), request.form.get('endereco'), request.form.get('obs'))
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO clientes (nome, telefone, email, documento, endereco, observacoes) 
                      VALUES (%s, %s, %s, %s, %s, %s)""", dados)
    conn.commit()
    conn.close()
    return redirect(url_for('clientes'))

# CADASTRAR VEÍCULO (VINCULADO AO CLIENTE)
@app.route('/add_veiculo', methods=['POST'])
def add_veiculos():
    dados = (request.form.get('modelo'), request.form.get('marca'), request.form.get('ano'), 
             request.form.get('placa'), request.form.get('cliente_id'))
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO veiculos (modelo, marca, ano, placa, cliente_id) VALUES (%s,%s,%s,%s,%s)", dados)
    conn.commit()
    conn.close()
    return redirect(url_for('veiculos'))

# GERENCIAR MECÂNICOS
@app.route('/mecânicos')
def mecanicos():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mecanicos")
    lista = cursor.fetchall()
    conn.close()
    return render_template('mecanicos.html', mecanicos=lista)

# CRIAR OS
@app.route('/add_os', methods=['POST'])
def add_os():
    dados = (request.form.get('cliente_id'), request.form.get('veiculo_id'), request.form.get('mecanico_id'),
             request.form.get('problema'), 'ABERTA')
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO ordens_servico (cliente_id, veiculo_id, mecanico_id, problema_relatado, status, data_abertura) 
                      VALUES (%s, %s, %s, %s, %s, NOW())""", dados)
    conn.commit()
    conn.close()
    return redirect(url_for('servicos'))

# ADICIONAR ITEM E BAIXAR ESTOQUE (REQUISITO 5 e 6)
@app.route('/add_item_os/<int:os_id>', methods=['POST'])
def add_item_os(os_id):
    tipo = request.form.get('tipo') # 'PEÇA' ou 'SERVIÇO'
    peca_id = request.form.get('peca_id') # Se for peça, pegamos o ID do estoque
    qtd = int(request.form.get('quantidade'))
    valor_un = float(request.form.get('valor_unitario'))
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Se for PEÇA, decrementa o estoque
    if tipo == 'PEÇA' and peca_id:
        cursor.execute("UPDATE estoque SET quantidade = quantidade - %s WHERE id = %s", (qtd, peca_id))
    
    # Insere o item na OS
    cursor.execute("""INSERT INTO itens_os (os_id, descricao, tipo, quantidade, valor_unitario) 
                      VALUES (%s, %s, %s, %s, %s)""", 
                   (os_id, request.form.get('descricao'), tipo, qtd, valor_un))
    
    # Atualiza valor total da OS
    cursor.execute("UPDATE ordens_servico SET valor = valor + (%s * %s) WHERE id = %s", (qtd, valor_un, os_id))
    
    conn.commit()
    conn.close()
    return redirect(url_for('detalhes_os', id=os_id))

# AVISO DE ESTOQUE BAIXO (REQUISITO 6)
@app.route('/estoque')
def estoque():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT *, (quantidade <= 3) as alerta_baixo FROM estoque")
    itens = cursor.fetchall()
    conn.close()
    return render_template('estoque.html', estoque=itens)

# REGISTRAR PAGAMENTO (REQUISITO 7)
@app.route('/pagar_os/<int:os_id>', methods=['POST'])
def pagar_os(os_id):
    forma = request.form.get('forma_pagamento')
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""UPDATE ordens_servico SET status = 'CONCLUÍDA', 
                      pago = 1, forma_pagamento = %s, data_pagamento = NOW() 
                      WHERE id = %s""", (forma, os_id))
    conn.commit()
    conn.close()
    return redirect(url_for('detalhes_os', id=os_id))
@app.route('/relatorios')
def relatorios():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)
    
    # OS Concluídas no mês
    cursor.execute("SELECT COUNT(*) as qtd, SUM(valor) as faturamento FROM ordens_servico WHERE status = 'CONCLUÍDA' AND MONTH(data_pagamento) = MONTH(CURRENT_DATE())")
    mes = cursor.fetchone()
    
    # Peças com estoque baixo (ex: menos de 5 unidades)
    cursor.execute("SELECT * FROM estoque WHERE quantidade < 5")
    baixos = cursor.fetchall()
    
    conn.close()
    return render_template('relatorios.html', mes=mes, baixos=baixos)






# ------------------- MAIN -------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)