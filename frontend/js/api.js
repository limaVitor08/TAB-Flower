/* =====================================================================
   TabFlower - Acesso a API
   =====================================================================
   Todas as chamadas ao backend passam por este arquivo. As telas nunca
   escrevem fetch direto: elas chamam api.clientes.listar(), e assim por
   diante.

   Se um dia a porta ou o endereço do servidor mudar, muda só aqui.
   ===================================================================== */

const URL_BASE = 'http://localhost:5000/api';

const PAGINA_LOGIN = 'login.html';

const ERRO_CONEXAO =
    'Não foi possível falar com o servidor. ' +
    'Confira se o WAMP está ligado e se o run.py está rodando.';


/* =====================================================================
   Sessão do usuário
   =====================================================================
   Depois do login, o backend devolve um "crachá" assinado (o token) e
   os dados do usuário. Guardamos os dois no localStorage do navegador,
   que sobrevive ao fechar e reabrir a aba.

   O token é enviado em toda requisição no cabeçalho Authorization. É
   ele que prova ao backend quem está falando: o servidor confere a
   assinatura e descobre sozinho qual é o usuário. Por isso nenhuma
   tela precisa mais mandar "usuario_id" - e nem adiantaria mandar,
   porque o backend ignora esse campo agora.

   Os dados do usuário guardados aqui servem só para a interface (nome
   no cabeçalho, esconder o que a pessoa não pode fazer). Toda decisão
   de permissão que importa é tomada de novo no backend.
   ===================================================================== */

const CHAVE_TOKEN = 'tabflower_token';
const CHAVE_USUARIO = 'tabflower_usuario';

const sessao = {

    /** Guarda token e usuário logo após o login dar certo. */
    salvar(token, usuario) {
        localStorage.setItem(CHAVE_TOKEN, token);
        localStorage.setItem(CHAVE_USUARIO, JSON.stringify(usuario));
    },

    token() {
        return localStorage.getItem(CHAVE_TOKEN);
    },

    /** Dados do usuário logado, ou null se ninguém estiver logado. */
    usuario() {
        const guardado = localStorage.getItem(CHAVE_USUARIO);
        if (!guardado) {
            return null;
        }
        try {
            return JSON.parse(guardado);
        } catch (erro) {
            return null;
        }
    },

    ativa() {
        return Boolean(this.token());
    },

    limpar() {
        localStorage.removeItem(CHAVE_TOKEN);
        localStorage.removeItem(CHAVE_USUARIO);
    },

    /** Sai do sistema e volta para a tela de login. */
    encerrar() {
        this.limpar();
        window.location.replace(PAGINA_LOGIN);
    }
};


/** Monta os cabeçalhos da requisição já com o token, quando existir. */
function cabecalhosAutenticados(extras = {}) {
    const cabecalhos = { ...extras };
    const token = sessao.token();

    if (token) {
        cabecalhos['Authorization'] = 'Bearer ' + token;
    }

    return cabecalhos;
}


/**
 * Envia a requisição e trata a resposta.
 *
 * Quando a API devolve erro, ela manda { "erro": "mensagem" }. Esta
 * função transforma isso numa exceção com a mensagem original, para a
 * tela poder exibi-la ao usuário sem precisar saber de código HTTP.
 *
 * Resposta 401 significa "sessão inválida ou vencida": nesse caso a
 * sessão é apagada e a pessoa volta para a tela de login. Sem isso ela
 * ficaria vendo mensagens de erro sem entender que precisa logar de novo.
 */
async function requisitar(caminho, opcoes = {}) {
    let resposta;

    const { headers: cabecalhosExtras, ...demaisOpcoes } = opcoes;

    try {
        resposta = await fetch(URL_BASE + caminho, {
            ...demaisOpcoes,
            headers: cabecalhosAutenticados({
                'Content-Type': 'application/json',
                ...cabecalhosExtras
            })
        });
    } catch (erro) {
        throw new Error(ERRO_CONEXAO);
    }

    if (resposta.status === 401) {
        sessao.encerrar();
        throw new Error('Sua sessão expirou. Faça login novamente.');
    }

    // 204 não tem corpo para ler.
    if (resposta.status === 204) {
        return null;
    }

    const dados = await resposta.json();

    if (!resposta.ok) {
        throw new Error(dados.erro || 'Erro inesperado no servidor.');
    }

    return dados;
}


/**
 * Envia arquivo por multipart/form-data.
 *
 * Não passa pelo requisitar() porque aquele fixa o Content-Type como
 * application/json. Aqui o navegador precisa montar o Content-Type
 * sozinho, com o boundary do multipart - mas o token continua indo.
 */
async function enviarArquivo(caminho, formData, mensagemErro) {
    let resposta;

    try {
        resposta = await fetch(URL_BASE + caminho, {
            method: 'POST',
            headers: cabecalhosAutenticados(),
            body: formData
        });
    } catch (erro) {
        throw new Error(ERRO_CONEXAO);
    }

    if (resposta.status === 401) {
        sessao.encerrar();
        throw new Error('Sua sessão expirou. Faça login novamente.');
    }

    const dados = await resposta.json();

    if (!resposta.ok) {
        throw new Error(dados.erro || mensagemErro);
    }

    return dados;
}


/**
 * Baixa um arquivo da API.
 *
 * Um <a href> comum não serve mais: o navegador não manda o cabeçalho
 * Authorization num link clicado, então o download voltaria 401. A
 * solução é buscar o arquivo por fetch (com o token), transformar a
 * resposta em blob e disparar o download a partir dele.
 */
async function baixarArquivo(caminho, nomeSugerido) {
    let resposta;

    try {
        resposta = await fetch(URL_BASE + caminho, {
            headers: cabecalhosAutenticados()
        });
    } catch (erro) {
        throw new Error(ERRO_CONEXAO);
    }

    if (resposta.status === 401) {
        sessao.encerrar();
        throw new Error('Sua sessão expirou. Faça login novamente.');
    }

    if (!resposta.ok) {
        throw new Error('Não foi possível baixar o arquivo.');
    }

    const blob = await resposta.blob();
    const endereco = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = endereco;
    link.download = nomeSugerido || 'arquivo';
    document.body.appendChild(link);
    link.click();
    link.remove();

    // Libera a memória do blob só depois que o navegador começou a gravar.
    // Liberar na mesma hora cancela o download em alguns navegadores: o
    // clique só agenda a gravação, e o endereço precisa continuar válido
    // até ela começar de verdade.
    setTimeout(() => URL.revokeObjectURL(endereco), 60000);
}

const api = {

    /* -----------------------------------------------------------------
       Autenticação
       ----------------------------------------------------------------- */
    auth: {

        /**
         * Faz o login. Não passa pelo requisitar() de propósito: um 401
         * aqui significa "senha errada", e não "sessão vencida" - não
         * pode disparar o redirecionamento para a tela de login, senão
         * a própria tela de login recarregaria sozinha.
         */
        async entrar(email, senha) {
            let resposta;

            try {
                resposta = await fetch(URL_BASE + '/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, senha })
                });
            } catch (erro) {
                throw new Error(ERRO_CONEXAO);
            }

            const dados = await resposta.json();

            if (!resposta.ok) {
                throw new Error(dados.erro || 'Não foi possível entrar.');
            }

            sessao.salvar(dados.token, dados.usuario);
            return dados.usuario;
        },

        /** Confere com o backend quem está logado, a partir do token. */
        eu() {
            return requisitar('/usuarios/eu');
        }
    },

    clientes: {

        /** Lista os clientes. Passe true para incluir os inativos. */
        listar(incluirInativos = false) {
            const filtro = incluirInativos ? '?incluir_inativos=true' : '';
            return requisitar('/clientes' + filtro);
        },

        /** Funcionalidade 01 - Busca por Nome. */
        buscarPorNome(termo) {
            return requisitar('/clientes/busca?nome=' + encodeURIComponent(termo));
        },

        /** Funcionalidade 02 - Busca por Documento. */
        buscarPorDocumento(documento) {
            const numeros = documento.replace(/\D/g, '');
            return requisitar('/clientes/documento/' + numeros);
        },

        buscarPorId(id) {
            return requisitar('/clientes/' + id);
        },

        criar(dados) {
            return requisitar('/clientes', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
        },

        atualizar(id, dados) {
            return requisitar('/clientes/' + id, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
        },

        excluir(id) {
            return requisitar('/clientes/' + id, { method: 'DELETE' });
        }
    },

    processos: {

        /** Lista os processos. Passe um cliente_id para filtrar. */
        listar(incluirInativos = false, clienteId = null) {
            if (clienteId) {
                return requisitar('/processos?cliente_id=' + clienteId);
            }
            const filtro = incluirInativos ? '?incluir_inativos=true' : '';
            return requisitar('/processos' + filtro);
        },

        /** Funcionalidade 03 - Busca por Processo (número exato). */
        buscarPorNumero(numero) {
            return requisitar('/processos/numero?valor=' + encodeURIComponent(numero));
        },

        /**
         * Funcionalidade 03 - busca combinada via sp_buscar_processos.
         * Procura no número, no título e no nome do cliente ao mesmo
         * tempo, e aceita filtros opcionais de status, advogado e tipo.
         */
        buscar(filtros = {}) {
            const p = new URLSearchParams();
            if (filtros.termo)      { p.set('termo', filtros.termo); }
            if (filtros.statusId)   { p.set('status_id', filtros.statusId); }
            if (filtros.advogadoId) { p.set('advogado_id', filtros.advogadoId); }
            if (filtros.tipoId)     { p.set('tipo_id', filtros.tipoId); }
            const query = p.toString();
            return requisitar('/processos/busca' + (query ? '?' + query : ''));
        },

        /** Funcionalidade 14 - Marcadores Visuais. */
        marcadores(id) {
            return requisitar('/processos/' + id + '/marcadores');
        },

        aplicarMarcador(id, marcadorId) {
            return requisitar('/processos/' + id + '/marcadores', {
                method: 'POST',
                body: JSON.stringify({ marcador_id: marcadorId })
            });
        },

        removerMarcador(id, marcadorId) {
            return requisitar('/processos/' + id + '/marcadores/' + marcadorId, {
                method: 'DELETE'
            });
        },

        buscarPorId(id) {
            return requisitar('/processos/' + id);
        },

        /** Alimenta os selects do formulario numa única chamada. */
        opcoes() {
            return requisitar('/processos/opcoes');
        },

        /** Funcionalidade 07 - histórico de mudancas de fase. */
        historico(id) {
            return requisitar('/processos/' + id + '/historico');
        },

        /** Funcionalidades 11 e 12 - checklist e pendências. */
        checklist(id) {
            return requisitar('/processos/' + id + '/checklist');
        },

        criar(dados) {
            return requisitar('/processos', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
        },

        atualizar(id, dados) {
            return requisitar('/processos/' + id, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
        },

        /** Funcionalidade 07 - Atualizacao de Status. */
        atualizarStatus(id, dados) {
            return requisitar('/processos/' + id + '/status', {
                method: 'PATCH',
                body: JSON.stringify(dados)
            });
        },

        excluir(id) {
            return requisitar('/processos/' + id, { method: 'DELETE' });
        }
    },

    usuarios: {

        listar(incluirInativos = false) {
            const filtro = incluirInativos ? '?incluir_inativos=true' : '';
            return requisitar('/usuarios' + filtro);
        },

        /** Perfis disponiveis: Admin, Advogado, Secretaria. */
        perfis() {
            return requisitar('/usuarios/perfis');
        },

        buscarPorId(id) {
            return requisitar('/usuarios/' + id);
        },

        criar(dados) {
            return requisitar('/usuarios', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
        },

        atualizar(id, dados) {
            return requisitar('/usuarios/' + id, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
        },

        alterarSenha(id, senha) {
            return requisitar('/usuarios/' + id + '/senha', {
                method: 'PATCH',
                body: JSON.stringify({ senha })
            });
        },

        excluir(id) {
            return requisitar('/usuarios/' + id, { method: 'DELETE' });
        }
    },

    documentos: {

        listar(filtros = {}) {
            const p = new URLSearchParams();
            if (filtros.processoId) { p.set('processo_id', filtros.processoId); }
            if (filtros.clienteId)  { p.set('cliente_id', filtros.clienteId); }
            if (filtros.incluirExcluidos) { p.set('incluir_excluidos', 'true'); }
            const query = p.toString();
            return requisitar('/documentos' + (query ? '?' + query : ''));
        },

        /** Categorias jurídicas. Funcionalidade 09. */
        categorias() {
            return requisitar('/documentos/categorias');
        },

        /**
         * Envia o arquivo. Funcionalidades 09, 10, 11 e 17.
         *
         * Aqui Não usamos JSON: arquivo vai por multipart/form-data. Por
         * isso a chamada não passa pela função requisitar(), que fixa o
         * cabecalho como application/json. O navegador precisa montar o
         * Content-Type sozinho, com o boundary do multipart.
         */
        enviar(formData) {
            return enviarArquivo(
                '/documentos', formData, 'Erro ao enviar o documento.'
            );
        },

        atualizar(id, dados) {
            return requisitar('/documentos/' + id, {
                method: 'PUT',
                body: JSON.stringify(dados)
            });
        },

        /**
         * Funcionalidade 20: exige um usuário com permissão.
         *
         * Não recebe mais o id de quem está excluindo. O backend
         * descobre isso pelo token e confere o perfil - antes o
         * frontend informava o id e o backend acreditava.
         */
        excluir(id) {
            return requisitar('/documentos/' + id, { method: 'DELETE' });
        },

        restaurar(id) {
            return requisitar('/documentos/' + id + '/restaurar', {
                method: 'PATCH'
            });
        },

        /** Baixa o arquivo levando o token junto. */
        baixar(id, nomeSugerido) {
            return baixarArquivo('/documentos/' + id + '/arquivo', nomeSugerido);
        }
    },

    notificacoes: {

        /** Traz os avisos de quem está logado (o backend usa o token). */
        listar(apenasNaoLidas = false) {
            const filtro = apenasNaoLidas ? '?nao_lidas=true' : '';
            return requisitar('/notificacoes' + filtro);
        },

        marcarLida(id) {
            return requisitar('/notificacoes/' + id + '/lida', { method: 'PATCH' });
        }
    },

    /* -----------------------------------------------------------------
       Painel - Terceira Etapa
       Cada metodo aqui chama uma stored procedure do MySQL, por meio da
       camada Repository do backend.
       ----------------------------------------------------------------- */
    painel: {

        /** sp_painel_resumo - Funcionalidade 06 */
        resumo() {
            return requisitar('/painel/resumo');
        },

        /** sp_pendencias_checklist - Funcionalidade 12 */
        pendencias(advogadoId = null) {
            const filtro = advogadoId ? '?advogado_id=' + advogadoId : '';
            return requisitar('/painel/pendencias' + filtro);
        },

        /** sp_processos_prioritarios - Funcionalidades 14 e 15 */
        prioritarios(pesoMinimo = null, advogadoId = null) {
            const p = new URLSearchParams();
            if (pesoMinimo) { p.set('peso_minimo', pesoMinimo); }
            if (advogadoId) { p.set('advogado_id', advogadoId); }
            const query = p.toString();
            return requisitar('/painel/prioritarios' + (query ? '?' + query : ''));
        },

        /** Marcadores fixos do sistema. */
        marcadores() {
            return requisitar('/painel/marcadores');
        }
    },

    /* Configuração de checklist por tipo de processo (Funcionalidade 13). */
    checklists: {

        opcoes() {
            return requisitar('/checklists/opcoes');
        },

        listar(tipoProcessoId) {
            return requisitar('/checklists?tipo_processo_id=' + tipoProcessoId);
        },

        adicionar(dados) {
            return requisitar('/checklists', {
                method: 'POST',
                body: JSON.stringify(dados)
            });
        },

        alternarObrigatorio(id) {
            return requisitar('/checklists/' + id + '/obrigatorio', {
                method: 'PATCH'
            });
        },

        remover(id) {
            return requisitar('/checklists/' + id, { method: 'DELETE' });
        }
    },

    /* Importação em lote (Funcionalidades 18 e 19). */
    importacoes: {

        listar() {
            return requisitar('/importacoes');
        },

        clientes(id) {
            return requisitar('/importacoes/' + id + '/clientes');
        },

        /* Planilha vai por multipart, então não passa pelo requisitar(),
           que fixa o cabeçalho como application/json. */
        enviar(formData) {
            return enviarArquivo(
                '/importacoes', formData, 'Erro ao importar a planilha.'
            );
        },

        desfazer(id) {
            return requisitar('/importacoes/' + id, { method: 'DELETE' });
        },

        /** Baixa o CSV de exemplo levando o token junto. */
        baixarModelo() {
            return baixarArquivo(
                '/importacoes/modelo', 'modelo_importacao_clientes.csv'
            );
        }
    }
};

/* =====================================================================
   Funções de apoio usadas pelas telas
   ===================================================================== */

/** Deixa só os números de um texto. */
function somenteNumeros(texto) {
    return (texto || '').replace(/\D/g, '');
}

/**
 * Formata CPF ou CNPJ conforme o usuário digita.
 * Decide o formato pela quantidade de digitos, não pelo tipo escolhido,
 * para o campo funcionar mesmo antes de o tipo ser selecionado.
 */
function formatarDocumento(valor) {
    const d = somenteNumeros(valor).slice(0, 14);

    if (d.length <= 11) {
        return d
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d)/, '$1.$2')
            .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    }

    return d
        .replace(/^(\d{2})(\d)/, '$1.$2')
        .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
        .replace(/\.(\d{3})(\d)/, '.$1/$2')
        .replace(/(\d{4})(\d{1,2})$/, '$1-$2');
}

/**
 * Escapa caracteres especiais antes de inserir texto no HTML.
 *
 * Sem isso, um cliente chamado 'Silva "Junior" & Cia' quebraria o
 * desenho da lista - e, num sistema real, permitiria injetar código.
 */
function escaparHtml(texto) {
    if (texto === null || texto === undefined) {
        return '';
    }
    return String(texto)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/** Mostra um aviso de erro ou sucesso no topo da tela. */
function mostrarAviso(elemento, mensagem, tipo = 'erro') {
    elemento.textContent = mensagem;
    elemento.className = 'aviso aviso-' + tipo;
}

/** Esconde o aviso. */
function limparAviso(elemento) {
    elemento.textContent = '';
    elemento.className = 'escondido';
}


/**
 * Converte 2026-08-06 para 06/08/2026. Vazio vira travessao.
 *
 * Aceita também o formato HTTP ("Sat, 15 Aug 2026 00:00:00 GMT"), que e
 * como o Flask serializa datas quando elas não passam por isoformat().
 * O backend já normaliza tudo para ISO, mas a tela não quebra se algum
 * campo escapar.
 */
function formatarData(valor) {
    if (!valor) {
        return '\u2014';
    }

    const texto = String(valor);

    // Formato ISO: 2026-08-15 ou 2026-08-15T14:30:00
    if (/^\d{4}-\d{2}-\d{2}/.test(texto)) {
        const [ano, mes, dia] = texto.split('T')[0].split('-');
        return `${dia}/${mes}/${ano}`;
    }

    // Qualquer outro formato que o navegador consiga interpretar.
    const data = new Date(texto);
    if (isNaN(data.getTime())) {
        return texto;
    }

    return data.toLocaleDateString('pt-BR');
}

/** Converte 1500.5 para R$ 1.500,50. */
function formatarDinheiro(valor) {
    if (valor === null || valor === undefined) {
        return '\u2014';
    }
    return valor.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

/**
 * Mascara de telefone. Aceita fixo e celular:
 *   (31) 3333-4444    -> 10 digitos
 *   (31) 99999-8888   -> 11 digitos
 */
function formatarTelefone(valor) {
    const d = somenteNumeros(valor).slice(0, 11);

    if (d.length <= 2) {
        return d;
    }
    if (d.length <= 6) {
        return `(${d.slice(0, 2)}) ${d.slice(2)}`;
    }
    if (d.length <= 10) {
        return `(${d.slice(0, 2)}) ${d.slice(2, 6)}-${d.slice(6)}`;
    }
    return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`;
}

/**
 * Mascara do número único de processo (padrão CNJ).
 * Formato: NNNNNNN-DD.AAAA.J.TR.OOOO  -> 20 digitos
 * Exemplo: 0001234-56.2026.8.13.0024
 */
function formatarNumeroProcesso(valor) {
    const d = somenteNumeros(valor).slice(0, 20);

    let saida = d.slice(0, 7);
    if (d.length > 7)  { saida += '-' + d.slice(7, 9); }
    if (d.length > 9)  { saida += '.' + d.slice(9, 13); }
    if (d.length > 13) { saida += '.' + d.slice(13, 14); }
    if (d.length > 14) { saida += '.' + d.slice(14, 16); }
    if (d.length > 16) { saida += '.' + d.slice(16, 20); }

    return saida;
}

/** Deixa só letras, em maiuscula. Usado na sigla do estado. */
function formatarUF(valor) {
    return (valor || '').replace(/[^a-zA-Z]/g, '').toUpperCase().slice(0, 2);
}

/**
 * Liga uma mascara a um campo.
 *
 * Aplica a formatação a cada tecla digitada e também ao colar texto.
 * Como toda mascara e apenas visual, o valor limpo e recuperado com
 * somenteNumeros() na hora de enviar para a API.
 */
function aplicarMascara(campo, funcaoMascara) {
    if (!campo) {
        return;
    }
    campo.addEventListener('input', (evento) => {
        evento.target.value = funcaoMascara(evento.target.value);
    });
}


/** Converte 2048 KB para "2,0 MB"; abaixo de 1024 mostra em KB. */
function formatarTamanho(kb) {
    if (!kb) {
        return '\u2014';
    }
    if (kb < 1024) {
        return kb + ' KB';
    }
    return (kb / 1024).toFixed(1).replace('.', ',') + ' MB';
}


/* =====================================================================
   Guarda de sessão e barra do usuário
   =====================================================================
   Este trecho roda sozinho assim que o api.js é carregado, em todas as
   telas. Ele faz duas coisas:

     1. Se não houver sessão, manda a pessoa para a tela de login antes
        de a tela aparecer. É a trava do lado do navegador - a trava que
        realmente importa é a do backend, que recusa qualquer requisição
        sem token válido.

     2. Se houver sessão, desenha no canto do cabeçalho o nome e o perfil
        de quem está logado, junto do botão "Sair".

   Fazer isso aqui, em vez de repetir em cada arquivo HTML, evita que
   uma tela nova esqueça a proteção.
   ===================================================================== */

/** Nome do arquivo da página aberta (ex: "clientes.html"). */
function paginaAtual() {
    const caminho = window.location.pathname.split('/').pop();
    return caminho || 'index.html';
}


/** Desenha o nome, o perfil e o botão Sair no cabeçalho. */
function montarBarraUsuario() {
    const usuario = sessao.usuario();
    const cabecalho = document.querySelector('.cabecalho-conteudo');

    if (!usuario || !cabecalho) {
        return;
    }

    const caixa = document.createElement('div');
    caixa.className = 'usuario-sessao';
    caixa.innerHTML = `
        <div class="usuario-dados">
            <span class="usuario-nome">${escaparHtml(usuario.nome)}</span>
            <span class="usuario-perfil">${escaparHtml(usuario.perfil_nome)}</span>
        </div>
        <button type="button" class="botao botao-pequeno" id="botao-sair">
            Sair
        </button>
    `;

    cabecalho.appendChild(caixa);

    document.getElementById('botao-sair').addEventListener('click', () => {
        sessao.encerrar();
    });
}


if (paginaAtual() !== PAGINA_LOGIN) {
    if (!sessao.ativa()) {
        // replace() em vez de href: assim o botão "voltar" do navegador
        // não devolve a pessoa para a tela protegida.
        window.location.replace(PAGINA_LOGIN);
    } else {
        document.addEventListener('DOMContentLoaded', montarBarraUsuario);
    }
}
