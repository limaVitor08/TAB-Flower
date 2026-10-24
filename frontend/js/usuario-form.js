// [JS] usuario-form> Atalhos para os campos do formulário de usuário
const campos = {
    // [JS] usuario-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    nome: document.getElementById('nome'),
    // [JS] usuario-form>main>form>div>div>input> Preenchido na edição e enviado ao salvar
    email: document.getElementById('email'),
    // [JS] usuario-form>main>form>div>div>select> Recebe os perfis da API; ao trocar, atualiza a dica de permissão
    perfil: document.getElementById('perfil_id'),
    // [JS] usuario-form>main>form>div>div>input> Vira obrigatório no cadastro e é enviado ao salvar
    senha: document.getElementById('senha')
};

// [JS] usuario-form> Atalhos para título, formulário, bloco de senha, avisos e botões
const tela = {
    // [JS] usuario-form>main>form> Ao enviar, cadastra ou atualiza e volta para a lista
    form: document.getElementById('form-usuario'),
    // [JS] usuario-form>main>div> Mostra aqui as mensagens de erro ou de sucesso
    aviso: document.getElementById('aviso'),
    // [JS] usuario-form>main>h1> Troca para "Editar usuário" quando a página abre com ?id=
    titulo: document.getElementById('titulo'),
    // [JS] usuario-form>main>p> Troca o texto no modo de edição
    subtitulo: document.getElementById('subtitulo'),
    // [JS] usuario-form>main>form>div>button> Troca para "Salvar alterações" na edição e mostra "Salvando..." enquanto espera
    botaoSalvar: document.getElementById('botao-salvar'),
    // [JS] usuario-form>main>form>div>div> É escondido no modo de edição
    blocoSenha: document.getElementById('bloco-senha'),
    // [JS] usuario-form>main>section> Mostra este bloco no modo de edição
    painelSenha: document.getElementById('painel-senha'),
    // [JS] usuario-form>main>section>div>input> Lê a nova senha e limpa depois de trocar
    senhaNova: document.getElementById('senha-nova'),
    // [JS] usuario-form>main>section>div>button> Envia a nova senha para a API e mostra o resultado
    botaoSenha: document.getElementById('botao-senha'),
    // [JS] usuario-form>main>form>div>div>span> Escreve se o perfil pode ou não excluir
    dicaPerfil: document.getElementById('dica-perfil')
};

// [JS] usuario-form> Lê o ?id= da URL: com id a tela edita, sem id cadastra
const idUsuario = new URLSearchParams(window.location.search).get('id');
const modoEdicao = Boolean(idUsuario);

// [JS] usuario-form> Guarda os perfis vindos da API
let perfis = [];

// [JS] usuario-form>main>form>div>div>span> Escreve se o perfil escolhido pode ou não excluir documentos
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

// [JS] usuario-form>main> Prepara a tela: preenche os perfis; na edição troca títulos, esconde a senha, mostra o bloco Trocar senha e preenche os dados
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

// [JS] usuario-form>main>form>div>div>select> Trocar o perfil atualiza a dica de permissão
campos.perfil.addEventListener('change', atualizarDicaPerfil);

// [JS] usuario-form>main>form> Ao salvar: cadastra (com senha) ou atualiza e volta para a lista; se der erro, mostra a mensagem no topo
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

// [JS] usuario-form>main>section>div>button> Trocar senha: envia a nova senha e mostra o resultado
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

// [JS] usuario-form> Prepara a tela assim que a página abre
prepararTela();
