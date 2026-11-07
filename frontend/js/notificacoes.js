/*
==============================================================================
SEÇÃO COMENTÁRIOS — notificacoes.js: Lógica da página notificacoes.html: Avisos de quem está logado
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
notificacoes> tela: Atalhos para os elementos da tela de avisos
notificacoes>main>div> tela.lista: Desenha cada aviso com processo, cliente, data e botões Abrir processo e Marcar lido
notificacoes>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
notificacoes>main>div>label>input> tela.apenasNaoLidas: Ao marcar ou desmarcar, recarrega os avisos
notificacoes>main>div>article> corDoTipo(): Escolhe a cor do selo pelo tipo do aviso (documento, prazo, situação)
notificacoes>main>div>article> montarFicha(): Monta a ficha do aviso: título, selo do tipo, processo, cliente, data, mensagem e botões (lido fica apagado)
notificacoes>main>div> desenhar(): Desenha a lista de avisos ou a caixa de "nenhum aviso"
notificacoes>main>div> carregar(): Busca os avisos de quem está logado (todos ou só os não lidos)
notificacoes>main>div>label>input> tela.apenasNaoLidas (change): Marcar ou desmarcar Apenas não lidos recarrega a lista
notificacoes>main>div> tela.lista (click): Clique em Marcar lido marca o aviso e recarrega
notificacoes> carregar(): Carrega os avisos assim que a página abre
==============================================================================
*/

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    apenasNaoLidas: document.getElementById('apenas-nao-lidas')
};

function corDoTipo(tipo) {
    if (tipo === 'DOCUMENTO') { return '#2f6f4e'; }
    if (tipo === 'PRAZO') { return '#c2410c'; }
    if (tipo === 'STATUS') { return '#1b2a41'; }
    return '#5a6472';
}

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

tela.apenasNaoLidas.addEventListener('change', carregar);

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

carregar();
