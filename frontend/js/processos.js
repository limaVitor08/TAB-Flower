/*
==============================================================================
SEÇÃO COMENTÁRIOS — processos.js: Lógica da página processos.html: Lista, busca e filtros de processos
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
processos> tela: Atalhos para os elementos da lista de processos
processos>main>div> tela.lista: Desenha uma ficha por processo com os botões Arquivar e Abrir
processos>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
processos>main>div>form> tela.formBusca: Ao enviar, refaz a busca com o termo e os filtros
processos>main>div>form>input> tela.campoBusca: Lê o termo digitado
processos>main>div>button> tela.botaoLimpar: Zera o campo e as três listas de filtro e recarrega
processos>main>div>label>input> tela.mostrarInativos: Ao marcar ou desmarcar, recarrega a lista
processos>main>div>select> tela.filtroStatus: Recebe as situações da API; ao trocar, refaz a busca
processos>main>div>select> tela.filtroAdvogado: Recebe os advogados da API; ao trocar, refaz a busca
processos>main>div>select> tela.filtroTipo: Recebe os tipos da API; ao trocar, refaz a busca
processos>main>div>span> tela.rotuloFonte: Escreve "Fonte: Model (CRUD)" ou "Fonte: sp_buscar_processos"
processos>main>div>article> montarFicha(): Monta a ficha de um processo: título, selo colorido da situação, número, cliente, advogado, prazo e botões
processos>main>div> desenharLista(): Desenha a lista de fichas ou a caixa de "nenhum processo"
processos>main>div>select> carregarFiltros(): Preenche as três listas de filtro com situações, advogados e tipos vindos da API
processos>main>div> filtrosAtuais(): Junta o termo da busca, os filtros escolhidos e a caixa Mostrar arquivados
processos> temFiltro(): Diz se a pessoa usou busca ou algum filtro
processos>main>div> carregar(): Carrega a lista: sem filtro usa a listagem simples (Model); com filtro usa a busca da procedure e mostra a fonte
processos>main>div>article>div>button> arquivar(): Pergunta se pode arquivar e, se sim, arquiva o processo e recarrega
processos>main>div>form> tela.formBusca (submit): Ao enviar a busca, recarrega a lista
processos>main>div>button> tela.botaoLimpar (click): Ver todos: limpa busca e filtros e recarrega
processos>main>div>select> tela.filtroStatus (change): Trocar qualquer filtro recarrega a lista
processos>main>div>label>input> tela.mostrarInativos (change): Marcar ou desmarcar Mostrar arquivados recarrega a lista
processos>main>div> tela.lista (click): Clique no botão Arquivar de qualquer ficha da lista
processos> carregarFiltros(): Ao abrir a página: preenche os filtros e depois carrega a lista
==============================================================================
*/

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    formBusca: document.getElementById('form-busca'),
    campoBusca: document.getElementById('campo-busca'),
    botaoLimpar: document.getElementById('botao-limpar'),
    mostrarInativos: document.getElementById('mostrar-inativos'),
    filtroStatus: document.getElementById('filtro-status'),
    filtroAdvogado: document.getElementById('filtro-advogado'),
    filtroTipo: document.getElementById('filtro-tipo'),
    rotuloFonte: document.getElementById('rotulo-fonte')
};

function montarFicha(processo) {
    const classeInativa = processo.ativo ? '' : ' inativa';
    const cor = processo.status_cor || '#6b7280';

    const acoes = processo.ativo
        ? `<button type="button" class="botao botao-pequeno botao-perigo"
                   data-arquivar="${processo.id}"
                   data-numero="${escaparHtml(processo.numero_processo)}">
               Arquivar
           </button>`
        : `<span class="etiqueta etiqueta-cinza">Arquivado</span>`;

    const prazo = processo.prazo_final
        ? `<span>Prazo: ${formatarData(processo.prazo_final)}</span>`
        : '';

    return `
        <article class="ficha${classeInativa}">
            <div class="ficha-dados">
                <div class="ficha-nome">${escaparHtml(processo.titulo)}</div>
                <div class="ficha-info">
                    <span class="etiqueta-status" style="background-color:${cor}">
                        ${escaparHtml(processo.status_nome)}
                    </span>
                    <span class="mono">${escaparHtml(processo.numero_processo)}</span>
                    <span>${escaparHtml(processo.cliente_nome)}</span>
                    <span>${escaparHtml(processo.advogado_nome)}</span>
                    ${prazo}
                </div>
            </div>
            <div class="ficha-acoes">
                ${acoes}
                <a href="processo-detalhe.html?id=${processo.id}"
                   class="botao botao-pequeno">Abrir</a>
            </div>
        </article>
    `;
}

function desenharLista(processos, houveFiltro) {
    if (processos.length === 0) {
        const mensagem = houveFiltro
            ? `<strong>Nenhum processo encontrado</strong>
               Tente outro termo ou limpe os filtros.`
            : `<strong>Nenhum processo cadastrado ainda</strong>
               Cadastre o primeiro e o checklist de documentos é montado sozinho.`;

        tela.lista.innerHTML = `<div class="vazio">${mensagem}</div>`;
        return;
    }

    tela.lista.innerHTML = processos.map(montarFicha).join('');
}

async function carregarFiltros() {
    try {
        const opcoes = await api.processos.opcoes();

        const montar = (select, itens, rotuloVazio) => {
            select.innerHTML =
                `<option value="">${rotuloVazio}</option>` +
                itens
                    .map((i) => `<option value="${i.id}">${escaparHtml(i.nome)}</option>`)
                    .join('');
        };

        montar(tela.filtroStatus, opcoes.status, 'Todas');
        montar(tela.filtroAdvogado, opcoes.advogados, 'Todos');
        montar(tela.filtroTipo, opcoes.tipos, 'Todos');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

function filtrosAtuais() {
    return {
        termo: tela.campoBusca.value.trim(),
        statusId: tela.filtroStatus.value,
        advogadoId: tela.filtroAdvogado.value,
        tipoId: tela.filtroTipo.value,
        incluirInativos: tela.mostrarInativos.checked
    };
}

function temFiltro(f) {
    return Boolean(f.termo || f.statusId || f.advogadoId || f.tipoId);
}

async function carregar() {
    limparAviso(tela.aviso);
    tela.lista.innerHTML = '<div class="vazio">Carregando...</div>';

    const filtros = filtrosAtuais();
    const usarProcedure = temFiltro(filtros);

    try {
        let processos;

        if (usarProcedure) {
            processos = await api.processos.buscar(filtros);
            tela.rotuloFonte.textContent = 'Fonte: sp_buscar_processos';
        } else {
            processos = await api.processos.listar(tela.mostrarInativos.checked);
            tela.rotuloFonte.textContent = 'Fonte: Model (CRUD)';
        }

        desenharLista(processos, usarProcedure);
    } catch (erro) {
        tela.lista.innerHTML = '';
        tela.rotuloFonte.textContent = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

async function arquivar(id, numero) {
    const confirmou = confirm(
        `Arquivar o processo ${numero}?\n\n` +
        `Ele sai da lista, mas continua no banco com todo o histórico, ` +
        `o checklist e os documentos anexados.`
    );

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await api.processos.excluir(id);
        await carregar();
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

tela.formBusca.addEventListener('submit', (evento) => {
    evento.preventDefault();
    carregar();
});

tela.botaoLimpar.addEventListener('click', () => {
    tela.campoBusca.value = '';
    tela.filtroStatus.value = '';
    tela.filtroAdvogado.value = '';
    tela.filtroTipo.value = '';
    carregar();
});

tela.filtroStatus.addEventListener('change', carregar);
tela.filtroAdvogado.addEventListener('change', carregar);
tela.filtroTipo.addEventListener('change', carregar);

tela.mostrarInativos.addEventListener('change', carregar);

tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-arquivar]');
    if (botao) {
        arquivar(botao.dataset.arquivar, botao.dataset.numero);
    }
});

carregarFiltros().then(carregar);
