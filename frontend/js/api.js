/*
==============================================================================
SEÇÃO COMENTÁRIOS — api.js: Funções usadas por todas as páginas: chamadas à API, sessão de login, máscaras e formatação
Formato: caminho do elemento no HTML> nome no código: o que faz
==============================================================================
global> URL_BASE: Endereço da API Flask que todas as telas chamam
global> PAGINA_LOGIN: Página para onde a pessoa vai quando não está logada
global> ERRO_CONEXAO: Mensagem mostrada quando o servidor não responde
global> SESSAO_EXPIRADA: Mensagem mostrada quando o token vence ou é recusado (401)
global> CHAVE_TOKEN: Nomes usados para guardar no navegador o token, o usuário e o aviso que o login deve mostrar
global> sessao: Cuida do login guardado no navegador (localStorage)
global> sessao.salvar(): Guarda o token e os dados de quem entrou
global> sessao.token(): Devolve o token guardado
global> sessao.usuario(): Devolve os dados do usuário guardado (ou nada, se não houver)
global> sessao.ativa(): Diz se existe alguém logado
global> sessao.limpar(): Apaga o token e o usuário do navegador
global> sessao.encerrar(): Faz logout e volta para a tela de login; se receber um motivo, guarda para o login mostrar
global> cabecalhosAutenticados(): Monta os cabeçalhos da requisição já com o token (Authorization: Bearer)
global> requisitar(): Função central que chama a API com JSON: trata erro de conexão, sessão vencida (401) e mensagens de erro
global> enviarArquivo(): Envia arquivo para a API (upload de documento e de planilha)
global> baixarArquivo(): Baixa um arquivo da API levando o token e dispara o download no navegador
global> api: Todas as chamadas à API, separadas por módulo
global> api.auth: Login: entrar
global> api.clientes: Chamadas de clientes: listar, buscarPorNome, buscarPorDocumento, buscarPorId, criar, atualizar, excluir
global> api.processos: Chamadas de processos: listar, buscar, marcadores, aplicarMarcador, removerMarcador, buscarPorId, opcoes, historico, checklist, criar, atualizar, atualizarStatus, excluir
global> api.usuarios: Chamadas de usuários: listar, perfis, buscarPorId, criar, atualizar, alterarSenha, excluir
global> api.documentos: Chamadas de documentos: listar, categorias, enviar, atualizar, excluir, restaurar, baixar
global> api.notificacoes: Chamadas de avisos: listar, marcarLida
global> api.painel: Chamadas do painel: resumo, pendencias, prioritarios, marcadores
global> api.checklists: Chamadas da configuração de checklist: opcoes, listar, adicionar, alternarObrigatorio, remover
global> api.importacoes: Chamadas da importação: listar, clientes, enviar, desfazer, baixarModelo
global> somenteNumeros(): Deixa só os números de um texto
global> formatarDocumento(): Formata CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00) enquanto digita
    HTML: cliente-form>main>form>div>div>input> (campo CPF / CNPJ)
global> escaparHtml(): Protege o texto antes de colocar no HTML (evita código malicioso)
global> mostrarAviso(): Mostra uma mensagem na caixa de aviso (erro ou sucesso)
    HTML: caixa de aviso de cada página, ex.: login>main>div>, clientes>main>div>
global> limparAviso(): Limpa e esconde a caixa de aviso
    HTML: caixa de aviso de cada página, ex.: login>main>div>, clientes>main>div>
global> formatarData(): Mostra data no formato dd/mm/aaaa
global> formatarDinheiro(): Mostra valor em reais (R$)
global> formatarTelefone(): Formata telefone (31) 99999-9999 enquanto digita
    HTML: cliente-form>main>form>div>div>input> (campo Telefone)
global> formatarNumeroProcesso(): Formata o número do processo no padrão do CNJ enquanto digita
    HTML: processo-form>main>form>div>div>input> (campo Número do processo)
global> formatarUF(): Deixa o estado com 2 letras maiúsculas
    HTML: cliente-form>main>form>div>div>input> (campo Estado)
global> aplicarMascara(): Liga uma máscara a um campo: formata a cada tecla
global> formatarTamanho(): Mostra o tamanho do arquivo em KB ou MB
global> paginaAtual(): Descobre o nome do arquivo da página aberta
global>header>div> montarBarraUsuario(): Coloca no topo o nome, o perfil e o botão Sair de quem está logado
    HTML: painel>header>div>, clientes>header>div>, cliente-form>header>div>, processos>header>div>, processo-form>header>div>, processo-detalhe>header>div>, documentos>header>div>, notificacoes>header>div>, checklists>header>div>, importacoes>header>div>, usuarios>header>div>, usuario-form>header>div>
global>header>div>div>button> #botao-sair (click): Clicar em Sair encerra a sessão
    HTML: <página>>header>div>div>button> (botão Sair, criado pelo JS em todas as páginas com menu)
global> ao abrir qualquer página: Em toda página (menos o login): sem sessão volta para o login; com sessão monta a barra do usuário
==============================================================================
*/

const URL_BASE = 'http://localhost:5000/api';

const PAGINA_LOGIN = 'login.html';

const ERRO_CONEXAO =
    'Não foi possível falar com o servidor. ' +
    'Confira se o WAMP está ligado e se o run.py está rodando.';

const SESSAO_EXPIRADA = 'Sua sessão expirou. Faça login novamente.';

const CHAVE_TOKEN = 'tabflower_token';
const CHAVE_USUARIO = 'tabflower_usuario';
const CHAVE_AVISO = 'tabflower_aviso';

const sessao = {

    salvar(token, usuario) {
        localStorage.setItem(CHAVE_TOKEN, token);
        localStorage.setItem(CHAVE_USUARIO, JSON.stringify(usuario));
    },

    token() {
        return localStorage.getItem(CHAVE_TOKEN);
    },

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

    encerrar(motivo) {
        this.limpar();
        if (motivo) {
            sessionStorage.setItem(CHAVE_AVISO, motivo);
        }
        window.location.replace(PAGINA_LOGIN);
    }
};

function cabecalhosAutenticados(extras = {}) {
    const cabecalhos = { ...extras };
    const token = sessao.token();

    if (token) {
        cabecalhos['Authorization'] = 'Bearer ' + token;
    }

    return cabecalhos;
}

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
        sessao.encerrar(SESSAO_EXPIRADA);
        throw new Error(SESSAO_EXPIRADA);
    }

    if (resposta.status === 204) {
        return null;
    }

    const dados = await resposta.json();

    if (!resposta.ok) {
        throw new Error(dados.erro || 'Erro inesperado no servidor.');
    }

    return dados;
}

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
        sessao.encerrar(SESSAO_EXPIRADA);
        throw new Error(SESSAO_EXPIRADA);
    }

    const dados = await resposta.json();

    if (!resposta.ok) {
        throw new Error(dados.erro || mensagemErro);
    }

    return dados;
}

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
        sessao.encerrar(SESSAO_EXPIRADA);
        throw new Error(SESSAO_EXPIRADA);
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

    setTimeout(() => URL.revokeObjectURL(endereco), 60000);
}

const api = {

    auth: {

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
        }
    },

    clientes: {

        listar(incluirInativos = false) {
            const filtro = incluirInativos ? '?incluir_inativos=true' : '';
            return requisitar('/clientes' + filtro);
        },

        buscarPorNome(termo, incluirInativos = false) {
            const filtro = incluirInativos ? '&incluir_inativos=true' : '';
            return requisitar('/clientes/busca?nome=' + encodeURIComponent(termo) + filtro);
        },

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

        listar(incluirInativos = false) {
            const filtro = incluirInativos ? '?incluir_inativos=true' : '';
            return requisitar('/processos' + filtro);
        },

        buscar(filtros = {}) {
            const p = new URLSearchParams();
            if (filtros.termo)      { p.set('termo', filtros.termo); }
            if (filtros.statusId)   { p.set('status_id', filtros.statusId); }
            if (filtros.advogadoId) { p.set('advogado_id', filtros.advogadoId); }
            if (filtros.tipoId)     { p.set('tipo_id', filtros.tipoId); }
            if (filtros.incluirInativos) { p.set('incluir_inativos', 'true'); }
            const query = p.toString();
            return requisitar('/processos/busca' + (query ? '?' + query : ''));
        },

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

        opcoes() {
            return requisitar('/processos/opcoes');
        },

        historico(id) {
            return requisitar('/processos/' + id + '/historico');
        },

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
            if (filtros.incluirExcluidos) { p.set('incluir_excluidos', 'true'); }
            const query = p.toString();
            return requisitar('/documentos' + (query ? '?' + query : ''));
        },

        categorias() {
            return requisitar('/documentos/categorias');
        },

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

        excluir(id) {
            return requisitar('/documentos/' + id, { method: 'DELETE' });
        },

        restaurar(id) {
            return requisitar('/documentos/' + id + '/restaurar', {
                method: 'PATCH'
            });
        },

        baixar(id, nomeSugerido) {
            return baixarArquivo('/documentos/' + id + '/arquivo', nomeSugerido);
        }
    },

    notificacoes: {

        listar(apenasNaoLidas = false) {
            const filtro = apenasNaoLidas ? '?nao_lidas=true' : '';
            return requisitar('/notificacoes' + filtro);
        },

        marcarLida(id) {
            return requisitar('/notificacoes/' + id + '/lida', { method: 'PATCH' });
        }
    },

    painel: {

        resumo() {
            return requisitar('/painel/resumo');
        },

        pendencias(advogadoId = null) {
            const filtro = advogadoId ? '?advogado_id=' + advogadoId : '';
            return requisitar('/painel/pendencias' + filtro);
        },

        prioritarios(pesoMinimo = null, advogadoId = null) {
            const p = new URLSearchParams();
            if (pesoMinimo) { p.set('peso_minimo', pesoMinimo); }
            if (advogadoId) { p.set('advogado_id', advogadoId); }
            const query = p.toString();
            return requisitar('/painel/prioritarios' + (query ? '?' + query : ''));
        },

        marcadores() {
            return requisitar('/painel/marcadores');
        }
    },

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

    importacoes: {

        listar() {
            return requisitar('/importacoes');
        },

        clientes(id) {
            return requisitar('/importacoes/' + id + '/clientes');
        },

        enviar(formData) {
            return enviarArquivo(
                '/importacoes', formData, 'Erro ao importar a planilha.'
            );
        },

        desfazer(id) {
            return requisitar('/importacoes/' + id, { method: 'DELETE' });
        },

        baixarModelo() {
            return baixarArquivo(
                '/importacoes/modelo', 'modelo_importacao_clientes.csv'
            );
        }
    }
};

function somenteNumeros(texto) {
    return (texto || '').replace(/\D/g, '');
}

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

function mostrarAviso(elemento, mensagem, tipo = 'erro') {
    elemento.textContent = mensagem;
    elemento.className = 'aviso aviso-' + tipo;
}

function limparAviso(elemento) {
    elemento.textContent = '';
    elemento.className = 'escondido';
}

function formatarData(valor) {
    if (!valor) {
        return '\u2014';
    }

    const texto = String(valor);

    if (/^\d{4}-\d{2}-\d{2}/.test(texto)) {
        const [ano, mes, dia] = texto.split('T')[0].split('-');
        return `${dia}/${mes}/${ano}`;
    }

    const data = new Date(texto);
    if (isNaN(data.getTime())) {
        return texto;
    }

    return data.toLocaleDateString('pt-BR');
}

function formatarDinheiro(valor) {
    if (valor === null || valor === undefined) {
        return '\u2014';
    }
    return valor.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

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

function formatarUF(valor) {
    return (valor || '').replace(/[^a-zA-Z]/g, '').toUpperCase().slice(0, 2);
}

function aplicarMascara(campo, funcaoMascara) {
    if (!campo) {
        return;
    }
    campo.addEventListener('input', (evento) => {
        evento.target.value = funcaoMascara(evento.target.value);
    });
}

function formatarTamanho(kb) {
    if (!kb) {
        return '\u2014';
    }
    if (kb < 1024) {
        return kb + ' KB';
    }
    return (kb / 1024).toFixed(1).replace('.', ',') + ' MB';
}

function paginaAtual() {
    const caminho = window.location.pathname.split('/').pop();
    return caminho || 'index.html';
}

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
        window.location.replace(PAGINA_LOGIN);
    } else {
        document.addEventListener('DOMContentLoaded', montarBarraUsuario);
    }
}
