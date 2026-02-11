CREATE DATABASE sistema_oficina;
USE sistema_oficina;

-- 1. Usuários do Sistema
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    nivel_acesso ENUM('admin', 'recepcao', 'mecanico') DEFAULT 'recepcao'
);

-- 2. Clientes
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf_cnpj VARCHAR(20) UNIQUE NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100),
    endereco TEXT
);

-- 3. Veículos (Relacionado ao Cliente)
CREATE TABLE veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    placa VARCHAR(10) UNIQUE NOT NULL,
    modelo VARCHAR(50),
    marca VARCHAR(50),
    ano INT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- 4. Mecânicos
CREATE TABLE mecanicos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especialidade VARCHAR(50),
    comissao_percentual DECIMAL(5,2) DEFAULT 0.00
);

-- 5. Peças (Estoque)
CREATE TABLE pecas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    valor_venda DECIMAL(10,2) NOT NULL,
    estoque_atual INT DEFAULT 0
);

-- 6. Ordens de Serviço (OS)
CREATE TABLE ordens_servico (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    veiculo_id INT NOT NULL,
    mecanico_id INT,
    data_abertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_conclusao DATETIME,
    status ENUM('ABERTA', 'EM ANDAMENTO', 'CONCLUÍDA', 'CANCELADA') DEFAULT 'ABERTA',
    valor_total DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id),
    FOREIGN KEY (mecanico_id) REFERENCES mecanicos(id)
);

-- 7. Itens da OS (Peças e Serviços)
CREATE TABLE os_itens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_id INT NOT NULL,
    peca_id INT, -- NULL se for apenas serviço
    descricao_servico VARCHAR(255), -- Preenchido se não for peça
    quantidade INT DEFAULT 1,
    valor_unitario DECIMAL(10,2) NOT NULL,
    tipo ENUM('PEÇA', 'SERVIÇO') NOT NULL,
    FOREIGN KEY (os_id) REFERENCES ordens_servico(id) ON DELETE CASCADE,
    FOREIGN KEY (peca_id) REFERENCES pecas(id)
);

-- 8. Pagamentos
CREATE TABLE pagamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    os_id INT NOT NULL,
    valor_pago DECIMAL(10,2) NOT NULL,
    metodo_pagamento ENUM('DINHEIRO', 'CARTAO', 'PIX'),
    data_pagamento DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (os_id) REFERENCES ordens_servico(id)
);

-- TRIGGER: Decrementar estoque automaticamente ao inserir peça na OS
DELIMITER //
CREATE TRIGGER tr_baixa_estoque AFTER INSERT ON os_itens
FOR EACH ROW
BEGIN
    IF NEW.tipo = 'PEÇA' AND NEW.peca_id IS NOT NULL THEN
        UPDATE pecas 
        SET estoque_atual = estoque_atual - NEW.quantidade
        WHERE id = NEW.peca_id;
    END IF;
END;
