-- Criar banco de dados
DROP DATABASE IF EXISTS oficina;
CREATE DATABASE oficina;
USE oficina;

-- 1. Usuários
DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Clientes
DROP TABLE IF EXISTS clientes;
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),CREATE DATABASE IF NOT EXISTS minha_oficina;
USE minha_oficina;

-- 2. Tabela de Usuários (Login)
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);

-- 3. Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    documento VARCHAR(20),
    email VARCHAR(100),
    endereco TEXT
);

-- 4. Tabela de Veículos (Relacionada aos Clientes)
CREATE TABLE IF NOT EXISTS veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modelo VARCHAR(100) NOT NULL,
    placa VARCHAR(10) NOT NULL UNIQUE,
    cliente_id INT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- 5. Tabela de Ordens de Serviço (Referenciada na rota /item)
CREATE TABLE IF NOT EXISTS ordens_servico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    veiculo_id INT,
    descricao TEXT,
    status VARCHAR(50) DEFAULT 'Pendente',
    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id) ON DELETE CASCADE
);

-- 6. Tabela de Estoque (Aquela que gerou o erro inicial)
CREATE TABLE IF NOT EXISTS estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(100) NOT NULL,
    quantidade INT DEFAULT 0,
    preco DECIMAL(10, 2)
);

-- 7. Itens da OS (Para o formulário de "Peças utilizadas")
CREATE TABLE IF NOT EXISTS itens_os (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_id INT,
    descricao VARCHAR(255) NOT NULL,
    quantidade INT NOT NULL,
    valor_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (os_id) REFERENCES ordens_servico(id) ON DELETE CASCADE
);

-- 8. Serviços da OS (Para o formulário de "Serviços executados")
CREATE TABLE IF NOT EXISTS servicos_os (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_id INT,
    descricao VARCHAR(255) NOT NULL,
    horas DECIMAL(5, 2),
    valor_hora DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (os_id) REFERENCES ordens_servico(id) ON DELETE CASCADE
);
    documento VARCHAR(20),
    endereco TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Veículos
DROP TABLE IF EXISTS veiculos;
CREATE TABLE veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    placa VARCHAR(10) UNIQUE NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- 4. Ordens de Serviço
CREATE TABLE IF NOT EXISTS ordens_servico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    descricao TEXT,
    valor DECIMAL(10, 2),
    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);

-- 5. Estoque
DROP TABLE IF EXISTS estoque;
CREATE TABLE estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    peca VARCHAR(100) NOT NULL,
    quantidade INT DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);