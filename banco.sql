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

-- TRIGGER: Correção no fechamento
DELIMITER //
CREATE TRIGGER tr_baixa_estoque AFTER INSERT ON os_itens
FOR EACH ROW
BEGIN
    IF NEW.tipo = 'PEÇA' AND NEW.peca_id IS NOT NULL THEN
        UPDATE pecas 
        SET estoque_atual = estoque_atual - NEW.quantidade
        WHERE id = NEW.peca_id;
    END IF;
END // -- Adicione o // aqui
DELIMITER ; -- Adicione esta linha para voltar ao padrão ;


USE sistema_oficina;

-- 1. Inserir Usuários
INSERT INTO usuarios (nome, email, senha, nivel_acesso) VALUES 
('Admin Geral', 'admin@oficina.com', 'hash_senha_123', 'admin'),
('Recepcionista Ana', 'ana@oficina.com', 'hash_senha_456', 'recepcao');

-- 2. Inserir Clientes
INSERT INTO clientes (nome, cpf_cnpj, telefone, email, endereco) VALUES 
('João Silva', '123.456.789-00', '(11) 98888-7777', 'joao@email.com', 'Rua das Flores, 123'),
('Maria Oliveira', '987.654.321-11', '(11) 91111-2222', 'maria@email.com', 'Av. Central, 500');

-- 3. Inserir Veículos (ligados aos clientes acima)
INSERT INTO veiculos (cliente_id, placa, modelo, marca, ano) VALUES 
(1, 'ABC-1234', 'Civic', 'Honda', 2020),
(2, 'XYZ-9876', 'Onix', 'Chevrolet', 2022);

-- 4. Inserir Mecânicos
INSERT INTO mecanicos (nome, especialidade, comissao_percentual) VALUES 
('Roberto Carlos', 'Motores', 10.00),
('Marcos Souza', 'Suspensão e Freios', 8.50);

-- 5. Inserir Peças (Estoque inicial)
INSERT INTO pecas (nome, valor_venda, estoque_atual) VALUES 
('Filtro de Óleo', 45.90, 50),
('Pastilha de Freio', 120.00, 20),
('Óleo 5W30 (Litro)', 35.00, 100);

-- 6. Abrir uma Ordem de Serviço (OS)
-- Cliente 1, Veículo 1, Mecânico 1
INSERT INTO ordens_servico (cliente_id, veiculo_id, mecanico_id, status, valor_total) VALUES 
(1, 1, 1, 'CONCLUÍDA', 245.90);

-- 7. Adicionar Itens na OS (Peças e Serviços)
-- Nota: Ao inserir a 'PEÇA' 1, a Trigger que criamos reduzirá o estoque de 50 para 49.
INSERT INTO os_itens (os_id, peca_id, descricao_servico, quantidade, valor_unitario, tipo) VALUES 
(1, 1, NULL, 1, 45.90, 'PEÇA'),           -- Peça (Filtro)
(1, NULL, 'Troca de Óleo e Filtro', 1, 200.00, 'SERVIÇO'); -- Mão de obra

-- 8. Registrar Pagamento
INSERT INTO pagamentos (os_id, valor_pago, metodo_pagamento) VALUES 
(1, 245.90, 'PIX');

SELECT 
    p.nome AS peca,
    SUM(oi.quantidade) AS total_vendido,
    SUM(oi.quantidade * oi.valor_unitario) AS faturamento_bruto,
    -- Supondo uma margem estimada ou buscando o valor unitário da tabela de peças
    COUNT(DISTINCT oi.os_id) AS total_ordens_servico,
    DATE_FORMAT(os.data_conclusao, '%d/%m/%Y') AS ultima_venda
FROM os_itens oi
JOIN pecas p ON oi.peca_id = p.id
JOIN ordens_servico os ON oi.os_id = os.id
WHERE oi.tipo = 'PEÇA' 
  AND os.status = 'CONCLUÍDA'
GROUP BY p.id, p.nome
ORDER BY faturamento_bruto DESC;
