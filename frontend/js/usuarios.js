/*
==============================================================================
SEÇÃO COMENTÁRIOS — usuarios.js: Lógica da página usuarios.html: Lista de usuários
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
usuarios> tela: Atalhos para os elementos da lista de usuários
usuarios>main>div> tela.lista: Desenha uma ficha por usuário com selo do perfil e botões Desativar e Editar
usuarios>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
usuarios>main>div>label>input> tela.mostrarInativos: Ao marcar ou desmarcar, recarrega a lista
usuarios>main>div>article> corDoPerfil(): Escolhe a cor do selo pelo perfil (Admin, Advogado ou Secretária)
usuarios>main>div>article> montarFicha(): Monta a ficha de um usuário: nome, selo do perfil, e-mail e botões (inativo fica apagado)
usuarios>main>div> desenharLista(): Desenha a lista de fichas ou a caixa de "nenhum usuário"
usuarios>main>div> carregar(): Busca os usuários na API e desenha a lista
usuarios>main>div>article>div>button> desativar(): Pergunta se pode desativar e, se sim, desativa o usuário e recarrega
usuarios>main>div>label>input> tela.mostrarInativos (change): Marcar ou desmarcar Mostrar inativos recarrega a lista
usuarios>main>div> tela.lista (click): Clique no botão Desativar de qualquer ficha da lista
usuarios> carregar(): Carrega a lista assim que a página abre
==============================================================================
*/

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    mostrarInativos: document.getElementById('mostrar-inativos')
};

function corDoPerfil(perfil) {
    if (perfil === 'Admin') { return '#1b2a41'; }
    if (perfil === 'Advogado') { return '#2f6f4e'; }
    return '#5a6472';
}

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
        await carregar();
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

tela.mostrarInativos.addEventListener('change', carregar);

tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-desativar]');
    if (botao) {
        desativar(botao.dataset.desativar, botao.dataset.nome);
    }
});

carregar();
