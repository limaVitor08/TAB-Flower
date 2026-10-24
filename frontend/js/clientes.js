// [JS] clientes> Atalhos para os elementos da lista de clientes
const tela = {
    // [JS] clientes>main>div> Desenha uma ficha por cliente com os botões Desativar e Editar
    lista: document.getElementById('lista'),
    // [JS] clientes>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] clientes>main>div>form> Ao enviar, busca por nome ou por CPF/CNPJ (se digitar só números)
    formBusca: document.getElementById('form-busca'),
    // [JS] clientes>main>div>form>input> Lê o termo digitado
    campoBusca: document.getElementById('campo-busca'),
    // [JS] clientes>main>div>button> Limpa o campo de busca e recarrega todos os clientes
    botaoLimpar: document.getElementById('botao-limpar'),
    // [JS] clientes>main>div>label>input> Ao marcar ou desmarcar, recarrega a lista
    mostrarInativos: document.getElementById('mostrar-inativos')
};

// [JS] clientes>main>div>article> Monta a ficha de um cliente: nome, tipo, documento, cidade e botoes (inativo fica apagado)
function montarFicha(cliente) {
    const classeInativa = cliente.ativo ? '' : ' inativa';
    const rotuloTipo = cliente.tipo_pessoa === 'F' ? 'Pessoa física' : 'Pessoa jurídica';

    const botaoExcluir = cliente.ativo
        ? `<button type="button" class="botao botao-pequeno botao-perigo"
                   data-excluir="${cliente.id}" data-nome="${escaparHtml(cliente.nome)}">
               Desativar
           </button>`
        : `<span class="etiqueta etiqueta-cinza">Inativo</span>`;

    const cidade = cliente.cidade
        ? `<span>${escaparHtml(cliente.cidade)}${cliente.estado ? '/' + escaparHtml(cliente.estado) : ''}</span>`
        : '';

    return `
        <article class="ficha${classeInativa}">
            <div class="ficha-dados">
                <div class="ficha-nome">${escaparHtml(cliente.nome)}</div>
                <div class="ficha-info">
                    <span class="etiqueta">${rotuloTipo}</span>
                    <span class="mono">${escaparHtml(cliente.documento_formatado)}</span>
                    ${cidade}
                </div>
            </div>
            <div class="ficha-acoes">
                ${botaoExcluir}
                <a href="cliente-form.html?id=${cliente.id}"
                   class="botao botao-pequeno">Editar</a>
            </div>
        </article>
    `;
}

// [JS] clientes>main>div> Desenha a lista de fichas ou a caixa de "nenhum cliente"
function desenharLista(clientes, contexto = 'lista') {
    if (clientes.length === 0) {
        const mensagem = contexto === 'busca'
            ? `<strong>Nenhum cliente encontrado</strong>
               Confira a grafia ou cadastre um cliente novo.`
            : `<strong>Nenhum cliente cadastrado ainda</strong>
               Cadastre o primeiro e o sistema cria a pasta dele no servidor.`;

        tela.lista.innerHTML = `<div class="vazio">${mensagem}</div>`;
        return;
    }

    tela.lista.innerHTML = clientes.map(montarFicha).join('');
}

// [JS] clientes>main>div> Busca todos os clientes na API e desenha a lista
async function carregarClientes() {
    limparAviso(tela.aviso);
    tela.lista.innerHTML = '<div class="vazio">Carregando...</div>';

    try {
        const clientes = await api.clientes.listar(tela.mostrarInativos.checked);
        desenharLista(clientes);
    } catch (erro) {
        tela.lista.innerHTML = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] clientes>main>div>form> Busca por CPF/CNPJ se o texto parecer documento; senão busca por nome
async function buscar(termo) {
    limparAviso(tela.aviso);
    tela.lista.innerHTML = '<div class="vazio">Buscando...</div>';

    const apenasNumeros = somenteNumeros(termo);

    const pareceDocumento = apenasNumeros.length >= 11 && !/[a-zA-Z]/.test(termo);

    try {
        if (pareceDocumento) {
            const cliente = await api.clientes.buscarPorDocumento(apenasNumeros);
            desenharLista([cliente], 'busca');
        } else {
            const clientes = await api.clientes.buscarPorNome(termo);
            desenharLista(clientes, 'busca');
        }
    } catch (erro) {
        tela.lista.innerHTML = '';

        if (erro.message.toLowerCase().includes('encontrad')) {
            desenharLista([], 'busca');
        } else {
            mostrarAviso(tela.aviso, erro.message);
        }
    }
}

// [JS] clientes>main>div>article>div>button> Pergunta se pode desativar e, se sim, desativa o cliente e recarrega a lista
async function desativarCliente(id, nome) {
    const confirmou = confirm(
        `Desativar o cliente "${nome}"?\n\n` +
        `O cadastro sai da lista, mas continua no banco junto com os ` +
        `processos e documentos dele. Um administrador pode reativar depois.`
    );

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await api.clientes.excluir(id);
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
        carregarClientes();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] clientes>main>div>form> Ao enviar a busca: campo vazio mostra todos, senão busca o termo
tela.formBusca.addEventListener('submit', (evento) => {
    evento.preventDefault();
    const termo = tela.campoBusca.value.trim();

    if (!termo) {
        carregarClientes();
        return;
    }

    buscar(termo);
});

// [JS] clientes>main>div>button> Ver todos: limpa a busca e recarrega a lista
tela.botaoLimpar.addEventListener('click', () => {
    tela.campoBusca.value = '';
    carregarClientes();
});

// [JS] clientes>main>div>label>input> Marcar ou desmarcar Mostrar inativos recarrega a lista
tela.mostrarInativos.addEventListener('change', carregarClientes);

// [JS] clientes>main>div> Clique no botão Desativar de qualquer ficha da lista
tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-excluir]');
    if (botao) {
        desativarCliente(botao.dataset.excluir, botao.dataset.nome);
    }
});

// [JS] clientes> Carrega a lista assim que a página abre
carregarClientes();
