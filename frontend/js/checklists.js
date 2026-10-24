// [JS] checklists> Atalhos para os elementos da configuração de checklists
const tela = {
    // [JS] checklists>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] checklists>main>div>select> Recebe os tipos da API; ao trocar, mostra as exigências daquele tipo
    tipoProcesso: document.getElementById('tipo-processo'),
    // [JS] checklists>main>section>ul> Desenha cada exigência com os botões Tornar opcional/obrigatório e Remover
    itens: document.getElementById('itens'),
    // [JS] checklists>main>section>div>select> Mostra só as categorias livres; avisa quando todas já foram usadas
    novaCategoria: document.getElementById('nova-categoria'),
    // [JS] checklists>main>section>div>label>input> Lê se está marcada ao acrescentar
    novoObrigatorio: document.getElementById('nova-obrigatorio'),
    // [JS] checklists>main>section>div>button> Adiciona a exigência e redesenha a lista; fica travado se não houver categoria livre
    botaoAdicionar: document.getElementById('botao-adicionar')
};

// [JS] checklists> Guarda todas as categorias de documento vindas da API
let categorias = [];

// [JS] checklists>main>section>ul> Desenha as exigências: bolinha vermelha (obrigatória) ou cinza (opcional), sigla e botões
function desenharItens(lista) {
    if (lista.length === 0) {
        tela.itens.innerHTML = `
            <li class="dica">
                Este tipo de processo não exige nenhum documento. Processos
                abertos assim nascem sem checklist.
            </li>`;
        return;
    }

    tela.itens.innerHTML = lista.map((item) => `
        <li class="${item.obrigatorio ? '' : 'entregue'}">
            <span class="marca-item"
                  style="${item.obrigatorio
                      ? ''
                      : 'background-color:var(--linha); color:var(--tinta-clara); border-color:var(--linha)'}">
                ${item.obrigatorio ? '!' : '?'}
            </span>
            <span style="flex:1">
                ${escaparHtml(item.categoria_nome)}
                <span class="mono" style="font-size:0.78rem; color:var(--tinta-clara)">
                    ${escaparHtml(item.categoria_sigla)}
                </span>
            </span>
            <button type="button" class="botao botao-pequeno"
                    data-alternar="${item.id}">
                ${item.obrigatorio ? 'Tornar opcional' : 'Tornar obrigatório'}
            </button>
            <button type="button" class="botao botao-pequeno botao-perigo"
                    data-remover="${item.id}"
                    data-nome="${escaparHtml(item.categoria_nome)}">
                Remover
            </button>
        </li>`).join('');
}

// [JS] checklists>main>section>div>select> Mostra só as categorias que este tipo ainda não exige; trava o botão se não sobrar nenhuma
function atualizarCategoriasDisponiveis(jaUsadas) {
    const usados = new Set(jaUsadas.map((i) => i.categoria_id));
    const livres = categorias.filter((c) => !usados.has(c.id));

    if (livres.length === 0) {
        tela.novaCategoria.innerHTML =
            '<option value="">Todas as categorias já foram usadas</option>';
        tela.botaoAdicionar.disabled = true;
        return;
    }

    tela.novaCategoria.innerHTML = livres
        .map((c) => `<option value="${c.id}">${escaparHtml(c.nome)}</option>`)
        .join('');
    tela.botaoAdicionar.disabled = false;
}

// [JS] checklists>main>section>ul> Busca as exigências do tipo escolhido e redesenha a lista
async function carregarItens() {
    limparAviso(tela.aviso);

    if (!tela.tipoProcesso.value) {
        return;
    }

    tela.itens.innerHTML = '<li class="dica">Carregando...</li>';

    try {
        const lista = await api.checklists.listar(tela.tipoProcesso.value);
        desenharItens(lista);
        atualizarCategoriasDisponiveis(lista);
    } catch (erro) {
        tela.itens.innerHTML = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] checklists>main>div>select> Prepara a tela: busca tipos e categorias, preenche a lista de tipos e carrega o primeiro
async function prepararTela() {
    try {
        const opcoes = await api.checklists.opcoes();
        categorias = opcoes.categorias;

        tela.tipoProcesso.innerHTML = opcoes.tipos
            .map((t) => `<option value="${t.id}">${escaparHtml(t.nome)}</option>`)
            .join('');

        await carregarItens();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] checklists>main>div>select> Trocar o tipo de processo carrega as exigências dele
tela.tipoProcesso.addEventListener('change', carregarItens);

// [JS] checklists>main>section>div>button> Acrescentar: envia a categoria e se é obrigatória, depois redesenha
tela.botaoAdicionar.addEventListener('click', async () => {
    limparAviso(tela.aviso);
    tela.botaoAdicionar.disabled = true;

    try {
        const lista = await api.checklists.adicionar({
            tipo_processo_id: Number(tela.tipoProcesso.value),
            categoria_id: Number(tela.novaCategoria.value),
            obrigatorio: tela.novoObrigatorio.checked
        });

        desenharItens(lista);
        atualizarCategoriasDisponiveis(lista);
        mostrarAviso(
            tela.aviso,
            'Exigência acrescentada. Vale para processos abertos daqui em diante.',
            'sucesso'
        );
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    } finally {
        tela.botaoAdicionar.disabled = false;
    }
});

// [JS] checklists>main>section>ul> Cliques na lista: Tornar opcional/obrigatório alterna; Remover pede confirmação e tira a exigência
tela.itens.addEventListener('click', async (evento) => {
    const alternar = evento.target.closest('[data-alternar]');
    const remover = evento.target.closest('[data-remover]');

    try {
        if (alternar) {
            const lista = await api.checklists.alternarObrigatorio(
                alternar.dataset.alternar
            );
            desenharItens(lista);
            return;
        }

        if (remover) {
            const confirmou = confirm(
                `Remover "${remover.dataset.nome}" das exigências deste tipo?\n\n` +
                `Processos já abertos mantêm o checklist que receberam. ` +
                `A mudança vale só para os próximos.`
            );
            if (!confirmou) {
                return;
            }

            const lista = await api.checklists.remover(remover.dataset.remover);
            desenharItens(lista);
            atualizarCategoriasDisponiveis(lista);
        }
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
});

// [JS] checklists> Prepara a tela assim que a página abre
prepararTela();
