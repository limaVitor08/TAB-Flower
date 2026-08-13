/* =====================================================================
   TabFlower - Configuração de checklists
   =====================================================================
   Funcionalidade 13 (Configuração de Checklist).

   Esta tela edita o MOLDE: a lista de documentos que cada tipo de
   processo exige. O molde é copiado uma única vez, no momento em que um
   processo é aberto.

   Consequência importante, avisada na própria tela: mudar o molde hoje
   não altera o checklist de um processo já protocolado. Se alterasse,
   um processo fechado no mês passado poderia voltar a aparecer como
   incompleto por causa de uma exigência criada depois.
   ===================================================================== */

const tela = {
    aviso: document.getElementById('aviso'),
    tipoProcesso: document.getElementById('tipo-processo'),
    itens: document.getElementById('itens'),
    novaCategoria: document.getElementById('nova-categoria'),
    novoObrigatorio: document.getElementById('nova-obrigatorio'),
    botaoAdicionar: document.getElementById('botao-adicionar')
};

let categorias = [];

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

/** Só oferece categorias que ainda não estão na lista deste tipo. */
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

tela.tipoProcesso.addEventListener('change', carregarItens);

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

prepararTela();
