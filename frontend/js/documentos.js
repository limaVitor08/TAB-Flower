// [JS] documentos> Atalhos para os elementos do acervo
const tela = {
    // [JS] documentos>main>div> Desenha cada documento com categoria editável e botões Baixar, Excluir ou Restaurar
    lista: document.getElementById('lista'),
    // [JS] documentos>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] documentos>main>div>form> Filtra a lista já carregada, sem chamar a API de novo
    formBusca: document.getElementById('form-busca'),
    // [JS] documentos>main>div>form>input> Lê o texto do filtro
    campoBusca: document.getElementById('campo-busca'),
    // [JS] documentos>main>div>button> Limpa o campo e mostra a lista completa
    botaoLimpar: document.getElementById('botao-limpar'),
    // [JS] documentos>main>div>label>input> Ao marcar ou desmarcar, recarrega a lista
    mostrarExcluidos: document.getElementById('mostrar-excluidos')
};

// [JS] documentos> Guarda as categorias e os documentos carregados, para filtrar sem chamar a API de novo
let categorias = [];
let documentos = [];

// [JS] documentos>main>div>article>div>div>select> Monta a listinha para trocar a categoria do documento na própria ficha
function selectCategoria(documento) {
    const opcoes = categorias
        .map((c) => `<option value="${c.id}"${c.id === documento.categoria_id ? ' selected' : ''}>${escaparHtml(c.nome)}</option>`)
        .join('');

    return `<select class="select-categoria" data-doc="${documento.id}">${opcoes}</select>`;
}

// [JS] documentos>main>div>article> Monta a ficha do documento: nome padronizado, categoria, cliente, tamanho, link do processo e botões
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

// [JS] documentos>main>div> Desenha a lista de fichas ou a caixa de "nenhum documento"
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

// [JS] documentos>main>div>form> Filtra os documentos pelo nome, cliente ou categoria
function filtrar(termo) {
    const t = termo.toLowerCase();
    return documentos.filter((d) =>
        (d.nome_padronizado || '').toLowerCase().includes(t) ||
        (d.cliente_nome || '').toLowerCase().includes(t) ||
        (d.categoria_nome || '').toLowerCase().includes(t)
    );
}

// [JS] documentos>main>div> Busca categorias e documentos na API e desenha a lista (aplicando o filtro, se houver)
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

// [JS] documentos>main>div>form> Ao enviar o filtro, redesenha só os documentos que batem
tela.formBusca.addEventListener('submit', (evento) => {
    evento.preventDefault();
    const termo = tela.campoBusca.value.trim();
    desenhar(termo ? filtrar(termo) : documentos);
});

// [JS] documentos>main>div>button> Ver todos: limpa o filtro e mostra tudo
tela.botaoLimpar.addEventListener('click', () => {
    tela.campoBusca.value = '';
    desenhar(documentos);
});

// [JS] documentos>main>div>label>input> Marcar ou desmarcar Mostrar excluídos recarrega a lista
tela.mostrarExcluidos.addEventListener('change', carregar);

// [JS] documentos>main>div> Trocar a categoria numa ficha salva a correção na API
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

// [JS] documentos>main>div> Cliques nas fichas: Baixar faz o download, Excluir pede confirmação, Restaurar desfaz a exclusão
tela.lista.addEventListener('click', async (evento) => {
    const excluir = evento.target.closest('[data-excluir]');
    const restaurar = evento.target.closest('[data-restaurar]');
    const baixar = evento.target.closest('[data-baixar]');

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

// [JS] documentos> Carrega o acervo assim que a página abre
carregar();
