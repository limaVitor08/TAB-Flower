/* =====================================================================
   TabFlower - Painel de gestao (Terceira Etapa)
   =====================================================================
   Esta tela não usa nenhuma consulta simples. Os três paineis vem de
   stored procedures do MySQL, chamadas pela camada Repository:

     Funcionalidade 06 - sp_painel_resumo
     Funcionalidade 12 - sp_pendencias_checklist
     Funcionalidades 14 e 15 - sp_processos_prioritarios
   ===================================================================== */

const tela = {
    aviso: document.getElementById('aviso'),
    resumo: document.getElementById('resumo'),
    prioritarios: document.getElementById('prioritarios'),
    pendencias: document.getElementById('pendencias'),
    filtroPeso: document.getElementById('filtro-peso')
};

/** Descreve o prazo em linguagem humana. */
function descreverPrazo(prazo, dias) {
    if (!prazo) {
        return '<span class="texto-prazo">Sem prazo definido</span>';
    }

    const data = formatarData(prazo);

    if (dias === null || dias === undefined) {
        return `<span class="texto-prazo">Prazo: ${data}</span>`;
    }

    if (dias < 0) {
        return `<span class="texto-prazo vencido">Vencido há ${Math.abs(dias)} dia(s) &middot; ${data}</span>`;
    }
    if (dias === 0) {
        return `<span class="texto-prazo vencido">Vence hoje &middot; ${data}</span>`;
    }
    if (dias <= 7) {
        return `<span class="texto-prazo vencido">Faltam ${dias} dia(s) &middot; ${data}</span>`;
    }
    return `<span class="texto-prazo">Prazo: ${data}</span>`;
}

/* ---------------------------------------------------------------------
   Funcionalidade 06 - Painel Central de Gestao
   --------------------------------------------------------------------- */

function desenharResumo(dados) {
    const cartoes = dados.por_status.map((s) => {
        const alertas = [];
        if (Number(s.total_vencidos) > 0) {
            alertas.push(`${s.total_vencidos} vencido(s)`);
        }
        if (Number(s.total_vencendo) > 0) {
            alertas.push(`${s.total_vencendo} vencendo`);
        }

        return `
            <div class="cartao" style="border-top-color:${s.status_cor || '#6b7280'}">
                <div class="cartao-numero">${s.total_processos}</div>
                <div class="cartao-rotulo">${escaparHtml(s.status_nome)}</div>
                ${alertas.length
                    ? `<div class="cartao-alerta">${alertas.join(' &middot; ')}</div>`
                    : ''}
            </div>`;
    }).join('');

    // Cartao de total geral, calculado pelo Service a partir das linhas.
    const total = `
        <div class="cartao" style="border-top-color:var(--tinta)">
            <div class="cartao-numero">${dados.total_processos}</div>
            <div class="cartao-rotulo">Total de processos ativos</div>
            ${dados.total_vencidos > 0
                ? `<div class="cartao-alerta">${dados.total_vencidos} com prazo vencido</div>`
                : ''}
        </div>`;

    tela.resumo.innerHTML = total + cartoes;
}

/* ---------------------------------------------------------------------
   Funcionalidades 14 e 15 - Marcadores e Filtros de Prioridade
   --------------------------------------------------------------------- */

function desenharPrioritarios(linhas) {
    if (linhas.length === 0) {
        tela.prioritarios.innerHTML =
            '<li class="dica">Nenhum processo neste filtro.</li>';
        return;
    }

    tela.prioritarios.innerHTML = linhas.map((p) => {
        // A procedure devolve os nomes e as cores em duas listas
        // separadas por virgula, na mesma ordem.
        const nomes = (p.marcadores || '').split(',').filter(Boolean);
        const cores = (p.marcadores_cores || '').split(',').filter(Boolean);

        const selos = nomes.map((nome, i) =>
            `<span class="selo" style="background-color:${cores[i] || '#6b7280'}">${escaparHtml(nome.trim())}</span>`
        ).join('');

        return `
            <li class="item-painel">
                <a href="processo-detalhe.html?id=${p.processo_id}">${escaparHtml(p.titulo)}</a>
                <div class="item-linha">
                    ${selos}
                    <span class="selo" style="background-color:${p.status_cor || '#6b7280'}">${escaparHtml(p.status_nome)}</span>
                    <span class="mono" style="font-size:0.8rem">${escaparHtml(p.numero_processo)}</span>
                </div>
                <div class="item-linha">
                    <span class="texto-prazo">${escaparHtml(p.cliente_nome)}</span>
                    ${descreverPrazo(p.prazo_final, p.dias_para_prazo)}
                </div>
            </li>`;
    }).join('');
}

/* ---------------------------------------------------------------------
   Funcionalidade 12 - Mapeamento de Pendências
   --------------------------------------------------------------------- */

function desenharPendencias(linhas) {
    if (linhas.length === 0) {
        tela.pendencias.innerHTML =
            '<li class="dica">Nenhum processo com documentação pendente.</li>';
        return;
    }

    tela.pendencias.innerHTML = linhas.map((p) => `
        <li class="item-painel">
            <a href="processo-detalhe.html?id=${p.processo_id}">${escaparHtml(p.titulo)}</a>
            <div class="item-linha">
                <span class="selo" style="background-color:${p.status_cor || '#6b7280'}">${escaparHtml(p.status_nome)}</span>
                <span class="texto-prazo">${escaparHtml(p.cliente_nome)}</span>
                <span class="texto-prazo">${p.total_entregues} de ${p.total_itens} entregues</span>
            </div>
            <div class="texto-pendente">
                Falta: ${escaparHtml(p.documentos_pendentes || '')}
            </div>
        </li>`).join('');
}

/* ---------------------------------------------------------------------
   Carga
   --------------------------------------------------------------------- */

async function carregarPrioritarios() {
    tela.prioritarios.innerHTML = '<li class="dica">Carregando...</li>';
    try {
        const peso = tela.filtroPeso.value || null;
        desenharPrioritarios(await api.painel.prioritarios(peso));
    } catch (erro) {
        tela.prioritarios.innerHTML =
            `<li class="dica">${escaparHtml(erro.message)}</li>`;
    }
}

async function carregar() {
    limparAviso(tela.aviso);
    tela.resumo.innerHTML = '<div class="cartao">Carregando...</div>';
    tela.pendencias.innerHTML = '<li class="dica">Carregando...</li>';

    try {
        // As três procedures são chamadas em paralelo.
        const [resumo, pendencias] = await Promise.all([
            api.painel.resumo(),
            api.painel.pendencias()
        ]);

        desenharResumo(resumo);
        desenharPendencias(pendencias);
        await carregarPrioritarios();
    } catch (erro) {
        tela.resumo.innerHTML = '';
        tela.pendencias.innerHTML = '';
        mostrarAviso(
            tela.aviso,
            erro.message +
            ' Se a mensagem falar em PROCEDURE, rode o arquivo ' +
            'backend/database/procedures.sql no MySQL Workbench.'
        );
    }
}

tela.filtroPeso.addEventListener('change', carregarPrioritarios);

carregar();
