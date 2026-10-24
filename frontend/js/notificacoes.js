// [JS] notificacoes> Atalhos para os elementos da tela de avisos
const tela = {
    // [JS] notificacoes>main>div> Desenha cada aviso com processo, cliente, data e botões Abrir processo e Marcar lido
    lista: document.getElementById('lista'),
    // [JS] notificacoes>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] notificacoes>main>div>label>input> Ao marcar ou desmarcar, recarrega os avisos
    apenasNaoLidas: document.getElementById('apenas-nao-lidas')
};

// [JS] notificacoes>main>div>article> Escolhe a cor do selo pelo tipo do aviso (documento, prazo, situação)
function corDoTipo(tipo) {
    if (tipo === 'DOCUMENTO') { return '#2f6f4e'; }
    if (tipo === 'PRAZO') { return '#c2410c'; }
    if (tipo === 'STATUS') { return '#1b2a41'; }
    return '#5a6472';
}

// [JS] notificacoes>main>div>article> Monta a ficha do aviso: título, selo do tipo, processo, cliente, data, mensagem e botões (lido fica apagado)
function montarFicha(n) {
    const classeLida = n.lida ? ' inativa' : '';

    const contexto = [];
    if (n.numero_processo) {
        contexto.push(`<span class="mono">${escaparHtml(n.numero_processo)}</span>`);
    }
    if (n.cliente_nome) {
        contexto.push(`<span>${escaparHtml(n.cliente_nome)}</span>`);
    }
    if (n.documento_categoria) {
        contexto.push(`<span>${escaparHtml(n.documento_categoria)}</span>`);
    }

    const quando = n.criado_em
        ? new Date(n.criado_em).toLocaleString('pt-BR')
        : '';

    const acoes = [];
    if (n.processo_id) {
        acoes.push(`<a href="processo-detalhe.html?id=${n.processo_id}"
                       class="botao botao-pequeno">Abrir processo</a>`);
    }
    if (!n.lida) {
        acoes.push(`<button type="button" class="botao botao-pequeno"
                            data-lida="${n.id}">Marcar lido</button>`);
    } else {
        acoes.push('<span class="etiqueta etiqueta-cinza">Lido</span>');
    }

    return `
        <article class="ficha${classeLida}">
            <div class="ficha-dados">
                <div class="ficha-nome">${escaparHtml(n.titulo)}</div>
                <div class="ficha-info">
                    <span class="etiqueta-status"
                          style="background-color:${corDoTipo(n.tipo)}">
                        ${escaparHtml(n.tipo)}
                    </span>
                    ${contexto.join('')}
                    <span class="texto-prazo">${quando}</span>
                </div>
                <div class="texto-prazo" style="margin-top:4px">
                    ${escaparHtml(n.mensagem)}
                </div>
            </div>
            <div class="ficha-acoes">${acoes.join('')}</div>
        </article>`;
}

// [JS] notificacoes>main>div> Desenha a lista de avisos ou a caixa de "nenhum aviso"
function desenhar(avisos) {
    if (avisos.length === 0) {
        tela.lista.innerHTML = `
            <div class="vazio">
                <strong>Nenhum aviso para este usuário</strong>
                Anexe um documento a um processo e o advogado responsável
                recebe o aviso automaticamente.
            </div>`;
        return;
    }
    tela.lista.innerHTML = avisos.map(montarFicha).join('');
}

// [JS] notificacoes>main>div> Busca os avisos de quem está logado (todos ou só os não lidos)
async function carregar() {
    limparAviso(tela.aviso);

    tela.lista.innerHTML = '<div class="vazio">Carregando...</div>';

    try {
        const avisos = await api.notificacoes.listar(
            tela.apenasNaoLidas.checked
        );
        desenhar(avisos);
    } catch (erro) {
        tela.lista.innerHTML = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] notificacoes>main>div>label>input> Marcar ou desmarcar Apenas não lidos recarrega a lista
tela.apenasNaoLidas.addEventListener('change', carregar);

// [JS] notificacoes>main>div> Clique em Marcar lido marca o aviso e recarrega
tela.lista.addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-lida]');
    if (!botao) {
        return;
    }

    try {
        await api.notificacoes.marcarLida(botao.dataset.lida);
        carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
});

// [JS] notificacoes> Carrega os avisos assim que a página abre
carregar();
