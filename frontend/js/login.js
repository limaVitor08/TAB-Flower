/* =====================================================================
   TabFlower - Tela de login
   =====================================================================
   Porta de entrada do sistema. Todas as outras telas exigem sessão
   ativa: quem chega nelas sem estar logado é mandado para cá pelo
   próprio api.js.

   Aqui a senha é digitada e enviada ao backend uma única vez. A senha
   nunca é guardada em lugar nenhum do navegador - o que fica guardado é
   o token que o backend devolve, e ele vence sozinho em 8 horas.
   ===================================================================== */

const PAGINA_INICIAL = 'painel.html';

const tela = {
    form: document.getElementById('form-login'),
    email: document.getElementById('email'),
    senha: document.getElementById('senha'),
    botao: document.getElementById('botao-entrar'),
    aviso: document.getElementById('aviso')
};

/* Quem já está logado não precisa ver esta tela de novo. */
if (sessao.ativa()) {
    window.location.replace(PAGINA_INICIAL);
}


tela.form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparAviso(tela.aviso);

    // Trava o botão para a pessoa não enviar duas vezes enquanto o
    // servidor responde.
    tela.botao.disabled = true;
    tela.botao.textContent = 'Entrando...';

    try {
        await api.auth.entrar(tela.email.value, tela.senha.value);
        window.location.replace(PAGINA_INICIAL);
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);

        // Limpa só a senha: o e-mail continua preenchido para a pessoa
        // não ter que digitar tudo de novo.
        tela.senha.value = '';
        tela.senha.focus();

        tela.botao.disabled = false;
        tela.botao.textContent = 'Entrar';
    }
});
