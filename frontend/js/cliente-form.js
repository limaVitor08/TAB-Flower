// [JS] cliente-form> Atalhos para os campos do formulário de cliente
const campos = {
    // [JS] cliente-form>main>form>div>div>select> Troca o exemplo do campo de documento; fica bloqueada na edição
    tipoPessoa: document.getElementById('tipo_pessoa'),
    // [JS] cliente-form>main>form>div>div>input> Formata com pontos e traço enquanto digita; fica bloqueado na edição
    documento: document.getElementById('documento'),
    // [JS] cliente-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    nome: document.getElementById('nome'),
    // [JS] cliente-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    email: document.getElementById('email'),
    // [JS] cliente-form>main>form>div>div>input> Formata como (31) 99999-9999 enquanto digita
    telefone: document.getElementById('telefone'),
    // [JS] cliente-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    endereco: document.getElementById('endereco'),
    // [JS] cliente-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    cidade: document.getElementById('cidade'),
    // [JS] cliente-form>main>form>div>div>input> Deixa só 2 letras maiúsculas enquanto digita
    estado: document.getElementById('estado'),
    // [JS] cliente-form>main>form>div>div>textarea> Preenchida na edição e enviada ao salvar
    observacao: document.getElementById('observacao')
};

// [JS] cliente-form> Atalhos para título, formulário, avisos e botão
const tela = {
    // [JS] cliente-form>main>form> Ao enviar, cadastra ou atualiza o cliente e volta para a lista
    form: document.getElementById('form-cliente'),
    // [JS] cliente-form>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] cliente-form>main>h1> Troca para "Editar cliente" quando a página abre com ?id=
    titulo: document.getElementById('titulo'),
    // [JS] cliente-form>main>p> Troca o texto no modo de edição
    subtitulo: document.getElementById('subtitulo'),
    // [JS] cliente-form>main>form>div>button> Troca para "Salvar alterações" na edição e mostra "Salvando..." enquanto espera
    botaoSalvar: document.getElementById('botao-salvar'),
    // [JS] cliente-form>main>form>div>div>span> Muda o texto da dica no modo de edição
    dicaDocumento: document.getElementById('dica-documento')
};

// [JS] cliente-form> Lê o ?id= da URL: com id a tela edita, sem id cadastra
const idCliente = new URLSearchParams(window.location.search).get('id');
const modoEdicao = Boolean(idCliente);

// [JS] cliente-form>main> No modo edição: troca títulos, bloqueia tipo e documento e preenche os campos com os dados do cliente
async function prepararTela() {
    if (!modoEdicao) {
        return;
    }

    tela.titulo.textContent = 'Editar cliente';
    tela.subtitulo.textContent =
        'O CPF/CNPJ fica bloqueado: alterar o documento burlaria o controle de duplicidade.';
    tela.botaoSalvar.textContent = 'Salvar alterações';

    campos.documento.disabled = true;
    campos.tipoPessoa.disabled = true;
    tela.dicaDocumento.textContent = 'Este campo não pode ser alterado.';

    try {
        const cliente = await api.clientes.buscarPorId(idCliente);

        campos.tipoPessoa.value = cliente.tipo_pessoa;
        campos.documento.value = cliente.documento_formatado;
        campos.nome.value = cliente.nome;
        campos.email.value = cliente.email || '';
        campos.telefone.value = cliente.telefone || '';
        campos.endereco.value = cliente.endereco || '';
        campos.cidade.value = cliente.cidade || '';
        campos.estado.value = cliente.estado || '';
        campos.observacao.value = cliente.observacao || '';
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        tela.botaoSalvar.disabled = true;
    }
}

// [JS] cliente-form>main>form>div>div>input> Liga as máscaras de documento, telefone e estado
aplicarMascara(campos.documento, formatarDocumento);
aplicarMascara(campos.telefone, formatarTelefone);
aplicarMascara(campos.estado, formatarUF);

// [JS] cliente-form>main>form>div>div>select> Ao trocar o tipo de pessoa, troca o exemplo do campo de documento
campos.tipoPessoa.addEventListener('change', () => {
    campos.documento.placeholder = campos.tipoPessoa.value === 'F'
        ? '000.000.000-00'
        : '00.000.000/0000-00';
});

// [JS] cliente-form>main>form> Junta os valores dos campos para enviar à API (documento só no cadastro)
function coletarDados() {
    const dados = {
        nome: campos.nome.value.trim(),
        email: campos.email.value.trim(),
        telefone: campos.telefone.value.trim(),
        endereco: campos.endereco.value.trim(),
        cidade: campos.cidade.value.trim(),
        estado: campos.estado.value.trim().toUpperCase(),
        observacao: campos.observacao.value.trim()
    };

    if (!modoEdicao) {
        dados.tipo_pessoa = campos.tipoPessoa.value;
        dados.documento = somenteNumeros(campos.documento.value);
    }

    return dados;
}

// [JS] cliente-form>main>form> Ao salvar: cadastra ou atualiza; deu certo volta para a lista, deu erro mostra a mensagem no topo
tela.form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparAviso(tela.aviso);

    tela.botaoSalvar.disabled = true;
    tela.botaoSalvar.textContent = 'Salvando...';

    try {
        const dados = coletarDados();

        if (modoEdicao) {
            await api.clientes.atualizar(idCliente, dados);
        } else {
            await api.clientes.criar(dados);
        }

        window.location.href = 'clientes.html';

    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        window.scrollTo({ top: 0, behavior: 'smooth' });

        tela.botaoSalvar.disabled = false;
        tela.botaoSalvar.textContent = modoEdicao
            ? 'Salvar alterações'
            : 'Cadastrar cliente';
    }
});

// [JS] cliente-form> Prepara a tela assim que a página abre
prepararTela();
