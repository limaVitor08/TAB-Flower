/* =====================================================================
   TabFlower - Listagem de usuários
   =====================================================================
   Funcionalidade 20 (Restricao de Exclusão): a lista mostra qual perfil
   tem permissão para excluir documentos em definitivo.
   ===================================================================== */

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    mostrarInativos: document.getElementById('mostrar-inativos')
};

/** Cor da etiqueta conforme o perfil. */
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
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
        carregar();
    } catch (erro) {
        // O Service recusa desativar advogado com processo ativo.
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
