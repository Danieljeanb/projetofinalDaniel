CREATE DATABASE IF NOT EXISTS oficina;
USE oficina;

-- 1. Tabela de Usuários (Administradores da Oficina)
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    documento VARCHAR(20),
    endereco TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    documento VARCHAR(20), -- CPF ou CNPJ
    endereco TEXT,
    observacoes TEXT,
    ativo BOOLEAN DEFAULT TRUE
);

-- 3. Tabela de Veículos
CREATE TABLE veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    ano INT,
    placa VARCHAR(10) UNIQUE NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- 4. Tabela de Mecânicos
CREATE TABLE mecanicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especialidade VARCHAR(50),
    telefone VARCHAR(20),
    ativo BOOLEAN DEFAULT TRUE
);

-- 5. Tabela de Peças (Estoque)
CREATE TABLE pecas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(50),
    quantidade_estoque INT DEFAULT 0,
    custo DECIMAL(10,2),
    preco_venda DECIMAL(10,2),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabela de Ordens de Serviço (OS)
CREATE TABLE ordens_servico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    mecanico_id INT,
    data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('ABERTA', 'EM_ANDAMENTO', 'AGUARDANDO_PEÇAS', 'CONCLUÍDA', 'CANCELADA') DEFAULT 'ABERTA',
    problema_relatado TEXT,
    diagnostico TEXT,
    valor_total DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id)
);

-- 7. Tabela de Itens da OS (Peças e Serviços vinculados)
CREATE TABLE os_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_id INT NOT NULL,
    peca_id INT, -- Nulo se for um serviço manual
    descricao VARCHAR(255),
    tipo ENUM('PEÇA', 'SERVIÇO') NOT NULL,
    quantidade INT DEFAULT 1,
    valor_unitario DECIMAL(10,2),
    valor_total DECIMAL(10,2),
    FOREIGN KEY (os_id) REFERENCES ordens_servico(id),
    FOREIGN KEY (peca_id) REFERENCES pecas(id)
);