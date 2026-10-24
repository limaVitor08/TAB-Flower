// [JS] processo-form> Atalhos para os campos do formulário de processo
const campos = {
    // [JS] processo-form>main>form>div>div>input> Formata o número enquanto digita; fica bloqueado na edição
    numero: document.getElementById('numero_processo'),
    // [JS] processo-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    titulo: document.getElementById('titulo_processo'),
    // [JS] processo-form>main>form>div>div>select> Recebe os clientes ativos da API; fica bloqueada na edição
    cliente: document.getElementById('cliente_id'),
    // [JS] processo-form>main>form>div>div>select> Recebe os advogados da API; avisa se não houver nenhum
    advogado: document.getElementById('advogado_id'),
    // [JS] processo-form>main>form>div>div>select> Recebe os tipos da API; fica bloqueada na edição
    tipo: document.getElementById('tipo_processo_id'),
    // [JS] processo-form>main>form>div>div>select> Recebe as situações da API; fica bloqueada na edição
    status: document.getElementById('status_id'),
    // [JS] processo-form>main>form>div>div>input> Já vem com a data de hoje no cadastro; fica bloqueado na edição
    dataAbertura: document.getElementById('data_abertura'),
    // [JS] processo-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    prazoFinal: document.getElementById('prazo_final'),
    // [JS] processo-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    comarca: document.getElementById('comarca'),
    // [JS] processo-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    valorCausa: document.getElementById('valor_causa'),
    // [JS] processo-form>main>form>div>div>textarea> Preenchida na edição e enviada ao salvar
    descricao: document.getElementById('descricao')
};

// [JS] processo-form> Atalhos para título, formulário, avisos e botão
const tela = {
    // [JS] processo-form>main>form> Ao enviar, cadastra ou atualiza e abre o detalhe do processo
    form: document.getElementById('form-processo'),
    // [JS] processo-form>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] processo-form>main>h1> Troca para "Editar processo" quando a página abre com ?id=
    titulo: document.getElementById('titulo'),
    // [JS] processo-form>main>p> Troca o texto no modo de edição
    subtitulo: document.getElementById('subtitulo'),
    // [JS] processo-form>main>form>div>button> Troca para "Salvar alterações" na edição e mostra "Salvando..." enquanto espera
    botaoSalvar: document.getElementById('botao-salvar'),
    // [JS] processo-form>main>form>div>div>span> Muda o texto da dica no modo de edição
    dicaNumero: document.getElementById('dica-numero')
};

// [JS] processo-form>main>form>div>div>input> Formata o número do processo enquanto digita
aplicarMascara(campos.numero, formatarNumeroProcesso);

// [JS] processo-form> Lê o ?id= da URL: com id a tela edita, sem id cadastra
const idProcesso = new URLSearchParams(window.location.search).get('id');
const modoEdicao = Boolean(idProcesso);

// [JS] processo-form>main>form>div>div>select> Coloca as opções dentro de uma lista (select)
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

// [JS] processo-form>main>form>div>div>select> Busca clientes, tipos, situações e advogados e preenche as listas; avisa se faltar advogado ou cliente
async function carregarOpcoes() {
    const [opcoes, clientes] = await Promise.all([
        api.processos.opcoes(),
        api.clientes.listar()
    ]);

    preencherSelect(campos.cliente, clientes, 'Selecione o cliente');
    preencherSelect(campos.tipo, opcoes.tipos, 'Selecione o tipo');
    preencherSelect(campos.status, opcoes.status);
    preencherSelect(campos.advogado, opcoes.advogados, 'Selecione o advogado');

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

// [JS] processo-form>main> Prepara a tela: no cadastro põe a data de hoje; na edição bloqueia campos fixos e preenche com os dados do processo
async function prepararTela() {
    try {
        await carregarOpcoes();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        tela.botaoSalvar.disabled = true;
        return;
    }

    if (!modoEdicao) {
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

// [JS] processo-form>main>form> Junta os valores dos campos para enviar à API (campos fixos só no cadastro)
function coletarDados() {
    const dados = {
        titulo: campos.titulo.value.trim(),
        descricao: campos.descricao.value.trim(),
        advogado_id: Number(campos.advogado.value) || null,
        comarca: campos.comarca.value.trim(),
        valor_causa: campos.valorCausa.value ? Number(campos.valorCausa.value) : null,
        prazo_final: campos.prazoFinal.value || null
    };

    if (!modoEdicao) {
        dados.numero_processo = campos.numero.value.trim();
        dados.cliente_id = Number(campos.cliente.value) || null;
        dados.tipo_processo_id = Number(campos.tipo.value) || null;
        dados.status_id = Number(campos.status.value) || null;
        dados.data_abertura = campos.dataAbertura.value || null;
    }

    return dados;
}

// [JS] processo-form>main>form> Ao salvar: cadastra ou atualiza e abre o detalhe do processo; se der erro, mostra a mensagem no topo
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

// [JS] processo-form> Prepara a tela assim que a página abre
prepararTela();
