/* =====================================================================
   TabFlower - Cadastro e edicao de usuário
   =====================================================================
   No cadastro, a senha e obrigatória. Na edicao, ela some do formulario
   principal e vira um painel separado: trocar senha e um caso de uso
   diferente de corrigir um nome.
   ===================================================================== */

const campos = {
    nome: document.getElementById('nome'),
    email: document.getElementById('email'),
    perfil: document.getElementById('perfil_id'),
    senha: document.getElementById('senha')
};

const tela = {
    form: document.getElementById('form-usuario'),
    aviso: document.getElementById('aviso'),
    titulo: document.getElementById('titulo'),
    subtitulo: document.getElementById('subtitulo'),
    botaoSalvar: document.getElementById('botao-salvar'),
    blocoSenha: document.getElementById('bloco-senha'),
    painelSenha: document.getElementById('painel-senha'),
    senhaNova: document.getElementById('senha-nova'),
    botaoSenha: document.getElementById('botao-senha'),
    dicaPerfil: document.getElementById('dica-perfil')
};

const idUsuario = new URLSearchParams(window.location.search).get('id');
const modoEdicao = Boolean(idUsuario);

let perfis = [];

/** Explica o que o perfil escolhido pode fazer. */
function atualizarDicaPerfil() {
    const perfil = perfis.find((p) => String(p.id) === campos.perfil.value);

    if (!perfil) {
        tela.dicaPerfil.textContent = '';
        return;
    }

    tela.dicaPerfil.textContent = perfil.pode_excluir
        ? 'Pode excluir documentos em definitivo.'
        : 'Não pode excluir documentos em definitivo.';
}

async function prepararTela() {
    try {
        perfis = await api.usuarios.perfis();

        campos.perfil.innerHTML = perfis
            .map((p) => `<option value="${p.id}">${escaparHtml(p.nome)}</option>`)
            .join('');

        atualizarDicaPerfil();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        tela.botaoSalvar.disabled = true;
        return;
    }

    if (!modoEdicao) {
        campos.senha.required = true;
        return;
    }

    tela.titulo.textContent = 'Editar usuário';
    tela.subtitulo.textContent = 'A senha é trocada no painel abaixo do formulário.';
    tela.botaoSalvar.textContent = 'Salvar alterações';

    // Na edicao a senha sai do formulario principal.
    tela.blocoSenha.classList.add('escondido');
    campos.senha.required = false;
    tela.painelSenha.classList.remove('escondido');

    try {
        const usuario = await api.usuarios.buscarPorId(idUsuario);
        campos.nome.value = usuario.nome;
        campos.email.value = usuario.email;
        campos.perfil.value = usuario.perfil_id;
        atualizarDicaPerfil();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        tela.botaoSalvar.disabled = true;
    }
}

campos.perfil.addEventListener('change', atualizarDicaPerfil);

tela.form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparAviso(tela.aviso);

    tela.botaoSalvar.disabled = true;
    tela.botaoSalvar.textContent = 'Salvando...';

    const dados = {
        nome: campos.nome.value.trim(),
        email: campos.email.value.trim(),
        perfil_id: Number(campos.perfil.value)
    };

    if (!modoEdicao) {
        dados.senha = campos.senha.value;
    }

    try {
        if (modoEdicao) {
            await api.usuarios.atualizar(idUsuario, dados);
        } else {
            await api.usuarios.criar(dados);
        }
        window.location.href = 'usuarios.html';
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
        window.scrollTo({ top: 0, behavior: 'smooth' });
        tela.botaoSalvar.disabled = false;
        tela.botaoSalvar.textContent = modoEdicao
            ? 'Salvar alterações'
            : 'Cadastrar usuário';
    }
});

tela.botaoSenha.addEventListener('click', async () => {
    limparAviso(tela.aviso);
    tela.botaoSenha.disabled = true;

    try {
        const resposta = await api.usuarios.alterarSenha(
            idUsuario,
            tela.senhaNova.value
        );
        tela.senhaNova.value = '';
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    } finally {
        tela.botaoSenha.disabled = false;
    }
});

prepararTela();
