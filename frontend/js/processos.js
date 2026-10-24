// [JS] processos> Atalhos para os elementos da lista de processos
const tela = {
    // [JS] processos>main>div> Desenha uma ficha por processo com os botões Arquivar e Abrir
    lista: document.getElementById('lista'),
    // [JS] processos>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] processos>main>div>form> Ao enviar, refaz a busca com o termo e os filtros
    formBusca: document.getElementById('form-busca'),
    // [JS] processos>main>div>form>input> Lê o termo digitado
    campoBusca: document.getElementById('campo-busca'),
    // [JS] processos>main>div>button> Zera o campo e as três listas de filtro e recarrega
    botaoLimpar: document.getElementById('botao-limpar'),
    // [JS] processos>main>div>label>input> Ao marcar ou desmarcar, recarrega a lista
    mostrarInativos: document.getElementById('mostrar-inativos'),
    // [JS] processos>main>div>select> Recebe as situações da API; ao trocar, refaz a busca
    filtroStatus: document.getElementById('filtro-status'),
    // [JS] processos>main>div>select> Recebe os advogados da API; ao trocar, refaz a busca
    filtroAdvogado: document.getElementById('filtro-advogado'),
    // [JS] processos>main>div>select> Recebe os tipos da API; ao trocar, refaz a busca
    filtroTipo: document.getElementById('filtro-tipo'),
    // [JS] processos>main>div>span> Escreve "Fonte: Model (CRUD)" ou "Fonte: sp_buscar_processos"
    rotuloFonte: document.getElementById('rotulo-fonte')
};

// [JS] processos>main>div>article> Monta a ficha de um processo: título, selo colorido da situação, número, cliente, advogado, prazo e botões
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

// [JS] processos>main>div> Desenha a lista de fichas ou a caixa de "nenhum processo"
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

// [JS] processos>main>div>select> Preenche as três listas de filtro com situações, advogados e tipos vindos da API
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

// [JS] processos>main>div> Junta o termo da busca e os filtros escolhidos
function filtrosAtuais() {
    return {
        termo: tela.campoBusca.value.trim(),
        statusId: tela.filtroStatus.value,
        advogadoId: tela.filtroAdvogado.value,
        tipoId: tela.filtroTipo.value
    };
}

// [JS] processos> Diz se a pessoa usou busca ou algum filtro
function temFiltro(f) {
    return Boolean(f.termo || f.statusId || f.advogadoId || f.tipoId);
}

// [JS] processos>main>div> Carrega a lista: sem filtro usa a listagem simples (Model); com filtro usa a busca da procedure e mostra a fonte
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

// [JS] processos>main>div>article>div>button> Pergunta se pode arquivar e, se sim, arquiva o processo e recarrega
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
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
        carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] processos>main>div>form> Ao enviar a busca, recarrega a lista
tela.formBusca.addEventListener('submit', (evento) => {
    evento.preventDefault();
    carregar();
});

// [JS] processos>main>div>button> Ver todos: limpa busca e filtros e recarrega
tela.botaoLimpar.addEventListener('click', () => {
    tela.campoBusca.value = '';
    tela.filtroStatus.value = '';
    tela.filtroAdvogado.value = '';
    tela.filtroTipo.value = '';
    carregar();
});

// [JS] processos>main>div>select> Trocar qualquer filtro recarrega a lista
tela.filtroStatus.addEventListener('change', carregar);
tela.filtroAdvogado.addEventListener('change', carregar);
tela.filtroTipo.addEventListener('change', carregar);

// [JS] processos>main>div>label>input> Marcar ou desmarcar Mostrar arquivados recarrega a lista
tela.mostrarInativos.addEventListener('change', carregar);

// [JS] processos>main>div> Clique no botão Arquivar de qualquer ficha da lista
tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-arquivar]');
    if (botao) {
        arquivar(botao.dataset.arquivar, botao.dataset.numero);
    }
});

// [JS] processos> Ao abrir a página: preenche os filtros e depois carrega a lista
carregarFiltros().then(carregar);
