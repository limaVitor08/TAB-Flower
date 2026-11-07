/*
==============================================================================
SEÇÃO COMENTÁRIOS — painel.js: Lógica da página painel.html: Painel de gestão: resumo por situação, prioridades e pendências
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
painel> tela: Atalhos para os elementos do painel
painel>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
painel>main>section>div> tela.resumo: Desenha um cartão por situação, com total e alertas de prazo
painel>main>div>section>ul> tela.prioritarios: Monta um item por processo com marcadores, situação e prazo
painel>main>div>section>ul> tela.pendencias: Monta um item por processo dizendo o que falta entregar
painel>main>div>section>div>select> tela.filtroPeso: Ao trocar a opção, recarrega a lista de prioridades
painel>main>div>section>ul>li> descreverPrazo(): Escreve o prazo do processo; fica vermelho se venceu ou vence em até 7 dias
painel>main>section>div> desenharResumo(): Desenha o cartão de total e um cartão por situação, com a cor da situação na faixa de cima
painel>main>div>section>ul> desenharPrioritarios(): Desenha a lista de prioridades: título, selos coloridos dos marcadores, situação e prazo
painel>main>div>section>ul> desenharPendencias(): Desenha a lista de pendências: título, situação, quantos documentos foram entregues e o que falta
painel>main>div>section>ul> carregarPrioritarios(): Busca na API os processos prioritários usando o filtro escolhido
painel>main> carregar(): Carrega o painel inteiro: resumo, pendências e prioridades; se falhar, mostra o erro
painel>main>div>section>div>select> tela.filtroPeso (change): Ao trocar o filtro, recarrega só a lista de prioridades
painel> carregar(): Começa a carregar o painel assim que a página abre
==============================================================================
*/

const tela = {
    aviso: document.getElementById('aviso'),
    resumo: document.getElementById('resumo'),
    prioritarios: document.getElementById('prioritarios'),
    pendencias: document.getElementById('pendencias'),
    filtroPeso: document.getElementById('filtro-peso')
};

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

function desenharPrioritarios(linhas) {
    if (linhas.length === 0) {
        tela.prioritarios.innerHTML =
            '<li class="dica">Nenhum processo neste filtro.</li>';
        return;
    }

    tela.prioritarios.innerHTML = linhas.map((p) => {
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
