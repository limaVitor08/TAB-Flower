/*
==============================================================================
SEÇÃO COMENTÁRIOS — documentos.js: Lógica da página documentos.html: Acervo de documentos
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
documentos> tela: Atalhos para os elementos do acervo
documentos>main>div> tela.lista: Desenha cada documento com categoria editável e botões Baixar, Excluir ou Restaurar
documentos>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
documentos>main>div>form> tela.formBusca: Filtra a lista já carregada, sem chamar a API de novo
documentos>main>div>form>input> tela.campoBusca: Lê o texto do filtro
documentos>main>div>button> tela.botaoLimpar: Limpa o campo e mostra a lista completa
documentos>main>div>label>input> tela.mostrarExcluidos: Ao marcar ou desmarcar, recarrega a lista
documentos> categorias: Guarda as categorias e os documentos carregados, para filtrar sem chamar a API de novo
documentos>main>div>article>div>div>select> selectCategoria(): Monta a listinha para trocar a categoria do documento na própria ficha
documentos>main>div>article> montarFicha(): Monta a ficha do documento: nome padronizado, categoria, cliente, tamanho, link do processo e botões
documentos>main>div> desenhar(): Desenha a lista de fichas, ou avisa que o filtro não achou nada ou que o acervo está vazio
documentos>main>div>form> filtrar(): Filtra os documentos pelo nome, cliente ou categoria
documentos>main>div> carregar(): Busca categorias e documentos na API e desenha a lista (aplicando o filtro, se houver)
documentos>main>div>form> tela.formBusca (submit): Ao enviar o filtro, redesenha só os documentos que batem
documentos>main>div>button> tela.botaoLimpar (click): Ver todos: limpa o filtro e mostra tudo
documentos>main>div>label>input> tela.mostrarExcluidos (change): Marcar ou desmarcar Mostrar excluídos recarrega a lista
documentos>main>div> tela.lista (change): Trocar a categoria numa ficha salva a correção na API
documentos>main>div> tela.lista (click): Cliques nas fichas: Baixar faz o download, Excluir pede confirmação, Restaurar desfaz a exclusão e avisa se o processo avançou de fase
documentos> carregar(): Carrega o acervo assim que a página abre
==============================================================================
*/

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    formBusca: document.getElementById('form-busca'),
    campoBusca: document.getElementById('campo-busca'),
    botaoLimpar: document.getElementById('botao-limpar'),
    mostrarExcluidos: document.getElementById('mostrar-excluidos')
};

let categorias = [];
let documentos = [];

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
                        ? '<span class="etiqueta etiqueta-cinza">Excluído</span>'
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
    if (lista.length === 0 && documentos.length > 0) {
        tela.lista.innerHTML = `
            <div class="vazio">
                <strong>Nenhum documento encontrado</strong>
                Tente outro termo ou clique em Ver todos.
            </div>`;
        return;
    }
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

tela.lista.addEventListener('change', async (evento) => {
    const select = evento.target.closest('.select-categoria');
    if (!select) {
        return;
    }

    try {
        await api.documentos.atualizar(select.dataset.doc, {
            categoria_id: Number(select.value)
        });
        await carregar();
        mostrarAviso(tela.aviso, 'Categoria atualizada.', 'sucesso');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        carregar();
    }
});

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

            await carregar();
            mostrarAviso(tela.aviso, mensagem, 'sucesso');
        } catch (erro) {
            mostrarAviso(tela.aviso, erro.message);
        }
        return;
    }

    if (restaurar) {
        try {
            const r = await api.documentos.restaurar(restaurar.dataset.restaurar);

            let mensagem = r.mensagem;
            if (r.avanco_status) {
                mensagem +=
                    ` A documentação obrigatória ficou completa de novo, então ` +
                    `o processo avançou para "${r.avanco_status}".`;
            }

            await carregar();
            mostrarAviso(tela.aviso, mensagem, 'sucesso');
        } catch (erro) {
            mostrarAviso(tela.aviso, erro.message);
        }
    }
});

carregar();
