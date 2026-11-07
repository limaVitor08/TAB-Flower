/* Stored procedures usadas pelos Repositories nas buscas e no painel */

USE tabflower;

DELIMITER $$

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

DROP PROCEDURE IF EXISTS sp_buscar_processos$$

CREATE PROCEDURE sp_buscar_processos(
    IN p_termo             VARCHAR(150),
    IN p_status_id         INT,
    IN p_advogado_id       INT,
    IN p_tipo_id           INT,
    IN p_incluir_arquivados BOOLEAN
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
    WHERE (p_incluir_arquivados = TRUE OR p.ativo = TRUE)
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

SELECT ROUTINE_NAME, ROUTINE_TYPE
FROM INFORMATION_SCHEMA.ROUTINES
WHERE ROUTINE_SCHEMA = 'tabflower'
ORDER BY ROUTINE_NAME;
