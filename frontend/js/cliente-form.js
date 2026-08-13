/* =====================================================================
   TabFlower - Tela de cadastro e edicao de cliente
   =====================================================================
   A mesma tela serve para os dois casos. Se a URL trouxer ?id=1, ela
   carrega o cliente e entra em modo de edicao.

   Funcionalidades atendidas:
     04 - Validação de Documento (a mensagem vem da API)
     05 - Bloqueio de Duplicidade (idem)
     08 - Geração de Diretórios (acontece no backend ao cadastrar)
   ===================================================================== */

const campos = {
    tipoPessoa: document.getElementById('tipo_pessoa'),
    documento: document.getElementById('documento'),
    nome: document.getElementById('nome'),
    email: document.getElementById('email'),
    telefone: document.getElementById('telefone'),
    endereco: document.getElementById('endereco'),
    cidade: document.getElementById('cidade'),
    estado: document.getElementById('estado'),
    observacao: document.getElementById('observacao')
};

const tela = {
    form: document.getElementById('form-cliente'),
    aviso: document.getElementById('aviso'),
    titulo: document.getElementById('titulo'),
    subtitulo: document.getElementById('subtitulo'),
    botaoSalvar: document.getElementById('botao-salvar'),
    dicaDocumento: document.getElementById('dica-documento')
};

// Le o ?id=1 da URL. Se não houver, estamos cadastrando.
const idCliente = new URLSearchParams(window.location.search).get('id');
const modoEdicao = Boolean(idCliente);

/* ---------------------------------------------------------------------
   Preparacao da tela
   --------------------------------------------------------------------- */

async function prepararTela() {
    if (!modoEdicao) {
        return;
    }

    tela.titulo.textContent = 'Editar cliente';
    tela.subtitulo.textContent =
        'O CPF/CNPJ fica bloqueado: alterar o documento burlaria o controle de duplicidade.';
    tela.botaoSalvar.textContent = 'Salvar alterações';

    // Documento e tipo de pessoa não mudam depois do cadastro.
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

/* ---------------------------------------------------------------------
   Mascaras dos campos
   Formatação e coisa de tela. O backend recebe e guarda os valores
   limpos, sem pontuação.
   --------------------------------------------------------------------- */

aplicarMascara(campos.documento, formatarDocumento);
aplicarMascara(campos.telefone, formatarTelefone);
aplicarMascara(campos.estado, formatarUF);

// Ao trocar o tipo de pessoa, o exemplo do campo acompanha.
campos.tipoPessoa.addEventListener('change', () => {
    campos.documento.placeholder = campos.tipoPessoa.value === 'F'
        ? '000.000.000-00'
        : '00.000.000/0000-00';
});

/* ---------------------------------------------------------------------
   Envio
   --------------------------------------------------------------------- */

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

    // Tipo e documento só vao na criação: na edicao eles estao travados.
    if (!modoEdicao) {
        dados.tipo_pessoa = campos.tipoPessoa.value;
        dados.documento = somenteNumeros(campos.documento.value);
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
            await api.clientes.atualizar(idCliente, dados);
        } else {
            await api.clientes.criar(dados);
        }

        // Deu certo: volta para a lista.
        window.location.href = 'clientes.html';

    } catch (erro) {
        // A mensagem vem pronta da API: "CPF inválido", "Já existe um
        // cliente cadastrado com este documento", etc.
        mostrarAviso(tela.aviso, erro.message);
        window.scrollTo({ top: 0, behavior: 'smooth' });

        tela.botaoSalvar.disabled = false;
        tela.botaoSalvar.textContent = modoEdicao
            ? 'Salvar alterações'
            : 'Cadastrar cliente';
    }
});

prepararTela();
