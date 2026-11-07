/*
==============================================================================
SEÇÃO COMENTÁRIOS — clientes.js: Lógica da página clientes.html: Lista e busca de clientes
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
clientes> tela: Atalhos para os elementos da lista de clientes
clientes>main>div> tela.lista: Desenha uma ficha por cliente com os botões Desativar e Editar
clientes>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
clientes>main>div>form> tela.formBusca: Ao enviar, busca por nome ou por CPF/CNPJ (se digitar só números)
clientes>main>div>form>input> tela.campoBusca: Lê o termo digitado
clientes>main>div>button> tela.botaoLimpar: Limpa o campo de busca e recarrega todos os clientes
clientes>main>div>label>input> tela.mostrarInativos: Ao marcar ou desmarcar, recarrega a lista
clientes>main>div>article> montarFicha(): Monta a ficha de um cliente: nome, tipo, documento, cidade e botões (inativo fica apagado)
clientes>main>div> desenharLista(): Desenha a lista de fichas ou a caixa de "nenhum cliente"
clientes>main>div> carregarClientes(): Busca todos os clientes na API e desenha a lista
clientes>main>div>form> buscar(): Busca por CPF/CNPJ se o texto parecer documento; senão busca por nome, trazendo os inativos se Mostrar inativos estiver marcado
clientes>main>div>article>div>button> desativarCliente(): Pergunta se pode desativar e, se sim, desativa o cliente e recarrega a lista
clientes>main>div>form> tela.formBusca (submit): Ao enviar a busca: campo vazio mostra todos, senão busca o termo
clientes>main>div>button> tela.botaoLimpar (click): Ver todos: limpa a busca e recarrega a lista
clientes>main>div>label>input> tela.mostrarInativos (change): Marcar ou desmarcar Mostrar inativos recarrega a lista
clientes>main>div> tela.lista (click): Clique no botão Desativar de qualquer ficha da lista
clientes> carregarClientes(): Carrega a lista assim que a página abre
==============================================================================
*/

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    formBusca: document.getElementById('form-busca'),
    campoBusca: document.getElementById('campo-busca'),
    botaoLimpar: document.getElementById('botao-limpar'),
    mostrarInativos: document.getElementById('mostrar-inativos')
};

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
            const clientes = await api.clientes.buscarPorNome(
                termo, tela.mostrarInativos.checked
            );
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

async function desativarCliente(id, nome) {
    const confirmou = confirm(
        `Desativar o cliente "${nome}"?\n\n` +
        `O cadastro sai da lista, mas continua no banco junto com os ` +
        `processos e documentos dele, e aparece marcando Mostrar inativos.`
    );

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await api.clientes.excluir(id);
        await carregarClientes();
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

tela.formBusca.addEventListener('submit', (evento) => {
    evento.preventDefault();
    const termo = tela.campoBusca.value.trim();

    if (!termo) {
        carregarClientes();
        return;
    }

    buscar(termo);
});

tela.botaoLimpar.addEventListener('click', () => {
    tela.campoBusca.value = '';
    carregarClientes();
});

tela.mostrarInativos.addEventListener('change', carregarClientes);

tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-excluir]');
    if (botao) {
        desativarCliente(botao.dataset.excluir, botao.dataset.nome);
    }
});

carregarClientes();
