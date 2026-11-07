/*
==============================================================================
SEÇÃO COMENTÁRIOS — usuario-form.js: Lógica da página usuario-form.html: Cadastro e edição de usuário, com troca de senha
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
usuario-form> campos: Atalhos para os campos do formulário de usuário
usuario-form>main>form>div>div>input> campos.nome: Preenchido na edição e enviado ao salvar
usuario-form>main>form>div>div>input> campos.email: Preenchido na edição e enviado ao salvar
usuario-form>main>form>div>div>select> campos.perfil: Recebe os perfis da API; ao trocar, atualiza a dica de permissão
usuario-form>main>form>div>div>input> campos.senha: Vira obrigatório no cadastro e é enviado ao salvar
usuario-form> tela: Atalhos para título, formulário, bloco de senha, avisos e botões
usuario-form>main>form> tela.form: Ao enviar, cadastra ou atualiza e volta para a lista
usuario-form>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
usuario-form>main>h1> tela.titulo: Troca para "Editar usuário" quando a página abre com ?id=
usuario-form>main>p> tela.subtitulo: Troca o texto no modo de edição
usuario-form>main>form>div>button> tela.botaoSalvar: Troca para "Salvar alterações" na edição e mostra "Salvando..." enquanto espera
usuario-form>main>form>div>div> tela.blocoSenha: É escondido no modo de edição
usuario-form>main>section> tela.painelSenha: Mostra este bloco no modo de edição
usuario-form>main>section>div>input> tela.senhaNova: Lê a nova senha e limpa depois de trocar
usuario-form>main>section>div>button> tela.botaoSenha: Envia a nova senha para a API e mostra o resultado
usuario-form>main>form>div>div>span> tela.dicaPerfil: Escreve se o perfil pode ou não excluir
usuario-form> idUsuario: Lê o ?id= da URL: com id a tela edita, sem id cadastra
usuario-form> perfis: Guarda os perfis vindos da API
usuario-form>main>form>div>div>span> atualizarDicaPerfil(): Escreve se o perfil escolhido pode ou não excluir documentos
usuario-form>main> prepararTela(): Prepara a tela: preenche os perfis; na edição troca títulos, esconde a senha, mostra o bloco Trocar senha e preenche os dados
usuario-form>main>form>div>div>select> campos.perfil (change): Trocar o perfil atualiza a dica de permissão
usuario-form>main>form> tela.form (submit): Ao salvar: cadastra (com senha) ou atualiza e volta para a lista; se der erro, mostra a mensagem no topo
usuario-form>main>section>div>button> tela.botaoSenha (click): Trocar senha: envia a nova senha e mostra o resultado
usuario-form> prepararTela(): Prepara a tela assim que a página abre
==============================================================================
*/

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

function atualizarDicaPerfil() {
    const perfil = perfis.find((p) => String(p.id) === campos.perfil.value);

    if (!perfil) {
        tela.dicaPerfil.textContent = '';
        return;
    }

    tela.dicaPerfil.textContent = perfil.pode_excluir
        ? 'Pode excluir e restaurar documentos e desativar cadastros.'
        : 'Não pode excluir documentos nem desativar cadastros.';
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
