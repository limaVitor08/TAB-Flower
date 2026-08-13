/* =====================================================================
   TabFlower - Tela de listagem de clientes
   =====================================================================
   Funcionalidades atendidas:
     01 - Busca por Nome
     02 - Busca por Documento
     20 - Restricao de Exclusão (o botao desativa, não apaga)
   ===================================================================== */

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    formBusca: document.getElementById('form-busca'),
    campoBusca: document.getElementById('campo-busca'),
    botaoLimpar: document.getElementById('botao-limpar'),
    mostrarInativos: document.getElementById('mostrar-inativos')
};

/* ---------------------------------------------------------------------
   Desenho da lista
   --------------------------------------------------------------------- */

/** Monta o HTML de uma ficha de cliente. */
function montarFicha(cliente) {
    const classeInativa = cliente.ativo ? '' : ' inativa';
    const rotuloTipo = cliente.tipo_pessoa === 'F' ? 'Pessoa física' : 'Pessoa jurídica';

    // Cliente inativo não pode ser desativado de novo.
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

/** Desenha a lista inteira, ou o estado vazio. */
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

/* ---------------------------------------------------------------------
   Carregamento
   --------------------------------------------------------------------- */

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

/**
 * Decide sozinho se a busca e por nome ou por documento.
 *
 * Se o usuário digitou só números (com ou sem pontuação), trata como
 * CPF/CNPJ. Caso contrario, busca por nome. Isso evita ter dois campos
 * de busca separados na tela.
 */
async function buscar(termo) {
    limparAviso(tela.aviso);
    tela.lista.innerHTML = '<div class="vazio">Buscando...</div>';

    const apenasNumeros = somenteNumeros(termo);

    // Se tem 11 digitos ou mais e nenhuma letra, só pode ser CPF ou CNPJ.
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

        // "Cliente não encontrado" não e falha do sistema: e resultado
        // vazio. Mostramos o estado vazio, não um erro vermelho.
        if (erro.message.toLowerCase().includes('encontrad')) {
            desenharLista([], 'busca');
        } else {
            mostrarAviso(tela.aviso, erro.message);
        }
    }
}

/* ---------------------------------------------------------------------
   Exclusão (Funcionalidade 20)
   --------------------------------------------------------------------- */

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

/* ---------------------------------------------------------------------
   Eventos
   --------------------------------------------------------------------- */

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

// Um único listener na lista inteira cuida de todos os botoes Desativar,
// inclusive dos que ainda nem foram desenhados na tela.
tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-excluir]');
    if (botao) {
        desativarCliente(botao.dataset.excluir, botao.dataset.nome);
    }
});

// Primeira carga ao abrir a página.
carregarClientes();
