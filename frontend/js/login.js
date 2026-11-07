/*
==============================================================================
SEÇÃO COMENTÁRIOS — login.js: Lógica da página login.html: Tela de login (e-mail e senha)
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
login> PAGINA_INICIAL: Página para onde a pessoa vai depois de entrar
login> tela: Atalhos para os elementos da tela de login
login>main>form> tela.form: Ao enviar, chama a API de login e vai para o painel
login>main>form>div>input> tela.email: Lê o e-mail digitado ao enviar
login>main>form>div>input> tela.senha: Lê a senha e apaga o campo se der erro
login>main>form>div>button> tela.botao: Trava o botão e mostra "Entrando..." enquanto espera a API
login>main>div> tela.aviso: Mostra aqui o erro (ex.: senha errada)
login> ao abrir a página: Quem já está logado pula direto para o painel
login>main>div> avisoGuardado: Se a pessoa caiu aqui porque a sessão venceu, mostra o aviso que o api.js guardou
login>main>form> tela.form (submit): Ao enviar: trava o botão, tenta entrar e vai para o painel; se der erro, mostra a mensagem e limpa a senha
==============================================================================
*/

const PAGINA_INICIAL = 'painel.html';

const tela = {
    form: document.getElementById('form-login'),
    email: document.getElementById('email'),
    senha: document.getElementById('senha'),
    botao: document.getElementById('botao-entrar'),
    aviso: document.getElementById('aviso')
};

if (sessao.ativa()) {
    window.location.replace(PAGINA_INICIAL);
}

const avisoGuardado = sessionStorage.getItem(CHAVE_AVISO);
if (avisoGuardado) {
    sessionStorage.removeItem(CHAVE_AVISO);
    mostrarAviso(tela.aviso, avisoGuardado);
}

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
