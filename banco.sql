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
    email VARCHAR(100),
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