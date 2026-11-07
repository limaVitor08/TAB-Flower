/*
==============================================================================
SEÇÃO COMENTÁRIOS — processo-detalhe.js: Lógica da página processo-detalhe.html: Detalhe do processo: dados, marcadores, situação, documentos, checklist e histórico
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
processo-detalhe> tela: Atalhos para os elementos do detalhe do processo
processo-detalhe>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
processo-detalhe>main>h1> tela.titulo: Troca pelo título do processo vindo da API
processo-detalhe>main>p> tela.numero: Escreve o número do processo vindo da API
processo-detalhe>main>section> tela.dados: Desenha situação, cliente, advogado, tipo, comarca, valor, datas e descrição
processo-detalhe>main>div>a> tela.linkEditar: Coloca o link certo para o formulário de edição deste processo
processo-detalhe>main>section>div>select> tela.selectStatus: Recebe as situações da API e marca a atual
processo-detalhe>main>section>div>input> tela.observacao: Lê a observação e limpa depois de salvar
processo-detalhe>main>section>div>button> tela.botaoStatus: Muda a fase do processo e recarrega a página
processo-detalhe>main>div>section>ul> tela.checklist: Desenha cada item com bolinha verde (entregue) ou vermelha (pendente)
processo-detalhe>main>div>section>p> tela.resumoChecklist: Escreve quantos documentos faltam
processo-detalhe>main>div>section>ol> tela.historico: Desenha cada mudança com data, fases e observação
processo-detalhe>main>section>form> tela.formUpload: Ao enviar, faz o upload e avisa se o processo avançou de fase sozinho
processo-detalhe>main>section>form>select> tela.categoriaDocumento: Recebe as categorias da API
processo-detalhe>main>section>form>input> tela.arquivo: Pega o arquivo escolhido para enviar
processo-detalhe>main>section>form>button> tela.botaoEnviar: Mostra "Enviando..." enquanto o arquivo sobe
processo-detalhe>main>section>ul> tela.documentos: Desenha cada documento com botões Baixar e Excluir
processo-detalhe>main>section>div>select> tela.selectMarcador: Recebe Urgente, Prioridade e Prazo curto da API
processo-detalhe>main>section>div>button> tela.botaoMarcador: Aplica o marcador escolhido e redesenha os selos
processo-detalhe>main>section>div> tela.marcadores: Desenha um selo colorido por marcador, com um × para remover
processo-detalhe> idProcesso: Lê o ?id= da URL para saber qual processo mostrar
processo-detalhe>main>section> desenharDados(): Escreve título e número, ajusta o link de editar e desenha a grade de dados do processo
processo-detalhe>main>div>section>ul> desenharChecklist(): Desenha o checklist: bolinha verde se entregue, vermelha se pendente, e selo "Opcional"
processo-detalhe>main>div>section>ol> desenharHistorico(): Desenha a linha do tempo com data, mudança de fase e observação
processo-detalhe>main> carregar(): Carrega tudo do processo: dados, checklist, histórico, categorias, documentos, marcadores e situações
processo-detalhe>main>section>div>button> tela.botaoStatus (click): Atualizar situação: envia a nova fase com a observação e recarrega
processo-detalhe>main>section>ul> desenharDocumentos(): Desenha a lista de documentos anexados com nome padronizado, tamanho e botões
processo-detalhe>main>section>ul> carregarDocumentos(): Busca na API os documentos deste processo
processo-detalhe>main>section>form>select> carregarCategorias(): Preenche a lista de categorias de documento
processo-detalhe>main>section>form> tela.formUpload (submit): Envia o arquivo; avisa o nome dado pelo sistema e se o processo avançou de fase sozinho
processo-detalhe>main>section>ul> tela.documentos (click): Cliques na lista de documentos: Baixar faz o download; Excluir pede confirmação e avisa se o processo voltou de fase
processo-detalhe>main>section>div> desenharMarcadores(): Desenha os selos coloridos dos marcadores aplicados, cada um com um × para remover
processo-detalhe>main>section>div>select> carregarMarcadores(): Busca os marcadores disponíveis e os já aplicados
processo-detalhe>main>section>div>button> tela.botaoMarcador (click): Aplicar marcador: aplica o escolhido e redesenha os selos
processo-detalhe>main>section>div> tela.marcadores (click): Clique no × de um selo apaga o aviso anterior e remove o marcador
processo-detalhe> carregar(): Carrega o processo assim que a página abre
==============================================================================
*/

const tela = {
    aviso: document.getElementById('aviso'),
    titulo: document.getElementById('titulo'),
    numero: document.getElementById('numero'),
    dados: document.getElementById('dados'),
    linkEditar: document.getElementById('link-editar'),
    selectStatus: document.getElementById('novo-status'),
    observacao: document.getElementById('observacao-status'),
    botaoStatus: document.getElementById('botao-status'),
    checklist: document.getElementById('checklist'),
    resumoChecklist: document.getElementById('resumo-checklist'),
    historico: document.getElementById('historico'),
    formUpload: document.getElementById('form-upload'),
    categoriaDocumento: document.getElementById('categoria-documento'),
    arquivo: document.getElementById('arquivo'),
    botaoEnviar: document.getElementById('botao-enviar'),
    documentos: document.getElementById('documentos'),
    selectMarcador: document.getElementById('novo-marcador'),
    botaoMarcador: document.getElementById('botao-marcador'),
    marcadores: document.getElementById('marcadores')
};

const idProcesso = new URLSearchParams(window.location.search).get('id');

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

async function carregar() {
    if (!idProcesso) {
        mostrarAviso(tela.aviso, 'Nenhum processo informado no endereço.');
        tela.titulo.textContent = 'Processo não informado';
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

async function carregarDocumentos() {
    try {
        const docs = await api.documentos.listar({ processoId: idProcesso });
        desenharDocumentos(docs);
    } catch (erro) {
        tela.documentos.innerHTML =
            `<li class="dica">${escaparHtml(erro.message)}</li>`;
    }
}

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

tela.marcadores.addEventListener('click', async (evento) => {
    const botao = evento.target.closest('[data-remover-marcador]');
    if (!botao) {
        return;
    }

    limparAviso(tela.aviso);

    try {
        const aplicados = await api.processos.removerMarcador(
            idProcesso, botao.dataset.removerMarcador
        );
        desenharMarcadores(aplicados);
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
});

carregar();
