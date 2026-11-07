/*
==============================================================================
SEÇÃO COMENTÁRIOS — processo-form.js: Lógica da página processo-form.html: Cadastro e edição de processo
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
processo-form> campos: Atalhos para os campos do formulário de processo
processo-form>main>form>div>div>input> campos.numero: Formata o número enquanto digita; fica bloqueado na edição
processo-form>main>form>div>div>input> campos.titulo: Preenchido na edição e enviado ao salvar
processo-form>main>form>div>div>select> campos.cliente: Recebe os clientes ativos da API; fica bloqueada na edição
processo-form>main>form>div>div>select> campos.advogado: Recebe os advogados da API; avisa se não houver nenhum
processo-form>main>form>div>div>select> campos.tipo: Recebe os tipos da API; fica bloqueada na edição
processo-form>main>form>div>div>select> campos.status: Recebe as situações da API; fica bloqueada na edição
processo-form>main>form>div>div>input> campos.dataAbertura: Já vem com a data de hoje no cadastro; fica bloqueado na edição
processo-form>main>form>div>div>input> campos.prazoFinal: Preenchido na edição e enviado ao salvar
processo-form>main>form>div>div>input> campos.comarca: Preenchido na edição e enviado ao salvar
processo-form>main>form>div>div>input> campos.valorCausa: Preenchido na edição e enviado ao salvar
processo-form>main>form>div>div>textarea> campos.descricao: Preenchida na edição e enviada ao salvar
processo-form> tela: Atalhos para título, formulário, avisos e botão
processo-form>main>form> tela.form: Ao enviar, cadastra ou atualiza e abre o detalhe do processo
processo-form>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
processo-form>main>h1> tela.titulo: Troca para "Editar processo" quando a página abre com ?id=
processo-form>main>p> tela.subtitulo: Troca o texto no modo de edição
processo-form>main>form>div>button> tela.botaoSalvar: Troca para "Salvar alterações" na edição e mostra "Salvando..." enquanto espera
processo-form>main>form>div>div>span> tela.dicaNumero: Muda o texto da dica no modo de edição
processo-form>main>form>div>div>input> aplicarMascara(): Formata o número do processo enquanto digita
processo-form> idProcesso: Lê o ?id= da URL: com id a tela edita, sem id cadastra
processo-form>main>form>div>div>select> preencherSelect(): Coloca as opções dentro de uma lista (select)
processo-form>main>form>div>div>select> carregarOpcoes(): Busca clientes, tipos, situações e advogados e preenche as listas; avisa se faltar advogado ou cliente
processo-form>main> prepararTela(): Prepara a tela: no cadastro põe a data de hoje; na edição bloqueia campos fixos e preenche com os dados do processo
processo-form>main>form> coletarDados(): Junta os valores dos campos para enviar à API (campos fixos só no cadastro)
processo-form>main>form> tela.form (submit): Ao salvar: cadastra ou atualiza e abre o detalhe do processo; se der erro, mostra a mensagem no topo
processo-form> prepararTela(): Prepara a tela assim que a página abre
==============================================================================
*/

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

aplicarMascara(campos.numero, formatarNumeroProcesso);

const idProcesso = new URLSearchParams(window.location.search).get('id');
const modoEdicao = Boolean(idProcesso);

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
        campos.valorCausa.value = processo.valor_causa ?? '';
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
