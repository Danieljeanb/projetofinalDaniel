DROP DATABASE IF EXISTS sistema_oficina;
CREATE DATABASE sistema_oficina;
USE sistema_oficina;

-- 1. Usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    documento VARCHAR(20),
    telefone VARCHAR(20),
    email VARCHAR(100),
    endereco TEXT,
    observacoes TEXT,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Veículos
CREATE TABLE veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    ano INT,
    placa VARCHAR(10) UNIQUE NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- 4. Mecânicos
CREATE TABLE mecanicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especialidade VARCHAR(50),
    ativo BOOLEAN DEFAULT TRUE
);

-- 5. Estoque (Renomeado para bater com itens_os)
CREATE TABLE estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    peca VARCHAR(100) NOT NULL,        -- Mudado de 'nome' para 'peca'
    quantidade INT DEFAULT 0,          -- Mudado de 'quantidade_estoque' para 'quantidade'
    codigo VARCHAR(50) UNIQUE,
    estoque_minimo INT DEFAULT 5,
    valor_custo DECIMAL(10,2),
    valor_venda DECIMAL(10,2) DEFAULT 0.00 -- Adicionado valor padrão para não dar erro
);


-- 6. Ordens de Serviço (Nome padronizado para 'servicos')
CREATE TABLE servicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    mecanico_id INT,
    data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_conclusao DATETIME,
    status ENUM('ABERTA', 'EM_ANDAMENTO', 'AGUARDANDO_PECAS', 'CONCLUIDA', 'CANCELADA') DEFAULT 'ABERTA',
    problema_relatado TEXT,
    diagnostico_oficina TEXT,
    observacoes TEXT,
    valor_total_pecas DECIMAL(10,2) DEFAULT 0.00,
    valor_total_servicos DECIMAL(10,2) DEFAULT 0.00,
    valor_total_geral DECIMAL(10,2) DEFAULT 0.00,
    paga BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id)
);

-- 7. Itens da OS (Corrigido para apontar para 'servicos')
CREATE TABLE itens_os (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_id INT NOT NULL,
    produto_id INT, 
    descricao VARCHAR(255) NOT NULL,
    tipo ENUM('PECA', 'SERVICO') NOT NULL,
    quantidade INT DEFAULT 1,
    valor_unitario DECIMAL(10,2) NOT NULL,
    valor_total_item DECIMAL(10,2) AS (quantidade * valor_unitario) STORED,
    FOREIGN KEY (os_id) REFERENCES servicos(id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos_estoque(id)
);

-- 8. Pagamentos (Corrigido para apontar para 'servicos')
CREATE TABLE pagamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_id INT NOT NULL,
    forma_pagamento ENUM('PIX', 'DINHEIRO', 'CARTAO_DEBITO', 'CARTAO_CREDITO') NOT NULL,
    valor_pago DECIMAL(10,2) NOT NULL,
    data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (os_id) REFERENCES servicos(id)
);