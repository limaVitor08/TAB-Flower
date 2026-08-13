/* =====================================================================
   TabFlower - Cadastro e edicao de processo
   =====================================================================
   A mesma tela serve para os dois casos: com ?id=1 na URL, entra em
   modo de edicao.

   Ao cadastrar, o backend monta sozinho o checklist de documentos
   obrigatórios do tipo escolhido (Funcionalidade 11).
   ===================================================================== */

const campos = {
    numero: document.getElementById('numero_processo'),
    titulo: document.getElementById('titulo_processo'),
    cliente: document.getElementById('cliente_id'),
    advogado: document.getElementById('advogado_id'),
    tipo: document.getElementById('tipo_processo_id'),
    status: document.getElementById('status_id'),
    dataAbertura: document.getElementById('data_abertura'),
    prazoFinal: document.getElementById('prazo_final'),
    comarca: document.getElementById('comarca'),
    valorCausa: document.getElementById('valor_causa'),
    descricao: document.getElementById('descricao')
};

const tela = {
    form: document.getElementById('form-processo'),
    aviso: document.getElementById('aviso'),
    titulo: document.getElementById('titulo'),
    subtitulo: document.getElementById('subtitulo'),
    botaoSalvar: document.getElementById('botao-salvar'),
    dicaNumero: document.getElementById('dica-numero')
};

/* Mascara do número do processo (padrão CNJ).
   Formatação e coisa de tela: o valor digitado com pontuação e enviado
   assim mesmo, porque o número do processo e um identificador oficial e
   o escritório o consulta nesse formato. */
aplicarMascara(campos.numero, formatarNumeroProcesso);

const idProcesso = new URLSearchParams(window.location.search).get('id');
const modoEdicao = Boolean(idProcesso);

/** Preenche um select com uma lista de itens. */
function preencherSelect(select, itens, vazio = null) {
    select.innerHTML = '';

    if (vazio) {
        const opcao = document.createElement('option');
        opcao.value = '';
        opcao.textContent = vazio;
        select.appendChild(opcao);
    }

    itens.forEach((item) => {
        const opcao = document.createElement('option');
        opcao.value = item.id;
        opcao.textContent = item.nome;
        select.appendChild(opcao);
    });
}

/** Carrega tudo que os selects precisam antes de liberar o formulario. */
async function carregarOpcoes() {
    const [opcoes, clientes] = await Promise.all([
        api.processos.opcoes(),
        api.clientes.listar()
    ]);

    preencherSelect(campos.cliente, clientes, 'Selecione o cliente');
    preencherSelect(campos.tipo, opcoes.tipos, 'Selecione o tipo');
    preencherSelect(campos.status, opcoes.status);
    preencherSelect(campos.advogado, opcoes.advogados, 'Selecione o advogado');

    // Sem advogado cadastrado não da para abrir processo nenhum.
    if (opcoes.advogados.length === 0) {
        mostrarAviso(
            tela.aviso,
            'Nenhum usuário com perfil de Advogado está cadastrado. ' +
            'Cadastre um advogado antes de abrir processos.'
        );
        tela.botaoSalvar.disabled = true;
    }

    if (clientes.length === 0) {
        mostrarAviso(
            tela.aviso,
            'Nenhum cliente ativo cadastrado. Cadastre o cliente primeiro.'
        );
        tela.botaoSalvar.disabled = true;
    }
}

async function prepararTela() {
    try {
        await carregarOpcoes();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        tela.botaoSalvar.disabled = true;
        return;
    }

    if (!modoEdicao) {
        // Cadastro novo abre com a data de hoje já preenchida.
        campos.dataAbertura.value = new Date().toISOString().split('T')[0];
        return;
    }

    tela.titulo.textContent = 'Editar processo';
    tela.subtitulo.textContent =
        'O número da ação e o tipo ficam bloqueados. A situação muda pela tela de detalhe.';
    tela.botaoSalvar.textContent = 'Salvar alterações';

    campos.numero.disabled = true;
    campos.tipo.disabled = true;
    campos.cliente.disabled = true;
    campos.status.disabled = true;
    // A data de abertura e dado histórico do processo, como o número da
    // acao. Ela ficava habilitada mas não era enviada no salvamento: a
    // pessoa alterava, lia "salvo com sucesso" e nada mudava. Travar o
    // campo e coerente com os outros e não engana ninguem.
    campos.dataAbertura.disabled = true;
    tela.dicaNumero.textContent = 'Este campo não pode ser alterado.';

    try {
        const processo = await api.processos.buscarPorId(idProcesso);

        campos.numero.value = processo.numero_processo;
        campos.titulo.value = processo.titulo;
        campos.cliente.value = processo.cliente_id;
        campos.advogado.value = processo.advogado_id;
        campos.tipo.value = processo.tipo_processo_id;
        campos.status.value = processo.status_id;
        campos.dataAbertura.value = processo.data_abertura || '';
        campos.prazoFinal.value = processo.prazo_final || '';
        campos.comarca.value = processo.comarca || '';
        campos.valorCausa.value = processo.valor_causa || '';
        campos.descricao.value = processo.descricao || '';
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        tela.botaoSalvar.disabled = true;
    }
}

function coletarDados() {
    const dados = {
        titulo: campos.titulo.value.trim(),
        descricao: campos.descricao.value.trim(),
        advogado_id: Number(campos.advogado.value) || null,
        comarca: campos.comarca.value.trim(),
        valor_causa: campos.valorCausa.value ? Number(campos.valorCausa.value) : null,
        prazo_final: campos.prazoFinal.value || null
    };

    // Campos travados na edicao só vao no cadastro.
    if (!modoEdicao) {
        dados.numero_processo = campos.numero.value.trim();
        dados.cliente_id = Number(campos.cliente.value) || null;
        dados.tipo_processo_id = Number(campos.tipo.value) || null;
        dados.status_id = Number(campos.status.value) || null;
        dados.data_abertura = campos.dataAbertura.value || null;
    }

    return dados;
}

tela.form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparAviso(tela.aviso);

    tela.botaoSalvar.disabled = true;
    tela.botaoSalvar.textContent = 'Salvando...';

    try {
        const dados = coletarDados();

        if (modoEdicao) {
            await api.processos.atualizar(idProcesso, dados);
            window.location.href = 'processo-detalhe.html?id=' + idProcesso;
        } else {
            const criado = await api.processos.criar(dados);
            window.location.href = 'processo-detalhe.html?id=' + criado.id;
        }
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        window.scrollTo({ top: 0, behavior: 'smooth' });
        tela.botaoSalvar.disabled = false;
        tela.botaoSalvar.textContent = modoEdicao
            ? 'Salvar alterações'
            : 'Cadastrar processo';
    }
});

prepararTela();
