/* =====================================================================
   TabFlower - Acervo de documentos
   =====================================================================
   Funcionalidades atendidas:
     09 - Identificação de Categoria (permite corrigir a classificação)
     10 - Renomeação Automática (mostra o nome gerado pelo sistema)
     20 - Restricao de Exclusão (exclui logicamente e permite restaurar)
   ===================================================================== */

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    formBusca: document.getElementById('form-busca'),
    campoBusca: document.getElementById('campo-busca'),
    botaoLimpar: document.getElementById('botao-limpar'),
    mostrarExcluidos: document.getElementById('mostrar-excluidos')
};

/* Quem está executando a ação vem da sessão, no backend, a partir do
   token. A tela não informa mais nenhum id de usuário: se informasse,
   seria ignorado. */

let categorias = [];
let documentos = [];

/** Monta o select de categoria de uma ficha, já com a atual marcada. */
function selectCategoria(documento) {
    const opcoes = categorias
        .map((c) => `<option value="${c.id}"${c.id === documento.categoria_id ? ' selected' : ''}>${escaparHtml(c.nome)}</option>`)
        .join('');

    return `<select class="select-categoria" data-doc="${documento.id}">${opcoes}</select>`;
}

function montarFicha(d) {
    const classeInativa = d.excluido ? ' inativa' : '';

    const acoes = d.excluido
        ? `<button type="button" class="botao botao-pequeno"
                   data-restaurar="${d.id}">Restaurar</button>`
        : `<a href="#" data-baixar="${d.id}" data-nome="${escaparHtml(d.nome_padronizado)}"
               class="botao botao-pequeno">Baixar</a>
           <button type="button" class="botao botao-pequeno botao-perigo"
                   data-excluir="${d.id}">Excluir</button>`;

    const vinculo = d.processo_id
        ? `<a href="processo-detalhe.html?id=${d.processo_id}">Ver processo</a>`
        : '<span class="dica">Sem processo vinculado</span>';

    return `
        <article class="ficha${classeInativa}">
            <div class="ficha-dados">
                <div class="ficha-nome mono"
                     style="font-size:0.95rem">${escaparHtml(d.nome_padronizado)}</div>
                <div class="ficha-info">
                    ${d.excluido
                        ? '<span class="etiqueta etiqueta-cinza">Excluido</span>'
                        : selectCategoria(d)}
                    <span>${escaparHtml(d.cliente_nome)}</span>
                    <span>${formatarTamanho(d.tamanho_kb)}</span>
                    ${vinculo}
                </div>
            </div>
            <div class="ficha-acoes">${acoes}</div>
        </article>
    `;
}

function desenhar(lista) {
    if (lista.length === 0) {
        tela.lista.innerHTML = `
            <div class="vazio">
                <strong>Nenhum documento no acervo</strong>
                Anexe documentos pela tela de detalhe de um processo.
            </div>`;
        return;
    }
    tela.lista.innerHTML = lista.map(montarFicha).join('');
}

/** Filtra na memória: a lista de documentos do escritório e pequena. */
function filtrar(termo) {
    const t = termo.toLowerCase();
    return documentos.filter((d) =>
        (d.nome_padronizado || '').toLowerCase().includes(t) ||
        (d.cliente_nome || '').toLowerCase().includes(t) ||
        (d.categoria_nome || '').toLowerCase().includes(t)
    );
}

async function carregar() {
    limparAviso(tela.aviso);
    tela.lista.innerHTML = '<div class="vazio">Carregando...</div>';

    try {
        if (categorias.length === 0) {
            categorias = await api.documentos.categorias();
        }

        documentos = await api.documentos.listar({
            incluirExcluidos: tela.mostrarExcluidos.checked
        });

        const termo = tela.campoBusca.value.trim();
        desenhar(termo ? filtrar(termo) : documentos);
    } catch (erro) {
        tela.lista.innerHTML = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

/* --- eventos --- */

tela.formBusca.addEventListener('submit', (evento) => {
    evento.preventDefault();
    const termo = tela.campoBusca.value.trim();
    desenhar(termo ? filtrar(termo) : documentos);
});

tela.botaoLimpar.addEventListener('click', () => {
    tela.campoBusca.value = '';
    desenhar(documentos);
});

tela.mostrarExcluidos.addEventListener('change', carregar);

/* Corrigir a categoria: Funcionalidade 09. */
tela.lista.addEventListener('change', async (evento) => {
    const select = evento.target.closest('.select-categoria');
    if (!select) {
        return;
    }

    try {
        await api.documentos.atualizar(select.dataset.doc, {
            categoria_id: Number(select.value)
        });
        mostrarAviso(tela.aviso, 'Categoria atualizada.', 'sucesso');
        carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        carregar();
    }
});

tela.lista.addEventListener('click', async (evento) => {
    const excluir = evento.target.closest('[data-excluir]');
    const restaurar = evento.target.closest('[data-restaurar]');
    const baixar = evento.target.closest('[data-baixar]');

    // O download passa por JavaScript porque o navegador não envia o
    // cabeçalho Authorization num link clicado - sem o token, a API
    // recusaria o pedido.
    if (baixar) {
        evento.preventDefault();
        try {
            await api.documentos.baixar(
                baixar.dataset.baixar, baixar.dataset.nome
            );
        } catch (erro) {
            mostrarAviso(tela.aviso, erro.message);
        }
        return;
    }

    if (excluir) {
        const confirmou = confirm(
            'Excluir este documento?\n\n' +
            'Somente o Administrador pode. O registro permanece no banco ' +
            'com a marca de exclusão, e se ele atendia uma pendência do ' +
            'checklist, a pendência volta a aparecer.'
        );
        if (!confirmou) { return; }

        try {
            const r = await api.documentos.excluir(excluir.dataset.excluir);

            let mensagem = r.mensagem;
            if (r.retorno_status) {
                mensagem +=
                    ` A pendência do checklist reabriu, então o processo ` +
                    `voltou para "${r.retorno_status}".`;
            }

            mostrarAviso(tela.aviso, mensagem, 'sucesso');
            carregar();
        } catch (erro) {
            mostrarAviso(tela.aviso, erro.message);
        }
        return;
    }

    if (restaurar) {
        try {
            const r = await api.documentos.restaurar(restaurar.dataset.restaurar);
            mostrarAviso(tela.aviso, r.mensagem, 'sucesso');
            carregar();
        } catch (erro) {
            mostrarAviso(tela.aviso, erro.message);
        }
    }
});

carregar();
