// [JS] usuarios> Atalhos para os elementos da lista de usuários
const tela = {
    // [JS] usuarios>main>div> Desenha uma ficha por usuário com selo do perfil e botões Desativar e Editar
    lista: document.getElementById('lista'),
    // [JS] usuarios>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] usuarios>main>div>label>input> Ao marcar ou desmarcar, recarrega a lista
    mostrarInativos: document.getElementById('mostrar-inativos')
};

// [JS] usuarios>main>div>article> Escolhe a cor do selo pelo perfil (Admin, Advogado ou Secretária)
function corDoPerfil(perfil) {
    if (perfil === 'Admin') { return '#1b2a41'; }
    if (perfil === 'Advogado') { return '#2f6f4e'; }
    return '#5a6472';
}

// [JS] usuarios>main>div>article> Monta a ficha de um usuário: nome, selo do perfil, e-mail e botões (inativo fica apagado)
function montarFicha(usuario) {
    const classeInativa = usuario.ativo ? '' : ' inativa';

    const acoes = usuario.ativo
        ? `<button type="button" class="botao botao-pequeno botao-perigo"
                   data-desativar="${usuario.id}"
                   data-nome="${escaparHtml(usuario.nome)}">
               Desativar
           </button>`
        : `<span class="etiqueta etiqueta-cinza">Inativo</span>`;

    return `
        <article class="ficha${classeInativa}">
            <div class="ficha-dados">
                <div class="ficha-nome">${escaparHtml(usuario.nome)}</div>
                <div class="ficha-info">
                    <span class="etiqueta-status"
                          style="background-color:${corDoPerfil(usuario.perfil_nome)}">
                        ${escaparHtml(usuario.perfil_nome)}
                    </span>
                    <span>${escaparHtml(usuario.email)}</span>
                </div>
            </div>
            <div class="ficha-acoes">
                ${acoes}
                <a href="usuario-form.html?id=${usuario.id}"
                   class="botao botao-pequeno">Editar</a>
            </div>
        </article>
    `;
}

// [JS] usuarios>main>div> Desenha a lista de fichas ou a caixa de "nenhum usuário"
function desenharLista(usuarios) {
    if (usuarios.length === 0) {
        tela.lista.innerHTML = `
            <div class="vazio">
                <strong>Nenhum usuário cadastrado</strong>
                Cadastre a equipe do escritório para poder atribuir processos.
            </div>`;
        return;
    }

    tela.lista.innerHTML = usuarios.map(montarFicha).join('');
}

// [JS] usuarios>main>div> Busca os usuários na API e desenha a lista
async function carregar() {
    limparAviso(tela.aviso);
    tela.lista.innerHTML = '<div class="vazio">Carregando...</div>';

    try {
        const usuarios = await api.usuarios.listar(tela.mostrarInativos.checked);
        desenharLista(usuarios);
    } catch (erro) {
        tela.lista.innerHTML = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] usuarios>main>div>article>div>button> Pergunta se pode desativar e, se sim, desativa o usuário e recarrega
async function desativar(id, nome) {
    const confirmou = confirm(
        `Desativar o usuário "${nome}"?\n\n` +
        `Ele perde o acesso, mas continua no banco: os processos e o log ` +
        `de auditoria precisam saber quem fez cada ação.`
    );

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await api.usuarios.excluir(id);
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
        carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

// [JS] usuarios>main>div>label>input> Marcar ou desmarcar Mostrar inativos recarrega a lista
tela.mostrarInativos.addEventListener('change', carregar);

// [JS] usuarios>main>div> Clique no botão Desativar de qualquer ficha da lista
tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-desativar]');
    if (botao) {
        desativar(botao.dataset.desativar, botao.dataset.nome);
    }
});

// [JS] usuarios> Carrega a lista assim que a página abre
carregar();
