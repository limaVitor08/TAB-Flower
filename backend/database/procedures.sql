-- =====================================================================
-- PROJETO TAB-FLOWER
-- Stored Procedures - Terceira Etapa
--
-- Arquivo.....: backend/database/procedures.sql
-- SGBD........: MySQL 8.0 (WAMP Server / MySQL Workbench)
--
-- Estas procedures concentram as consultas que extrapolam o CRUD:
-- filtros combinados, JOINs entre várias tabelas, ordenacoes e
-- agregacoes. Elas são chamadas exclusivamente pela camada Repository
-- do backend, nunca por Models ou Services diretamente.
--
-- COMO EXECUTAR:
--   1. Rode ANTES o create_database.sql (ele cria o banco e as tabelas).
--   2. Abra este arquivo no MySQL Workbench.
--   3. Execute o script inteiro (raio amarelo / Ctrl+Shift+Enter).
--   4. Confira em SCHEMAS > tabflower > Stored Procedures.
--
-- Rodar este arquivo mais de uma vez e seguro: cada procedure e
-- apagada antes de ser recriada.
-- =====================================================================

USE tabflower;

DELIMITER $$


-- =====================================================================
-- 1. sp_buscar_clientes_por_nome
--
-- Funcionalidade 01 - Busca por Nome.
--
-- Busca parcial e sem diferenciar maiusculas. Traz junto a contagem de
-- processos ativos de cada cliente, o que a secretaria precisa ver na
-- lista sem ter que abrir cliente por cliente.
--
-- Este JOIN com contagem e exatamente o tipo de consulta que não cabe
-- na Model: não e CRUD, e relatório.
-- =====================================================================

DROP PROCEDURE IF EXISTS sp_buscar_clientes_por_nome$$

CREATE PROCEDURE sp_buscar_clientes_por_nome(
    IN p_termo          VARCHAR(150),
    IN p_apenas_ativos  BOOLEAN
)
BEGIN
    SELECT
        c.id,
        c.tipo_pessoa,
        c.nome,
        c.documento,
        c.email,
        c.telefone,
        c.cidade,
        c.estado,
        c.caminho_pasta,
        c.ativo,
        COUNT(DISTINCT p.id) AS total_processos
    FROM cliente c
    LEFT JOIN processo p
        ON p.cliente_id = c.id
       AND p.ativo = TRUE
    WHERE c.nome LIKE CONCAT('%', p_termo, '%')
      AND (p_apenas_ativos = FALSE OR c.ativo = TRUE)
    GROUP BY
        c.id, c.tipo_pessoa, c.nome, c.documento, c.email,
        c.telefone, c.cidade, c.estado, c.caminho_pasta, c.ativo
    ORDER BY c.nome;
END$$


-- =====================================================================
-- 2. sp_buscar_processos
--
-- Funcionalidade 03 - Busca por Processo.
--
-- Busca combinada: o termo procura ao mesmo tempo no número da ação, no
-- título e no nome do cliente. Os filtros de status e advogado são
-- opcionais - passando NULL, o filtro e ignorado.
--
-- Junta cinco tabelas para devolver a linha já pronta para a tela, sem
-- o backend precisar de consultas extras.
-- =====================================================================

DROP PROCEDURE IF EXISTS sp_buscar_processos$$

CREATE PROCEDURE sp_buscar_processos(
    IN p_termo        VARCHAR(150),
    IN p_status_id    INT,
    IN p_advogado_id  INT,
    IN p_tipo_id      INT
)
BEGIN
    SELECT
        p.id,
        p.numero_processo,
        p.titulo,
        p.data_abertura,
        p.prazo_final,
        p.valor_causa,
        p.comarca,
        p.ativo,
        c.id            AS cliente_id,
        c.nome          AS cliente_nome,
        c.documento     AS cliente_documento,
        u.id            AS advogado_id,
        u.nome          AS advogado_nome,
        t.id            AS tipo_processo_id,
        t.nome          AS tipo_nome,
        s.id            AS status_id,
        s.nome          AS status_nome,
        s.cor_hex       AS status_cor
    FROM processo p
    INNER JOIN cliente         c ON c.id = p.cliente_id
    INNER JOIN usuario         u ON u.id = p.advogado_id
    INNER JOIN tipo_processo   t ON t.id = p.tipo_processo_id
    INNER JOIN status_processo s ON s.id = p.status_id
    WHERE p.ativo = TRUE
      AND (
            p_termo IS NULL
         OR p_termo = ''
         OR p.numero_processo LIKE CONCAT('%', p_termo, '%')
         OR p.titulo          LIKE CONCAT('%', p_termo, '%')
         OR c.nome            LIKE CONCAT('%', p_termo, '%')
          )
      AND (p_status_id   IS NULL OR p.status_id        = p_status_id)
      AND (p_advogado_id IS NULL OR p.advogado_id      = p_advogado_id)
      AND (p_tipo_id     IS NULL OR p.tipo_processo_id = p_tipo_id)
    ORDER BY p.data_abertura DESC;
END$$


-- =====================================================================
-- 3. sp_painel_resumo
--
-- Funcionalidade 06 - Painel Central de Gestao.
--
-- Agregação pura: conta quantos processos existem em cada fase e quantos
-- deles estao com o prazo vencido ou vencendo nos próximos 7 dias.
--
-- Sai da direita para a esquerda da tabela status_processo, para as
-- fases sem nenhum processo também aparecerem no painel com zero. Sem o
-- LEFT JOIN, uma fase vazia sumiria e o painel mentiria.
-- =====================================================================

DROP PROCEDURE IF EXISTS sp_painel_resumo$$

CREATE PROCEDURE sp_painel_resumo()
BEGIN
    SELECT
        s.id                AS status_id,
        s.nome              AS status_nome,
        s.cor_hex           AS status_cor,
        s.ordem,
        COUNT(p.id)         AS total_processos,
        SUM(CASE
                WHEN p.prazo_final IS NOT NULL
                 AND p.prazo_final < CURDATE()
                THEN 1 ELSE 0
            END)            AS total_vencidos,
        SUM(CASE
                WHEN p.prazo_final IS NOT NULL
                 AND p.prazo_final BETWEEN CURDATE()
                                       AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                THEN 1 ELSE 0
            END)            AS total_vencendo
    FROM status_processo s
    LEFT JOIN processo p
        ON p.status_id = s.id
       AND p.ativo = TRUE
    WHERE s.ativo = TRUE
    GROUP BY s.id, s.nome, s.cor_hex, s.ordem
    ORDER BY s.ordem;
END$$


-- =====================================================================
-- 4. sp_pendencias_checklist
--
-- Funcionalidade 12 - Mapeamento de Pendências.
--
-- Esta e a consulta que substitui o checklist impresso. Para cada
-- processo ativo, informa quantos documentos são exigidos, quantos já
-- foram entregues e lista, em texto, quais ainda faltam.
--
-- O GROUP_CONCAT e o que monta a lista de nomes numa única coluna, algo
-- impossível de fazer no Active Record sem várias idas ao banco.
-- Processos com a documentação completa ficam de fora: o painel mostra
-- o que exige ação, não o que já esta resolvido.
-- =====================================================================

DROP PROCEDURE IF EXISTS sp_pendencias_checklist$$

CREATE PROCEDURE sp_pendencias_checklist(
    IN p_advogado_id INT
)
BEGIN
    SELECT
        p.id                AS processo_id,
        p.numero_processo,
        p.titulo,
        p.prazo_final,
        c.nome              AS cliente_nome,
        u.nome              AS advogado_nome,
        s.nome              AS status_nome,
        s.cor_hex           AS status_cor,
        COUNT(cp.id)        AS total_itens,
        SUM(CASE WHEN cp.entregue = TRUE THEN 1 ELSE 0 END) AS total_entregues,
        SUM(CASE WHEN cp.entregue = FALSE THEN 1 ELSE 0 END) AS total_pendentes,
        GROUP_CONCAT(
            CASE WHEN cp.entregue = FALSE THEN cd.nome END
            ORDER BY cd.nome
            SEPARATOR ', '
        )                   AS documentos_pendentes
    FROM processo p
    INNER JOIN cliente             c  ON c.id  = p.cliente_id
    INNER JOIN usuario             u  ON u.id  = p.advogado_id
    INNER JOIN status_processo     s  ON s.id  = p.status_id
    INNER JOIN checklist_processo  cp ON cp.processo_id = p.id
    INNER JOIN categoria_documento cd ON cd.id = cp.categoria_id
    WHERE p.ativo = TRUE
      AND (p_advogado_id IS NULL OR p.advogado_id = p_advogado_id)
    GROUP BY
        p.id, p.numero_processo, p.titulo, p.prazo_final,
        c.nome, u.nome, s.nome, s.cor_hex
    HAVING total_pendentes > 0
    ORDER BY total_pendentes DESC, p.prazo_final IS NULL, p.prazo_final;
END$$


-- =====================================================================
-- 5. sp_processos_prioritarios
--
-- Funcionalidade 14 - Marcadores Visuais.
-- Funcionalidade 15 - Filtros de Prioridade.
--
-- Ordena os processos por urgencia real, combinando duas coisas: o peso
-- do marcador aplicado (Urgente pesa 3, Prioridade 2, Prazo curto 1) e
-- quantos dias faltam para o prazo final.
--
-- A ordenação por peso máximo dos marcadores e o motivo desta consulta
-- existir: e um JOIN N:N com agregação, que não tem como sair da Model.
-- =====================================================================

DROP PROCEDURE IF EXISTS sp_processos_prioritarios$$

CREATE PROCEDURE sp_processos_prioritarios(
    IN p_advogado_id  INT,
    IN p_peso_minimo  INT
)
BEGIN
    SELECT
        p.id                AS processo_id,
        p.numero_processo,
        p.titulo,
        p.prazo_final,
        DATEDIFF(p.prazo_final, CURDATE()) AS dias_para_prazo,
        c.nome              AS cliente_nome,
        u.nome              AS advogado_nome,
        s.nome              AS status_nome,
        s.cor_hex           AS status_cor,
        COALESCE(MAX(m.peso), 0) AS peso_maximo,
        GROUP_CONCAT(
            m.nome ORDER BY m.peso DESC SEPARATOR ', '
        )                   AS marcadores,
        GROUP_CONCAT(
            m.cor_hex ORDER BY m.peso DESC SEPARATOR ','
        )                   AS marcadores_cores
    FROM processo p
    INNER JOIN cliente         c ON c.id = p.cliente_id
    INNER JOIN usuario         u ON u.id = p.advogado_id
    INNER JOIN status_processo s ON s.id = p.status_id
    LEFT JOIN processo_marcador pm ON pm.processo_id = p.id
    LEFT JOIN marcador           m ON m.id = pm.marcador_id
    WHERE p.ativo = TRUE
      AND (p_advogado_id IS NULL OR p.advogado_id = p_advogado_id)
    GROUP BY
        p.id, p.numero_processo, p.titulo, p.prazo_final,
        c.nome, u.nome, s.nome, s.cor_hex
    HAVING peso_maximo >= COALESCE(p_peso_minimo, 0)
    ORDER BY
        peso_maximo DESC,
        p.prazo_final IS NULL,
        p.prazo_final ASC;
END$$


-- =====================================================================
-- 6. sp_notificacoes_advogado
--
-- Funcionalidade 16 - Disparo de Notificações.
-- Funcionalidade 17 - Direcionamento Automático.
--
-- Devolve os avisos de um advogado já com o contexto: qual processo,
-- qual cliente e qual documento originou o aviso. Sem este JOIN, a tela
-- mostraria apenas "novo documento anexado", sem dizer em que caso.
-- =====================================================================

DROP PROCEDURE IF EXISTS sp_notificacoes_advogado$$

CREATE PROCEDURE sp_notificacoes_advogado(
    IN p_usuario_id       INT,
    IN p_apenas_nao_lidas BOOLEAN
)
BEGIN
    SELECT
        n.id,
        n.titulo,
        n.mensagem,
        n.tipo,
        n.lida,
        n.criado_em,
        p.id                AS processo_id,
        p.numero_processo,
        p.titulo            AS processo_titulo,
        c.nome              AS cliente_nome,
        d.id                AS documento_id,
        d.nome_padronizado  AS documento_nome,
        cd.nome             AS documento_categoria
    FROM notificacao n
    LEFT JOIN processo            p  ON p.id  = n.processo_id
    LEFT JOIN cliente             c  ON c.id  = p.cliente_id
    LEFT JOIN documento           d  ON d.id  = n.documento_id
    LEFT JOIN categoria_documento cd ON cd.id = d.categoria_id
    WHERE n.usuario_destino_id = p_usuario_id
      AND (p_apenas_nao_lidas = FALSE OR n.lida = FALSE)
    ORDER BY n.lida ASC, n.criado_em DESC;
END$$


DELIMITER ;


-- =====================================================================
-- CONFERENCIA
-- Depois de executar, esta consulta deve listar as 6 procedures.
-- =====================================================================

SELECT ROUTINE_NAME, ROUTINE_TYPE
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'tabflower'
ORDER BY ROUTINE_NAME;
