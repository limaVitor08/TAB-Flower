/* =====================================================================
   TabFlower - Tela de listagem de processos
   =====================================================================
   Esta tela demonstra, num lugar só, a regra de decisão da arquitetura:

     Sem termo e sem filtro  -> listagem simples, resolvida pela Model
                                (Active Record), via /api/processos.
     Com termo ou filtro     -> consulta combinada, resolvida pelo
                                Repository chamando a stored procedure
                                sp_buscar_processos.

   O rótulo no canto direito da barra de filtros mostra qual dos dois
   caminhos produziu o resultado que está na tela.

   Funcionalidades atendidas:
     03 - Busca por Processo
     06 - Painel Central de Gestão
     20 - Restrição de Exclusão (arquiva, não apaga)
   ===================================================================== */

const tela = {
    lista: document.getElementById('lista'),
    aviso: document.getElementById('aviso'),
    formBusca: document.getElementById('form-busca'),
    campoBusca: document.getElementById('campo-busca'),
    botaoLimpar: document.getElementById('botao-limpar'),
    mostrarInativos: document.getElementById('mostrar-inativos'),
    filtroStatus: document.getElementById('filtro-status'),
    filtroAdvogado: document.getElementById('filtro-advogado'),
    filtroTipo: document.getElementById('filtro-tipo'),
    rotuloFonte: document.getElementById('rotulo-fonte')
};

/* ---------------------------------------------------------------------
   Desenho da lista
   --------------------------------------------------------------------- */

function montarFicha(processo) {
    const classeInativa = processo.ativo ? '' : ' inativa';
    const cor = processo.status_cor || '#6b7280';

    const acoes = processo.ativo
        ? `<button type="button" class="botao botao-pequeno botao-perigo"
                   data-arquivar="${processo.id}"
                   data-numero="${escaparHtml(processo.numero_processo)}">
               Arquivar
           </button>`
        : `<span class="etiqueta etiqueta-cinza">Arquivado</span>`;

    const prazo = processo.prazo_final
        ? `<span>Prazo: ${formatarData(processo.prazo_final)}</span>`
        : '';

    return `
        <article class="ficha${classeInativa}">
            <div class="ficha-dados">
                <div class="ficha-nome">${escaparHtml(processo.titulo)}</div>
                <div class="ficha-info">
                    <span class="etiqueta-status" style="background-color:${cor}">
                        ${escaparHtml(processo.status_nome)}
                    </span>
                    <span class="mono">${escaparHtml(processo.numero_processo)}</span>
                    <span>${escaparHtml(processo.cliente_nome)}</span>
                    <span>${escaparHtml(processo.advogado_nome)}</span>
                    ${prazo}
                </div>
            </div>
            <div class="ficha-acoes">
                ${acoes}
                <a href="processo-detalhe.html?id=${processo.id}"
                   class="botao botao-pequeno">Abrir</a>
            </div>
        </article>
    `;
}

function desenharLista(processos, houveFiltro) {
    if (processos.length === 0) {
        const mensagem = houveFiltro
            ? `<strong>Nenhum processo encontrado</strong>
               Tente outro termo ou limpe os filtros.`
            : `<strong>Nenhum processo cadastrado ainda</strong>
               Cadastre o primeiro e o checklist de documentos é montado sozinho.`;

        tela.lista.innerHTML = `<div class="vazio">${mensagem}</div>`;
        return;
    }

    tela.lista.innerHTML = processos.map(montarFicha).join('');
}

/* ---------------------------------------------------------------------
   Filtros
   --------------------------------------------------------------------- */

/** Preenche os três selects com os dados vindos de /api/processos/opcoes. */
async function carregarFiltros() {
    try {
        const opcoes = await api.processos.opcoes();

        const montar = (select, itens, rotuloVazio) => {
            select.innerHTML =
                `<option value="">${rotuloVazio}</option>` +
                itens
                    .map((i) => `<option value="${i.id}">${escaparHtml(i.nome)}</option>`)
                    .join('');
        };

        montar(tela.filtroStatus, opcoes.status, 'Todas');
        montar(tela.filtroAdvogado, opcoes.advogados, 'Todos');
        montar(tela.filtroTipo, opcoes.tipos, 'Todos');
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

/** Reúne o que o usuário escolheu. */
function filtrosAtuais() {
    return {
        termo: tela.campoBusca.value.trim(),
        statusId: tela.filtroStatus.value,
        advogadoId: tela.filtroAdvogado.value,
        tipoId: tela.filtroTipo.value
    };
}

/** Algum critério foi informado? */
function temFiltro(f) {
    return Boolean(f.termo || f.statusId || f.advogadoId || f.tipoId);
}

/* ---------------------------------------------------------------------
   Carga
   --------------------------------------------------------------------- */

async function carregar() {
    limparAviso(tela.aviso);
    tela.lista.innerHTML = '<div class="vazio">Carregando...</div>';

    const filtros = filtrosAtuais();
    const usarProcedure = temFiltro(filtros);

    try {
        let processos;

        if (usarProcedure) {
            // Caminho do Repository: consulta combinada no banco.
            processos = await api.processos.buscar(filtros);
            tela.rotuloFonte.textContent = 'Fonte: sp_buscar_processos';
        } else {
            // Caminho da Model: listagem simples, CRUD puro.
            processos = await api.processos.listar(tela.mostrarInativos.checked);
            tela.rotuloFonte.textContent = 'Fonte: Model (CRUD)';
        }

        desenharLista(processos, usarProcedure);
    } catch (erro) {
        tela.lista.innerHTML = '';
        tela.rotuloFonte.textContent = '';
        mostrarAviso(tela.aviso, erro.message);
    }
}

/* ---------------------------------------------------------------------
   Arquivamento (Funcionalidade 20)
   --------------------------------------------------------------------- */

async function arquivar(id, numero) {
    const confirmou = confirm(
        `Arquivar o processo ${numero}?\n\n` +
        `Ele sai da lista, mas continua no banco com todo o histórico, ` +
        `o checklist e os documentos anexados.`
    );

    if (!confirmou) {
        return;
    }

    try {
        const resposta = await api.processos.excluir(id);
        mostrarAviso(tela.aviso, resposta.mensagem, 'sucesso');
        carregar();
    } catch (erro) {
        mostrarAviso(tela.aviso, erro.message);
    }
}

/* ---------------------------------------------------------------------
   Eventos
   --------------------------------------------------------------------- */

tela.formBusca.addEventListener('submit', (evento) => {
    evento.preventDefault();
    carregar();
});

tela.botaoLimpar.addEventListener('click', () => {
    tela.campoBusca.value = '';
    tela.filtroStatus.value = '';
    tela.filtroAdvogado.value = '';
    tela.filtroTipo.value = '';
    carregar();
});

// Trocar um filtro já dispara a busca: obrigar a clicar em Buscar depois
// de escolher uma situação seria um passo a mais sem motivo.
tela.filtroStatus.addEventListener('change', carregar);
tela.filtroAdvogado.addEventListener('change', carregar);
tela.filtroTipo.addEventListener('change', carregar);

tela.mostrarInativos.addEventListener('change', carregar);

tela.lista.addEventListener('click', (evento) => {
    const botao = evento.target.closest('[data-arquivar]');
    if (botao) {
        arquivar(botao.dataset.arquivar, botao.dataset.numero);
    }
});

/* Carga inicial: filtros primeiro, para os selects já existirem quando a
   lista for desenhada. */
carregarFiltros().then(carregar);
