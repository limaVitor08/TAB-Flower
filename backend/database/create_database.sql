-- =====================================================================
-- PROJETO TAB-FLOWER
-- Sistema de Gestao Documental e Processual para Escritório de Advocacia
--
-- Arquivo.....: backend/database/create_database.sql
-- SGBD........: MySQL 8.0 (WAMP Server / MySQL Workbench)
-- Equipe......: Gabriel Mazzega, Gabriel Almeida, Gabriel Fernandes,
--               Vitor Papini, Nnamdi Delfino
-- Disciplina..: Projeto de Software - Prof. Gleison Brito
--
-- COMO EXECUTAR:
--   1. Abra o MySQL Workbench e conecte no servidor local (WAMP).
--   2. Abra este arquivo (File > Open SQL Script).
--   3. Execute o script inteiro (raio amarelo / Ctrl+Shift+Enter).
--   4. Atualize a lista de schemas para visualizar o banco "tabflower".
-- =====================================================================


-- =====================================================================
-- 1. Criação DO BANCO
-- =====================================================================

DROP DATABASE IF EXISTS tabflower;

CREATE DATABASE tabflower
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE tabflower;


-- =====================================================================
-- 2. MODULO DE Usuários E Permissões
-- =====================================================================

-- ---------------------------------------------------------------------
-- perfil
-- Define o nível de permissão do usuário dentro do sistema.
-- Usado pela Funcionalidade 20 (Restricao de Exclusão): apenas o perfil
-- Admin pode excluir documentos em definitivo.
-- ---------------------------------------------------------------------
CREATE TABLE perfil (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(50)  NOT NULL,
    descricao       VARCHAR(150) NULL,
    pode_excluir    BOOLEAN      NOT NULL DEFAULT FALSE,
    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_perfil_nome UNIQUE (nome)
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- usuário
-- Funcionarios do escritório que acessam o sistema.
-- Os usuários de perfil "Advogado" também são os responsaveis pelos
-- processos e os destinatarios das notificações (Funcionalidade 17).
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(120) NOT NULL,
    email           VARCHAR(120) NOT NULL,
    senha_hash      VARCHAR(255) NOT NULL,
    perfil_id       INT          NOT NULL,
    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME     NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_usuario_email  UNIQUE (email),
    CONSTRAINT fk_usuario_perfil FOREIGN KEY (perfil_id)
        REFERENCES perfil (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE INDEX ix_usuario_nome  ON usuario (nome);
CREATE INDEX ix_usuario_ativo ON usuario (ativo);


-- =====================================================================
-- 3. MODULO DE CLIENTES
-- =====================================================================

-- ---------------------------------------------------------------------
-- cliente
-- Pessoa física ou jurídica atendida pelo escritório.
--
-- Funcionalidade 04 (Validação de Documento): o formato do CPF/CNPJ e
--   validado na aplicação antes da inserção.
-- Funcionalidade 05 (Bloqueio de Duplicidade): a restricao UNIQUE em
--   "documento" garante no banco que o mesmo cliente não seja cadastrado
--   duas vezes, mesmo que a validação da aplicação falhe.
-- Funcionalidade 08 (Geração de Diretórios): "caminho_pasta" guarda a
--   estrutura de pastas criada automaticamente no cadastro.
-- ---------------------------------------------------------------------
CREATE TABLE cliente (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    tipo_pessoa     ENUM('F', 'J') NOT NULL,
    nome            VARCHAR(150)   NOT NULL,
    documento       VARCHAR(14)    NOT NULL COMMENT 'CPF ou CNPJ somente numeros',
    email           VARCHAR(120)   NULL,
    telefone        VARCHAR(20)    NULL,
    endereco        VARCHAR(200)   NULL,
    cidade          VARCHAR(80)    NULL,
    estado          CHAR(2)        NULL,
    caminho_pasta   VARCHAR(255)   NULL,
    observacao      TEXT           NULL,
    ativo           BOOLEAN        NOT NULL DEFAULT TRUE,
    importacao_id   INT            NULL COMMENT 'Preenchido quando o registro veio de carga de legado',
    criado_por      INT            NULL,
    criado_em       DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME       NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_cliente_documento UNIQUE (documento),
    CONSTRAINT fk_cliente_usuario   FOREIGN KEY (criado_por)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB;

-- Funcionalidade 01 (Busca por Nome) e 02 (Busca por Documento)
CREATE INDEX ix_cliente_nome  ON cliente (nome);
CREATE INDEX ix_cliente_ativo ON cliente (ativo);


-- =====================================================================
-- 4. MODULO DE PROCESSOS
-- =====================================================================

-- ---------------------------------------------------------------------
-- tipo_processo
-- Natureza da ação judicial (Trabalhista, Civel, Familia...).
-- E a chave da Funcionalidade 13 (Configuração de Checklist): cada tipo
-- possui sua própria lista de documentos obrigatórios.
-- ---------------------------------------------------------------------
CREATE TABLE tipo_processo (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(80)  NOT NULL,
    descricao       VARCHAR(200) NULL,
    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_tipo_processo_nome UNIQUE (nome)
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- status_processo
-- Fases do andamento processual, configuraveis pelo escritório.
-- Funcionalidade 07 (Atualizacao de Status).
-- ---------------------------------------------------------------------
CREATE TABLE status_processo (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(60) NOT NULL,
    descricao       VARCHAR(200) NULL,
    cor_hex         CHAR(7)     NOT NULL DEFAULT '#6B7280',
    ordem           INT         NOT NULL DEFAULT 0,
    is_final        BOOLEAN     NOT NULL DEFAULT FALSE,
    ativo           BOOLEAN     NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_status_processo_nome UNIQUE (nome)
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- marcador
-- Etiquetas visuais fixas do sistema (Urgente, Prioridade...).
-- Funcionalidades 14 (Marcadores Visuais) e 15 (Filtros de Prioridade).
-- ---------------------------------------------------------------------
CREATE TABLE marcador (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(40) NOT NULL,
    cor_hex         CHAR(7)     NOT NULL DEFAULT '#6B7280',
    peso            INT         NOT NULL DEFAULT 0 COMMENT 'Quanto maior, mais urgente',

    CONSTRAINT uq_marcador_nome UNIQUE (nome)
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- processo
-- Ação judicial vinculada a um cliente e a um advogado responsavel.
--
-- Funcionalidade 03 (Busca por Processo): índice em numero_processo.
-- Funcionalidade 06 (Painel Central de Gestao): tabela principal do painel.
-- Funcionalidade 17 (Direcionamento Automático): "advogado_id" define
--   quem recebe a notificação quando um documento e anexado.
-- ---------------------------------------------------------------------
CREATE TABLE processo (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    numero_processo     VARCHAR(30)  NOT NULL COMMENT 'Numero unico da acao judicial',
    titulo              VARCHAR(150) NOT NULL,
    descricao           TEXT         NULL,
    cliente_id          INT          NOT NULL,
    advogado_id         INT          NOT NULL,
    tipo_processo_id    INT          NOT NULL,
    status_id           INT          NOT NULL,
    comarca             VARCHAR(100) NULL,
    valor_causa         DECIMAL(12,2) NULL,
    data_abertura       DATE         NOT NULL,
    prazo_final         DATE         NULL,
    ativo               BOOLEAN      NOT NULL DEFAULT TRUE,
    importacao_id       INT          NULL COMMENT 'Preenchido quando o registro veio de carga de legado',
    criado_em           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em       DATETIME     NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_processo_numero UNIQUE (numero_processo),

    CONSTRAINT fk_processo_cliente FOREIGN KEY (cliente_id)
        REFERENCES cliente (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_processo_advogado FOREIGN KEY (advogado_id)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_processo_tipo FOREIGN KEY (tipo_processo_id)
        REFERENCES tipo_processo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_processo_status FOREIGN KEY (status_id)
        REFERENCES status_processo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE INDEX ix_processo_cliente  ON processo (cliente_id);
CREATE INDEX ix_processo_advogado ON processo (advogado_id);
CREATE INDEX ix_processo_status   ON processo (status_id);
CREATE INDEX ix_processo_prazo    ON processo (prazo_final);


-- ---------------------------------------------------------------------
-- processo_marcador
-- Relacionamento N:N entre processo e marcador.
-- Um processo pode estar marcado como Urgente e Prioridade ao mesmo tempo.
-- ---------------------------------------------------------------------
CREATE TABLE processo_marcador (
    processo_id     INT      NOT NULL,
    marcador_id     INT      NOT NULL,
    aplicado_por    INT      NULL,
    aplicado_em     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (processo_id, marcador_id),

    CONSTRAINT fk_procmarc_processo FOREIGN KEY (processo_id)
        REFERENCES processo (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_procmarc_marcador FOREIGN KEY (marcador_id)
        REFERENCES marcador (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_procmarc_usuario FOREIGN KEY (aplicado_por)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- historico_status
-- Registra cada mudanca de fase do processo.
-- Permite responder "ha quanto tempo o processo esta nesta fase" e gerar
-- os relatórios de produtividade citados nas entrevistas (Etapa 3).
-- ---------------------------------------------------------------------
CREATE TABLE historico_status (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    processo_id         INT      NOT NULL,
    status_anterior_id  INT      NULL,
    status_novo_id      INT      NOT NULL,
    usuario_id          INT      NULL,
    observacao          VARCHAR(255) NULL,
    criado_em           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_hist_processo FOREIGN KEY (processo_id)
        REFERENCES processo (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_hist_status_ant FOREIGN KEY (status_anterior_id)
        REFERENCES status_processo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_hist_status_novo FOREIGN KEY (status_novo_id)
        REFERENCES status_processo (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_hist_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB;

CREATE INDEX ix_hist_processo ON historico_status (processo_id);


-- =====================================================================
-- 5. MODULO DE DOCUMENTOS E AUTOMACAO DE ARQUIVOS
-- =====================================================================

-- ---------------------------------------------------------------------
-- categoria_documento
-- Classificação jurídica do arquivo (Procuracao, RG, Contrato...).
--
-- Funcionalidade 09 (Identificação de Categoria).
-- Funcionalidade 10 (Renomeação Automática): a coluna "sigla" e usada
--   para montar o nome padronizado do arquivo.
--   Ex.: PROC_JOAO-DA-SILVA_2026-08-06.pdf
-- ---------------------------------------------------------------------
CREATE TABLE categoria_documento (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    nome            VARCHAR(80)  NOT NULL,
    sigla           VARCHAR(10)  NOT NULL COMMENT 'Prefixo usado na renomeacao automatica',
    descricao       VARCHAR(200) NULL,
    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_categoria_nome  UNIQUE (nome),
    CONSTRAINT uq_categoria_sigla UNIQUE (sigla)
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- documento
-- Arquivo digitalizado vinculado a um cliente e, opcionalmente, a um
-- processo. O PDF fica no servidor de arquivos; o banco guarda o caminho.
--
-- Funcionalidade 10 (Renomeação Automática): "nome_original" preserva o
--   nome enviado e "nome_padronizado" guarda o nome gerado pelo sistema.
-- Funcionalidade 20 (Restricao de Exclusão): a exclusão e Lógica. O
--   registro nunca sai da tabela; apenas "excluido" vira TRUE e o
--   responsavel fica gravado em "excluido_por".
-- ---------------------------------------------------------------------
CREATE TABLE documento (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id          INT          NOT NULL,
    processo_id         INT          NULL,
    categoria_id        INT          NOT NULL,
    nome_original       VARCHAR(200) NOT NULL,
    nome_padronizado    VARCHAR(200) NOT NULL,
    caminho_arquivo     VARCHAR(255) NOT NULL,
    extensao            VARCHAR(10)  NOT NULL DEFAULT 'pdf',
    tamanho_kb          INT          NULL,
    enviado_por         INT          NULL,
    criado_em           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    excluido            BOOLEAN      NOT NULL DEFAULT FALSE,
    excluido_em         DATETIME     NULL,
    excluido_por        INT          NULL,

    CONSTRAINT uq_documento_caminho UNIQUE (caminho_arquivo),

    CONSTRAINT fk_documento_cliente FOREIGN KEY (cliente_id)
        REFERENCES cliente (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_documento_processo FOREIGN KEY (processo_id)
        REFERENCES processo (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_documento_categoria FOREIGN KEY (categoria_id)
        REFERENCES categoria_documento (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_documento_enviado_por FOREIGN KEY (enviado_por)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_documento_excluido_por FOREIGN KEY (excluido_por)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB;

CREATE INDEX ix_documento_cliente  ON documento (cliente_id);
CREATE INDEX ix_documento_processo ON documento (processo_id);
CREATE INDEX ix_documento_excluido ON documento (excluido);


-- =====================================================================
-- 6. MODULO DE CHECKLIST E Pendências
-- =====================================================================

-- ---------------------------------------------------------------------
-- checklist_modelo
-- Lista de documentos exigidos para cada tipo de processo.
-- E o "molde" configuravel pela Funcionalidade 13.
-- ---------------------------------------------------------------------
CREATE TABLE checklist_modelo (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    tipo_processo_id    INT     NOT NULL,
    categoria_id        INT     NOT NULL,
    obrigatorio         BOOLEAN NOT NULL DEFAULT TRUE,
    ordem               INT     NOT NULL DEFAULT 0,

    CONSTRAINT uq_checklist_modelo UNIQUE (tipo_processo_id, categoria_id),

    CONSTRAINT fk_chkmodelo_tipo FOREIGN KEY (tipo_processo_id)
        REFERENCES tipo_processo (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_chkmodelo_categoria FOREIGN KEY (categoria_id)
        REFERENCES categoria_documento (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- checklist_processo
-- Copia do modelo aplicada a um processo específico no momento em que
-- ele e criado. Cada linha representa um item do checklist digital.
--
-- Funcionalidade 11 (Checklist Obrigatório).
-- Funcionalidade 12 (Mapeamento de Pendências): itens com entregue =
--   FALSE são exatamente as pendências exibidas na tela.
-- ---------------------------------------------------------------------
CREATE TABLE checklist_processo (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    processo_id     INT      NOT NULL,
    categoria_id    INT      NOT NULL,
    documento_id    INT      NULL COMMENT 'Documento que atendeu a exigencia',
    obrigatorio     BOOLEAN  NOT NULL DEFAULT TRUE,
    entregue        BOOLEAN  NOT NULL DEFAULT FALSE,
    entregue_em     DATETIME NULL,
    observacao      VARCHAR(200) NULL,

    CONSTRAINT uq_checklist_processo UNIQUE (processo_id, categoria_id),

    CONSTRAINT fk_chkproc_processo FOREIGN KEY (processo_id)
        REFERENCES processo (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_chkproc_categoria FOREIGN KEY (categoria_id)
        REFERENCES categoria_documento (id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_chkproc_documento FOREIGN KEY (documento_id)
        REFERENCES documento (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB;

CREATE INDEX ix_chkproc_entregue ON checklist_processo (processo_id, entregue);


-- =====================================================================
-- 7. MODULO DE Integração E Comunicação
-- =====================================================================

-- ---------------------------------------------------------------------
-- notificação
-- Alertas internos entregues ao advogado responsavel.
--
-- Funcionalidade 16 (Disparo de Notificações).
-- Funcionalidade 17 (Direcionamento Automático): ao anexar um documento,
--   o sistema cruza o documento com o advogado_id do processo e gera
--   automaticamente uma linha nesta tabela.
-- ---------------------------------------------------------------------
CREATE TABLE notificacao (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_destino_id  INT          NOT NULL,
    processo_id         INT          NULL,
    documento_id        INT          NULL,
    titulo              VARCHAR(120) NOT NULL,
    mensagem            VARCHAR(255) NOT NULL,
    tipo                ENUM('DOCUMENTO', 'PRAZO', 'STATUS', 'GERAL')
                        NOT NULL DEFAULT 'GERAL',
    lida                BOOLEAN      NOT NULL DEFAULT FALSE,
    lida_em             DATETIME     NULL,
    criado_em           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_notif_usuario FOREIGN KEY (usuario_destino_id)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_notif_processo FOREIGN KEY (processo_id)
        REFERENCES processo (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_notif_documento FOREIGN KEY (documento_id)
        REFERENCES documento (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE = InnoDB;

CREATE INDEX ix_notif_destino ON notificacao (usuario_destino_id, lida);


-- ---------------------------------------------------------------------
-- importacao_lote
-- Controle das cargas de dados legados vindos das planilhas antigas.
--
-- Funcionalidade 18 (Importação em Lote).
-- Funcionalidade 19 (Organização de Legado): guarda o resultado de cada
--   importação para que o usuário saiba o que entrou e o que falhou.
-- ---------------------------------------------------------------------
CREATE TABLE importacao_lote (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id          INT          NULL,
    nome_arquivo        VARCHAR(200) NOT NULL,
    total_registros     INT          NOT NULL DEFAULT 0,
    total_sucesso       INT          NOT NULL DEFAULT 0,
    total_erro          INT          NOT NULL DEFAULT 0,
    situacao            ENUM('PROCESSANDO', 'CONCLUIDA', 'FALHOU')
                        NOT NULL DEFAULT 'PROCESSANDO',
    log_erros           TEXT         NULL,
    criado_em           DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finalizado_em       DATETIME     NULL,

    CONSTRAINT fk_importacao_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB;


-- ---------------------------------------------------------------------
-- Vinculo dos registros legados com a importação que os originou.
-- Feito por ALTER TABLE porque cliente e processo são criados antes de
-- importacao_lote, e a FK exige que a tabela referenciada já exista.
--
-- Funcionalidade 19 (Organização de Legado): permite responder "quais
-- clientes entraram na planilha importada em tal dia" e desfazer uma
-- carga que veio errada, sem tocar nos cadastros feitos manualmente.
-- ---------------------------------------------------------------------
ALTER TABLE cliente
    ADD CONSTRAINT fk_cliente_importacao FOREIGN KEY (importacao_id)
        REFERENCES importacao_lote (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL;

ALTER TABLE processo
    ADD CONSTRAINT fk_processo_importacao FOREIGN KEY (importacao_id)
        REFERENCES importacao_lote (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL;


-- =====================================================================
-- 8. MODULO DE SEGURANCA E AUDITORIA
-- =====================================================================

-- ---------------------------------------------------------------------
-- log_auditoria
-- Rastreabilidade de todas as ações sensiveis do sistema.
-- Responde a dor levantada na entrevista: "o log de alterações e
-- inexistente, entao quando algo some, não sabemos quem moveu ou apagou".
-- Complementa a Funcionalidade 20.
-- ---------------------------------------------------------------------
CREATE TABLE log_auditoria (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id      INT          NULL,
    acao            ENUM('CRIAR', 'ATUALIZAR', 'EXCLUIR', 'RESTAURAR', 'LOGIN', 'DOWNLOAD')
                    NOT NULL,
    entidade        VARCHAR(50)  NOT NULL COMMENT 'Nome da tabela afetada',
    entidade_id     INT          NULL     COMMENT 'ID do registro afetado',
    descricao       VARCHAR(255) NULL,
    criado_em       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_log_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuario (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE = InnoDB;

CREATE INDEX ix_log_entidade ON log_auditoria (entidade, entidade_id);
CREATE INDEX ix_log_data     ON log_auditoria (criado_em);


-- =====================================================================
-- 9. CARGA INICIAL (DADOS FIXOS DO SISTEMA)
-- =====================================================================

-- Perfis: apenas o Admin pode excluir documentos (Funcionalidade 20)
INSERT INTO perfil (nome, descricao, pode_excluir) VALUES
    ('Admin',      'Acesso total ao sistema, incluindo exclusão de documentos', TRUE),
    ('Advogado',   'Responsável pelos processos e destinatário das notificações', FALSE),
    ('Secretária', 'Cadastro de clientes, processos e anexo de documentos',       FALSE);

-- Status configuraveis do processo
INSERT INTO status_processo (nome, descricao, cor_hex, ordem, is_final) VALUES
    ('Aguardando documentos', 'Checklist ainda possui pendências',       '#F59E0B', 1, FALSE),
    ('Pronto para protocolo',  'Documentação completa e conferida',      '#3B82F6', 2, FALSE),
    ('Protocolado',            'Ação ajuizada e aguardando distribuição', '#8B5CF6', 3, FALSE),
    ('Em andamento',           'Processo em tramitação no tribunal',      '#10B981', 4, FALSE),
    ('Suspenso',               'Tramitação temporariamente interrompida', '#6B7280', 5, FALSE),
    ('Arquivado',              'Processo encerrado e arquivado',          '#374151', 6, TRUE);

-- Marcadores visuais fixos do sistema
INSERT INTO marcador (nome, cor_hex, peso) VALUES
    ('Urgente',     '#DC2626', 3),
    ('Prioridade',  '#F97316', 2),
    ('Prazo curto', '#EAB308', 1);

-- Tipos de processo iniciais
INSERT INTO tipo_processo (nome, descricao) VALUES
    ('Trabalhista',    'Ações relativas a relações de trabalho'),
    ('Cível',          'Ações de indenização, cobrança e contratos'),
    ('Família',        'Divórcio, guarda, pensão alimentícia'),
    ('Previdenciário', 'Benefícios e aposentadorias junto ao INSS'),
    ('Consumidor',     'Relações de consumo');

-- Categorias de documento (a sigla alimenta a renomeação automática)
INSERT INTO categoria_documento (nome, sigla, descricao) VALUES
    ('Procuração',              'PROC', 'Instrumento de mandato assinado pelo cliente'),
    ('Documento de identidade', 'RG',   'RG, CNH ou documento equivalente'),
    ('CPF',                     'CPF',  'Comprovante de inscricao no CPF'),
    ('Comprovante de endereço', 'ENDR', 'Conta de consumo ou equivalente'),
    ('Contrato',                'CTRT', 'Contrato firmado entre as partes'),
    ('Carteira de trabalho',    'CTPS', 'CTPS física ou digital'),
    ('Petição inicial',         'PETI', 'Peça de abertura da ação'),
    ('Certidão',                'CERT', 'Certidões em geral'),
    ('Laudo médico',            'LAUD', 'Laudos e relatórios médicos'),
    ('Comprovante de pagamento','COMP', 'Recibos e comprovantes financeiros');

-- Modelos de checklist por tipo de processo (Funcionalidade 13)
-- Trabalhista
INSERT INTO checklist_modelo (tipo_processo_id, categoria_id, obrigatorio, ordem) VALUES
    (1, 1, TRUE, 1),
    (1, 2, TRUE, 2),
    (1, 4, TRUE, 3),
    (1, 6, TRUE, 4);
-- Civel
INSERT INTO checklist_modelo (tipo_processo_id, categoria_id, obrigatorio, ordem) VALUES
    (2, 1, TRUE,  1),
    (2, 2, TRUE,  2),
    (2, 4, TRUE,  3),
    (2, 5, TRUE,  4),
    (2, 10, FALSE, 5);
-- Familia
INSERT INTO checklist_modelo (tipo_processo_id, categoria_id, obrigatorio, ordem) VALUES
    (3, 1, TRUE, 1),
    (3, 2, TRUE, 2),
    (3, 4, TRUE, 3),
    (3, 8, TRUE, 4);
-- Previdenciario
INSERT INTO checklist_modelo (tipo_processo_id, categoria_id, obrigatorio, ordem) VALUES
    (4, 1, TRUE,  1),
    (4, 2, TRUE,  2),
    (4, 3, TRUE,  3),
    (4, 9, TRUE,  4),
    (4, 6, FALSE, 5);
-- Consumidor
INSERT INTO checklist_modelo (tipo_processo_id, categoria_id, obrigatorio, ordem) VALUES
    (5, 1, TRUE,  1),
    (5, 2, TRUE,  2),
    (5, 5, TRUE,  3),
    (5, 10, TRUE, 4);

-- Usuário administrador inicial
-- Atenção: a senha abaixo e um hash de exemplo. Ela será regerada pela
-- aplicação Flask no primeiro cadastro real de usuário.
INSERT INTO usuario (nome, email, senha_hash, perfil_id) VALUES
    ('Administrador', 'admin@tabflower.com', 'ALTERAR_NO_PRIMEIRO_ACESSO', 1);


-- =====================================================================
-- FIM DO SCRIPT
-- =====================================================================
