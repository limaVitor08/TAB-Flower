// [JS] processo-detalhe> Atalhos para os elementos do detalhe do processo
const tela = {
    // [JS] processo-detalhe>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] processo-detalhe>main>h1> Troca pelo título do processo vindo da API
    titulo: document.getElementById('titulo'),
    // [JS] processo-detalhe>main>p> Escreve o número do processo vindo da API
    numero: document.getElementById('numero'),
    // [JS] processo-detalhe>main>section> Desenha situação, cliente, advogado, tipo, comarca, valor, datas e descrição
    dados: document.getElementById('dados'),
    // [JS] processo-detalhe>main>div>a> Coloca o link certo para o formulário de edição deste processo
    linkEditar: document.getElementById('link-editar'),
    // [JS] processo-detalhe>main>section>div>select> Recebe as situações da API e marca a atual
    selectStatus: document.getElementById('novo-status'),
    // [JS] processo-detalhe>main>section>div>input> Lê a observação e limpa depois de salvar
    observacao: document.getElementById('observacao-status'),
    // [JS] processo-detalhe>main>section>div>button> Muda a fase do processo e recarrega a página
    botaoStatus: document.getElementById('botao-status'),
    // [JS] processo-detalhe>main>div>section>ul> Desenha cada item com bolinha verde (entregue) ou vermelha (pendente)
    checklist: document.getElementById('checklist'),
    // [JS] processo-detalhe>main>div>section>p> Escreve quantos documentos faltam
    resumoChecklist: document.getElementById('resumo-checklist'),
    // [JS] processo-detalhe>main>div>section>ol> Desenha cada mudança com data, fases e observação
    historico: document.getElementById('historico'),
    // [JS] processo-detalhe>main>section>form> Ao enviar, faz o upload e avisa se o processo avançou de fase sozinho
    formUpload: document.getElementById('form-upload'),
    // [JS] processo-detalhe>main>section>form>select> Recebe as categorias da API
    categoriaDocumento: document.getElementById('categoria-documento'),
    // [JS] processo-detalhe>main>section>form>input> Pega o arquivo escolhido para enviar
    arquivo: document.getElementById('arquivo'),
    // [JS] processo-detalhe>main>section>form>button> Mostra "Enviando..." enquanto o arquivo sobe
    botaoEnviar: document.getElementById('botao-enviar'),
    // [JS] processo-detalhe>main>section>ul> Desenha cada documento com botões Baixar e Excluir
    documentos: document.getElementById('documentos'),
    // [JS] processo-detalhe>main>section>div>select> Recebe Urgente, Prioridade e Prazo curto da API
    selectMarcador: document.getElementById('novo-marcador'),
    // [JS] processo-detalhe>main>section>div>button> Aplica o marcador escolhido e redesenha os selos
    botaoMarcador: document.getElementById('botao-marcador'),
    // [JS] processo-detalhe>main>section>div> Desenha um selo colorido por marcador, com um × para remover
    marcadores: document.getElementById('marcadores')
};

// [JS] processo-detalhe> Lê o ?id= da URL para saber qual processo mostrar
const idProcesso = new URLSearchParams(window.location.search).get('id');

// [JS] processo-detalhe>main>section> Escreve título e número, ajusta o link de editar e desenha a grade de dados do processo
function desenharDados(p) {
    tela.titulo.textContent = p.titulo;
    tela.numero.textContent = p.numero_processo;
    tela.linkEditar.href = 'processo-form.html?id=' + p.id;

    const cor = p.status_cor || '#6b7280';

    const itens = [
        ['Situação', `<span class="etiqueta-status" style="background-color:${cor}">${escaparHtml(p.status_nome)}</span>`],
        ['Cliente', escaparHtml(p.cliente_nome)],
        ['Advogado responsável', escaparHtml(p.advogado_nome)],
        ['Tipo', escaparHtml(p.tipo_nome)],
        ['Comarca', escaparHtml(p.comarca) || '\u2014'],
        ['Valor da causa', formatarDinheiro(p.valor_causa)],
        ['Aberto em', formatarData(p.data_abertura)],
        ['Prazo final', formatarData(p.prazo_final)],
        ['Situação do registro', p.ativo ? 'Ativo' : 'Arquivado']
    ];

    tela.dados.innerHTML = `
        <h2 class="titulo-secao">Dados do processo</h2>
        <div class="grade-dados" style="margin-top:14px">
            ${itens.map(([rotulo, valor]) => `
                <div class="dado">
                    <span class="dado-rotulo">${rotulo}</span>
                    <span class="dado-valor">${valor}</span>
                </div>
            `).join('')}
        </div>
        ${p.descricao ? `<p style="margin-top:16px">${escaparHtml(p.descricao)}</p>` : ''}
    `;
}

// [JS] processo-detalhe>main>div>section>ul> Desenha o checklist: bolinha verde se entregue, vermelha se pendente, e selo "Opcional"
function desenharChecklist(itens) {
    if (itens.length === 0) {
        tela.resumoChecklist.textContent =
            'Este tipo de processo não tem documentos obrigatórios configurados.';
        tela.checklist.innerHTML = '';
        return;
    }

    const entregues = itens.filter((i) => i.entregue).length;
    const pendentes = itens.length - entregues;

    tela.resumoChecklist.textContent = pendentes === 0
        ? `Documentação completa: ${itens.length} de ${itens.length} entregues.`
        : `${pendentes} de ${itens.length} documentos ainda pendentes.`;

    tela.checklist.innerHTML = itens.map((item) => `
        <li class="${item.entregue ? 'entregue' : ''}">
            <span class="marca-item">${item.entregue ? '\u2713' : '!'}</span>
            <span>${escaparHtml(item.categoria_nome)}</span>
            ${item.obrigatorio
                ? ''
                : '<span class="etiqueta etiqueta-cinza">Opcional</span>'}
        </li>
    `).join('');
}

// [JS] processo-detalhe>main>div>section>ol> Desenha a linha do tempo com data, mudança de fase e observação
function desenharHistorico(registros) {
    if (registros.length === 0) {
        tela.historico.innerHTML = '<li class="dica">Nenhuma mudança registrada.</li>';
        return;
    }

    tela.historico.innerHTML = registros.map((r) => {
        const mudanca = r.status_anterior
            ? `${escaparHtml(r.status_anterior)} \u2192 ${escaparHtml(r.status_novo)}`
            : escaparHtml(r.status_novo);

        const quando = r.criado_em
            ? new Date(r.criado_em).toLocaleString('pt-BR')
            : '';

        return `
            <li>
                <span class="historico-data">${quando}</span>
                <div class="historico-mudanca">${mudanca}</div>
                ${r.observacao
                    ? `<div class="historico-obs">${escaparHtml(r.observacao)}</div>`
                    : ''}
            </li>
        `;
    }).join('');
}

// [JS] processo-detalhe>main> Carrega tudo do processo: dados, checklist, histórico, categorias, documentos, marcadores e situações
async function carregar() {
    if (!idProcesso) {
        mostrarAviso(tela.aviso, 'Nenhum processo informado no endereço.');
        return;
    }

    try {
        const [processo, itens, registros] = await Promise.all([
            api.processos.buscarPorId(idProcesso),
            api.processos.checklist(idProcesso),
            api.processos.historico(idProcesso)
        ]);

        desenharDados(processo);
        desenharChecklist(itens);
        desenharHistorico(registros);

        await carregarCategorias();
        await carregarDocumentos();
        await carregarMarcadores();

        const opcoes = await api.processos.opcoes();
        tela.selectStatus.innerHTML = opcoes.status
            .map((s) => `<option value="${s.id}"${s.id === processo.status_id ? ' selected' : ''}>${escaparHtml(s.nome)}</option>`)
            .join('');

    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        tela.titulo.textContent = 'Processo não encontrado';
    }
}

// [JS] processo-detalhe>main>section>div>button> Atualizar situação: envia a nova fase com a observação e recarrega
tela.botaoStatus.addEventListener('click', async () => {
    limparAviso(tela.aviso);
    tela.botaoStatus.disabled = true;

    try {
        await api.processos.atualizarStatus(idProcesso, {
            status_id: Number(tela.selectStatus.value),
            observacao: tela.observacao.value.trim()
        });

        tela.observacao.value = '';
        mostrarAviso(tela.aviso, 'Situação atualizada e registrada no histórico.', 'sucesso');
        await carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    } finally {
        tela.botaoStatus.disabled = false;
    }
});

// [JS] processo-detalhe>main>section>ul> Desenha a lista de documentos anexados com nome padronizado, tamanho e botões
function desenharDocumentos(docs) {
    if (docs.length === 0) {
        tela.documentos.innerHTML =
            '<li class="dica">Nenhum documento anexado ainda.</li>';
        return;
    }

    tela.documentos.innerHTML = docs.map((d) => `
        <li>
            <span class="marca-item" style="background-color:var(--folha-clara);
                  color:var(--folha); border-color:var(--folha)">\u2713</span>
            <span style="flex:1">
                <strong>${escaparHtml(d.categoria_nome)}</strong>
                <br>
                <span class="mono" style="font-size:0.82rem; color:var(--tinta-clara)">
                    ${escaparHtml(d.nome_padronizado)}
                </span>
            </span>
            <span class="dica">${formatarTamanho(d.tamanho_kb)}</span>
            <a href="#" data-baixar="${d.id}"
               data-nome="${escaparHtml(d.nome_padronizado)}"
               class="botao botao-pequeno">Baixar</a>
            <button type="button" class="botao botao-pequeno botao-perigo"
                    data-excluir-doc="${d.id}">Excluir</button>
        </li>
    `).join('');
}

// [JS] processo-detalhe>main>section>ul> Busca na API os documentos deste processo
async function carregarDocumentos() {
    try {
        const docs = await api.documentos.listar({ processoId: idProcesso });
        desenharDocumentos(docs);
    } catch (erro) {
        tela.documentos.innerHTML =
            `<li class="dica">${escaparHtml(erro.message)}</li>`;
    }
}

// [JS] processo-detalhe>main>section>form>select> Preenche a lista de categorias de documento
async function carregarCategorias() {
    try {
        const categorias = await api.documentos.categorias();
        tela.categoriaDocumento.innerHTML =
            '<option value="">Categoria do documento</option>' +
            categorias
                .map((c) => `<option value="${c.id}">${escaparHtml(c.nome)}</option>`)
                .join('');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] processo-detalhe>main>section>form> Envia o arquivo; avisa o nome dado pelo sistema e se o processo avançou de fase sozinho
tela.formUpload.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparAviso(tela.aviso);

    tela.botaoEnviar.disabled = true;
    tela.botaoEnviar.textContent = 'Enviando...';

    const dados = new FormData();
    dados.append('arquivo', tela.arquivo.files[0]);
    dados.append('categoria_id', tela.categoriaDocumento.value);
    dados.append('processo_id', idProcesso);

    try {
        const doc = await api.documentos.enviar(dados);

        let mensagem =
            `Documento anexado como ${doc.nome_padronizado}. ` +
            'O advogado responsável foi notificado.';

        if (doc.avanco_status) {
            mensagem +=
                ` Como esta era a última pendência obrigatória, o processo ` +
                `avançou automaticamente para "${doc.avanco_status}".`;
        }

        mostrarAviso(tela.aviso, mensagem, 'sucesso');

        tela.formUpload.reset();
        await carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    } finally {
        tela.botaoEnviar.disabled = false;
        tela.botaoEnviar.textContent = 'Anexar';
    }
});

// [JS] processo-detalhe>main>section>ul> Cliques na lista de documentos: Baixar faz o download; Excluir pede confirmação e avisa se o processo voltou de fase
tela.documentos.addEventListener('click', async (evento) => {
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

    const botao = evento.target.closest('[data-excluir-doc]');
    if (!botao) {
        return;
    }

    const confirmou = confirm(
        'Excluir este documento?\n\n' +
        'Somente o Administrador pode fazer isso. O arquivo continua no ' +
        'servidor e o registro fica no banco com a marca de exclusão, ' +
        'junto com quem excluiu e quando.'
    );

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await api.documentos.excluir(
            botao.dataset.excluirDoc
        );

        let mensagem = resposta.mensagem;

        if (resposta.retorno_status) {
            mensagem +=
                ` A pendência do checklist reabriu, então o processo ` +
                `voltou para "${resposta.retorno_status}".`;
        }

        mostrarAviso(tela.aviso, mensagem, 'sucesso');
        await carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
});

// [JS] processo-detalhe>main>section>div> Desenha os selos coloridos dos marcadores aplicados, cada um com um × para remover
function desenharMarcadores(aplicados) {
    if (aplicados.length === 0) {
        tela.marcadores.innerHTML =
            '<span class="dica">Nenhum marcador aplicado.</span>';
        return;
    }

    tela.marcadores.innerHTML = aplicados.map((m) => `
        <span class="selo" style="background-color:${m.cor_hex || '#6b7280'};
              display:inline-flex; align-items:center; gap:6px">
            ${escaparHtml(m.nome)}
            <button type="button" data-remover-marcador="${m.id}"
                    title="Remover marcador"
                    style="background:none; border:none; color:#fff;
                           cursor:pointer; font-size:0.9rem; padding:0">
                &times;
            </button>
        </span>`).join('');
}

// [JS] processo-detalhe>main>section>div>select> Busca os marcadores disponíveis e os já aplicados
async function carregarMarcadores() {
    try {
        const [disponiveis, aplicados] = await Promise.all([
            api.painel.marcadores(),
            api.processos.marcadores(idProcesso)
        ]);

        tela.selectMarcador.innerHTML = disponiveis
            .map((m) => `<option value="${m.id}">${escaparHtml(m.nome)}</option>`)
            .join('');

        desenharMarcadores(aplicados);
    } catch (erro) {
        tela.marcadores.innerHTML =
            `<span class="dica">${escaparHtml(erro.message)}</span>`;
    }
}

// [JS] processo-detalhe>main>section>div>button> Aplicar marcador: aplica o escolhido e redesenha os selos
tela.botaoMarcador.addEventListener('click', async () => {
    limparAviso(tela.aviso);
    tela.botaoMarcador.disabled = true;

    try {
        const aplicados = await api.processos.aplicarMarcador(
            idProcesso, Number(tela.selectMarcador.value)
        );
        desenharMarcadores(aplicados);
        mostrarAviso(tela.aviso, 'Marcador aplicado.', 'sucesso');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    } finally {
        tela.botaoMarcador.disabled = false;
    }
});

// [JS] processo-detalhe>main>section>div> Clique no × de um selo remove o marcador
tela.marcadores.addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-remover-marcador]');
    if (!botao) {
        return;
    }

    try {
        const aplicados = await api.processos.removerMarcador(
            idProcesso, botao.dataset.removerMarcador
        );
        desenharMarcadores(aplicados);
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
});

// [JS] processo-detalhe> Carrega o processo assim que a página abre
carregar();
