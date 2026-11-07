/*
==============================================================================
SEÇÃO COMENTÁRIOS — importacoes.js: Lógica da página importacoes.html: Importação de clientes por planilha
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
importacoes> tela: Atalhos para os elementos da importação
importacoes>main>div> tela.aviso: Mostra aqui as mensagens de erro ou de sucesso
importacoes>main>section>form> tela.form: Ao enviar, importa a planilha e mostra o resultado
importacoes>main>section>form>input> tela.arquivo: Pega o arquivo escolhido para enviar
importacoes>main>section>form>button> tela.botaoEnviar: Mostra "Importando..." enquanto a planilha é processada
importacoes>main>section>form>a> tela.linkModelo: Baixa o modelo levando o token de login
importacoes>main>section>div> tela.resultado: Aparece com os cartões de total, sucesso, erro e a lista de linhas que falharam
importacoes>main>section>div> tela.lista: Desenha cada carga com os botões Ver clientes e Desfazer
importacoes>main>section>form>a> tela.linkModelo.href: Baixar modelo: baixa o CSV de exemplo pelo JS (um link comum não levaria o token)
importacoes>main>section>div> mostrarResultado(): Mostra o resultado da carga: três cartões (linhas, cadastrados, com problema) e a lista de linhas que falharam
importacoes> NOMES_SITUACAO: Troca a situação gravada no banco (CONCLUIDA) pelo nome com acento mostrado na tela (Concluída)
importacoes>main>section>div>article> montarFicha(): Monta a ficha de uma importação: arquivo, situação, quantos entraram, erros, data e botões
importacoes>main>section>div> carregarHistorico(): Busca o histórico de importações e desenha a lista
importacoes>main>section>form> tela.form (submit): Envia a planilha, mostra o resultado e um aviso com o total; depois recarrega o histórico
importacoes>main>section>div> tela.lista (click): Cliques nas fichas: Ver clientes mostra/esconde os nomes da carga; Desfazer pede confirmação e desativa a carga
importacoes> carregarHistorico(): Carrega o histórico assim que a página abre
==============================================================================
*/

const tela = {
    aviso: document.getElementById('aviso'),
    form: document.getElementById('form-importacao'),
    arquivo: document.getElementById('arquivo'),
    botaoEnviar: document.getElementById('botao-enviar'),
    linkModelo: document.getElementById('link-modelo'),
    resultado: document.getElementById('resultado'),
    lista: document.getElementById('lista')
};

tela.linkModelo.href = '#';
tela.linkModelo.addEventListener('click', async (evento) => {
    evento.preventDefault();
    try {
        await api.importacoes.baixarModelo();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
});

function mostrarResultado(lote) {
    const houveErro = lote.total_erro > 0;

    const erros = houveErro
        ? `<div class="texto-pendente" style="margin-top:12px">
               <strong>Linhas que não entraram:</strong>
               <ul style="margin:6px 0 0 18px">
                   ${lote.log_erros.split('\n')
                       .map((e) => `<li>${escaparHtml(e)}</li>`)
                       .join('')}
               </ul>
           </div>`
        : '';

    tela.resultado.className = 'painel';
    tela.resultado.style.marginTop = '16px';
    tela.resultado.innerHTML = `
        <h2 class="titulo-secao">Resultado da importação</h2>
        <div class="cartoes" style="margin-top:12px">
            <div class="cartao" style="border-top-color:var(--tinta)">
                <div class="cartao-numero">${lote.total_registros}</div>
                <div class="cartao-rotulo">Linhas na planilha</div>
            </div>
            <div class="cartao" style="border-top-color:var(--folha)">
                <div class="cartao-numero">${lote.total_sucesso}</div>
                <div class="cartao-rotulo">Clientes cadastrados</div>
            </div>
            <div class="cartao" style="border-top-color:var(--alerta)">
                <div class="cartao-numero">${lote.total_erro}</div>
                <div class="cartao-rotulo">Linhas com problema</div>
            </div>
        </div>
        ${erros}`;
}

const NOMES_SITUACAO = {
    PROCESSANDO: 'Processando',
    CONCLUIDA: 'Concluída',
    FALHOU: 'Falhou'
};

function montarFicha(lote) {
    const cor = lote.situacao === 'CONCLUIDA' ? '#2f6f4e' : '#c2410c';

    const quando = lote.criado_em
        ? new Date(lote.criado_em).toLocaleString('pt-BR')
        : '';

    const acoes = lote.total_sucesso > 0
        ? `<button type="button" class="botao botao-pequeno"
                   data-ver="${lote.id}">Ver clientes</button>
           <button type="button" class="botao botao-pequeno botao-perigo"
                   data-desfazer="${lote.id}"
                   data-arquivo="${escaparHtml(lote.nome_arquivo)}">Desfazer</button>`
        : '';

    return `
        <article class="ficha">
            <div class="ficha-dados">
                <div class="ficha-nome mono"
                     style="font-size:0.95rem">${escaparHtml(lote.nome_arquivo)}</div>
                <div class="ficha-info">
                    <span class="etiqueta-status" style="background-color:${cor}">
                        ${escaparHtml(NOMES_SITUACAO[lote.situacao] || lote.situacao)}
                    </span>
                    <span>${lote.total_sucesso} de ${lote.total_registros} importados</span>
                    ${lote.total_erro > 0
                        ? `<span class="texto-pendente">${lote.total_erro} com erro</span>`
                        : ''}
                    <span class="texto-prazo">${quando}</span>
                </div>
                <div class="dica" id="clientes-${lote.id}"></div>
            </div>
            <div class="ficha-acoes">${acoes}</div>
        </article>`;
}

async function carregarHistorico() {
    tela.lista.innerHTML = '<div class="vazio">Carregando...</div>';

    try {
        const lotes = await api.importacoes.listar();

        if (lotes.length === 0) {
            tela.lista.innerHTML = `
                <div class="vazio">
                    <strong>Nenhuma importação realizada</strong>
                    Envie a planilha de clientes antigos para começar.
                </div>`;
            return;
        }

        tela.lista.innerHTML = lotes.map(montarFicha).join('');
    } catch (erro) {
        tela.lista.innerHTML = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

tela.form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    limparAviso(tela.aviso);

    tela.botaoEnviar.disabled = true;
    tela.botaoEnviar.textContent = 'Importando...';
    tela.resultado.className = 'escondido';

    const dados = new FormData();
    dados.append('arquivo', tela.arquivo.files[0]);

    try {
        const lote = await api.importacoes.enviar(dados);

        mostrarResultado(lote);

        const tipo = lote.total_erro === 0 ? 'sucesso' : 'erro';
        mostrarAviso(
            tela.aviso,
            `${lote.total_sucesso} de ${lote.total_registros} clientes importados.` +
            (lote.total_erro > 0
                ? ` ${lote.total_erro} linha(s) não entraram — veja a lista abaixo.`
                : ' Todas as linhas entraram.'),
            tipo
        );

        tela.form.reset();
        await carregarHistorico();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    } finally {
        tela.botaoEnviar.disabled = false;
        tela.botaoEnviar.textContent = 'Importar';
    }
});

tela.lista.addEventListener('click', async (evento) => {
    const ver = evento.target.closest('[data-ver]');
    const desfazer = evento.target.closest('[data-desfazer]');

    if (ver) {
        const alvo = document.getElementById('clientes-' + ver.dataset.ver);
        if (alvo.innerHTML) {
            alvo.innerHTML = '';
            return;
        }
        try {
            const clientes = await api.importacoes.clientes(ver.dataset.ver);
            alvo.innerHTML =
                '<strong>Clientes desta carga:</strong> ' +
                clientes.map((c) =>
                    `${escaparHtml(c.nome)}${c.ativo ? '' : ' (inativo)'}`
                ).join(' &middot; ');
        } catch (erro) {
            mostrarAviso(tela.aviso, erro.message);
        }
        return;
    }

    if (desfazer) {
        const confirmou = confirm(
            `Desfazer a importação de "${desfazer.dataset.arquivo}"?\n\n` +
            `Os clientes desta carga ficam inativos. Quem já tem processo ` +
            `aberto é preservado, porque deixou de ser legado bruto e ` +
            `virou trabalho do escritório.`
        );
        if (!confirmou) {
            return;
        }

        try {
            const r = await api.importacoes.desfazer(desfazer.dataset.desfazer);

            let mensagem = `${r.desativados} cliente(s) desativado(s).`;
            if (r.preservados.length > 0) {
                mensagem +=
                    ` ${r.preservados.length} preservado(s) por já ter processo: ` +
                    r.preservados.join(', ') + '.';
            }

            mostrarAviso(tela.aviso, mensagem, 'sucesso');
            await carregarHistorico();
        } catch (erro) {
            mostrarAviso(tela.aviso, erro.message);
        }
    }
});

carregarHistorico();
