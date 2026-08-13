/* =====================================================================
   TabFlower - Detalhe do processo
   =====================================================================
   Esta e a tela que substitui a pasta física com etiquetas. Reune:

     07 - Atualizacao de Status (com registro no histórico)
     11 - Checklist Obrigatório
     12 - Mapeamento de Pendências
   ===================================================================== */

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

/* Sem tela de login, o sistema ainda não sabe quem esta operando.
   O autor das ações que exigem permissão vem da sessão, no backend,
   a partir do token - a tela não informa mais nenhum id de usuário. */

const idProcesso = new URLSearchParams(window.location.search).get('id');

/* ---------------------------------------------------------------------
   Dados do processo
   --------------------------------------------------------------------- */

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

/* ---------------------------------------------------------------------
   Checklist e pendências (Funcionalidades 11 e 12)
   --------------------------------------------------------------------- */

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

/* ---------------------------------------------------------------------
   Histórico (Funcionalidade 07)
   --------------------------------------------------------------------- */

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

/* ---------------------------------------------------------------------
   Carga da tela
   --------------------------------------------------------------------- */

async function carregar() {
    if (!idProcesso) {
        mostrarAviso(tela.aviso, 'Nenhum processo informado no endereço.');
        return;
    }

    try {
        // As três chamadas saem juntas, não uma esperando a outra.
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

/* --- Atualizacao de situação (Funcionalidade 07) --- */

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

/* ---------------------------------------------------------------------
   Documentos (Funcionalidades 09, 10, 16, 17 e 20)
   --------------------------------------------------------------------- */

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

    // FormData e o que permite mandar arquivo junto com os outros campos.
    const dados = new FormData();
    dados.append('arquivo', tela.arquivo.files[0]);
    dados.append('categoria_id', tela.categoriaDocumento.value);
    dados.append('processo_id', idProcesso);

    try {
        const doc = await api.documentos.enviar(dados);

        // O backend devolve avanco_status quando este anexo fechou o
        // checklist obrigatório e o processo mudou de fase sozinho.
        // A automação precisa ser dita em voz alta: se o processo pular
        // de fase calado, quem anexou acha que clicou errado.
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
        // Recarrega tudo: o checklist pode ter mudado com este anexo.
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

        // Contrapartida do avanço: a pendência reabriu e o processo
        // desceu de volta.
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

/* ---------------------------------------------------------------------
   Marcadores de prioridade (Funcionalidade 14)

   São fixos, definidos pelo sistema. O usuário aplica e remove, não cria.
   O peso de cada um e o que ordena o painel de prioridades, que roda pela
   procedure sp_processos_prioritarios.
   --------------------------------------------------------------------- */

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
