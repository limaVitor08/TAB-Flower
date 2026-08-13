/* =====================================================================
   TabFlower - Avisos internos
   =====================================================================
   Funcionalidade 16 (Disparo de Notificações)
   Funcionalidade 17 (Direcionamento Automático)

   Os avisos são criados pelo sistema, nunca pelo usuário: quando um
   documento é anexado, o EnviarDocumentoService descobre quem é o
   advogado do processo e cria o aviso para ele. Por isso esta tela só
   lê e marca como lido.

   Os dados vêm da procedure sp_notificacoes_advogado, que junta o aviso
   ao processo, ao cliente e ao documento. Sem esse JOIN, a tela diria
   apenas "novo documento", sem dizer em qual caso.
   ===================================================================== */

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    apenasNaoLidas: document.getElementById('apenas-nao-lidas')
};

/** Cor da tarja conforme o tipo de aviso. */
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

/* Antes existia aqui um seletor "avisos de quem", porque sem login o
   sistema não sabia quem estava operando. Com a sessão, esse seletor
   deixou de fazer sentido: cada pessoa vê apenas os próprios avisos, e
   quem é essa pessoa o backend descobre pelo token. */
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
