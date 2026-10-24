// [JS] login> Página para onde a pessoa vai depois de entrar
const PAGINA_INICIAL = 'painel.html';

// [JS] login> Atalhos para os elementos da tela de login
const tela = {
    // [JS] login>main>form> Ao enviar, chama a API de login e vai para o painel
    form: document.getElementById('form-login'),
    // [JS] login>main>form>div>input> Lê o e-mail digitado ao enviar
    email: document.getElementById('email'),
    // [JS] login>main>form>div>input> Lê a senha e apaga o campo se der erro
    senha: document.getElementById('senha'),
    // [JS] login>main>form>div>button> Trava o botão e mostra "Entrando..." enquanto espera a API
    botao: document.getElementById('botao-entrar'),
    // [JS] login>main>div> Mostra aqui o erro (ex.: senha errada)
    aviso: document.getElementById('aviso')
};

// [JS] login> Quem já está logado pula direto para o painel
if (sessao.ativa()) {
    window.location.replace(PAGINA_INICIAL);
}

// [JS] login>main>form> Ao enviar: trava o botão, tenta entrar e vai para o painel; se der erro, mostra a mensagem e limpa a senha
tela.form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparAviso(tela.aviso);

    tela.botao.disabled = true;
    tela.botao.textContent = 'Entrando...';

    try {
        await api.auth.entrar(tela.email.value, tela.senha.value);
        window.location.replace(PAGINA_INICIAL);
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);

        tela.senha.value = '';
        tela.senha.focus();

        tela.botao.disabled = false;
        tela.botao.textContent = 'Entrar';
    }
});
