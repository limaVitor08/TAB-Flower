# TabFlower

Sistema de gestão documental e processual para escritórios de advocacia.

Projeto de Conclusão de Curso — Colégio COTEMIG
Disciplina: Projeto de Software — Prof. Gleison Brito

**Equipe:** Gabriel Mazzega, Gabriel Almeida, Gabriel Fernandes, Vitor Papini, Nnamdi Delfino

---

## O problema

A equipe administrativa de escritórios de advocacia perde horas faturáveis em tarefas manuais: criar pastas para cada cliente, renomear PDFs escaneados um a um, conferir checklists impressos e manter planilhas paralelas que ficam desatualizadas. O resultado é lentidão para localizar arquivos, risco de extravio de documentos e ausência total de rastreabilidade — quando algo some, ninguém sabe quem moveu ou apagou.

O TabFlower centraliza clientes, processos e documentos, automatiza a criação de diretórios e a padronização de nomes de arquivo, substitui os controles em papel por checklist digital e registra quem fez cada ação.

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Flask |
| ORM | SQLAlchemy (Flask-SQLAlchemy) |
| Banco de dados | MySQL 8 (WAMP Server) |
| Frontend | HTML, CSS e JavaScript |

---

## Arquitetura

Monólito modular em 5 camadas, no padrão MVC + Services + Model (Active Record) + Repository.

| Camada | Pasta | Responsabilidade |
|---|---|---|
| Apresentação | `routes.py` + `controllers/` | Recebe requisições HTTP e devolve JSON |
| Aplicação | `services/` | Um Service por caso de uso; valida e orquestra |
| Domínio | `models/` | Entidades e CRUD básico (herdam de `db.Model`) |
| Persistência especializada | `repositories/` | Consultas com filtro, JOIN e ordenação |
| Infraestrutura | `extensions.py` | Instância única do SQLAlchemy (Singleton) + MySQL |

**Regra de decisão:** CRUD simples fica na Model. Consulta com filtro, JOIN, ordenação ou relatório fica no Repository.

Três exemplos concretos dessa separação no código:

- `Cliente.salvar()` — CRUD puro, resolvido pela Model via Active Record.
- `ClienteRepository.buscar_por_nome()` — usa `LIKE` com filtro parcial, então mora no Repository.
- `CriarProcessoService` — orquestra: valida vínculos, chama a Model para salvar, monta o checklist a partir do molde e grava o histórico. Nenhuma dessas decisões cabe na Model nem no Controller.

O Controller nunca contém regra de negócio nem SQL. O `routes.py` apenas aponta cada rota para um método de Controller.

---

## Estrutura do repositório

```
tabflower/
├── README.md
├── frontend/
│   ├── index.html             (redireciona para o login)
│   ├── login.html             Porta de entrada do sistema
│   ├── clientes.html          cliente-form.html
│   ├── processos.html         processo-form.html      processo-detalhe.html
│   ├── documentos.html
│   ├── painel.html            checklists.html
│   ├── notificacoes.html      importacoes.html
│   ├── usuarios.html          usuario-form.html
│   ├── css/estilo.css
│   └── js/
│       ├── api.js             (acesso à API, sessão, máscaras e apoio)
│       ├── login.js
│       ├── clientes.js        cliente-form.js
│       ├── processos.js       processo-form.js       processo-detalhe.js
│       ├── documentos.js
│       ├── painel.js          checklists.js
│       ├── notificacoes.js    importacoes.js
│       └── usuarios.js        usuario-form.js
└── backend/
    ├── run.py                 Ponto de entrada
    ├── criar_primeiro_usuario.py   Cadastra o primeiro Admin (rodar uma vez)
    ├── app.py                 Application factory
    ├── config.py              Configuração e string de conexão
    ├── extensions.py          Instância única do SQLAlchemy (Singleton)
    ├── routes.py              Registro central das rotas
    ├── requirements.txt
    ├── .env.example
    ├── controllers/           Controllers, incluindo auth_controller.py
    ├── services/              Services agrupados por entidade (+ services/auth/)
    ├── models/                15 Models
    ├── repositories/          Consultas específicas
    ├── utils/                 Validador de CPF/CNPJ, gerenciador de arquivos,
    │                          token.py e autenticacao.py (login)
    └── database/
        └── create_database.sql
```

---

## Models implementadas

| Model | Tabela | Papel |
|---|---|---|
| `Cliente` | `cliente` | Pessoa física ou jurídica atendida |
| `Usuario` | `usuario` | Equipe do escritório |
| `Perfil` | `perfil` | Nível de permissão (Admin, Advogado, Secretária) |
| `Processo` | `processo` | Ação judicial |
| `HistoricoStatus` | `historico_status` | Cada mudança de fase do processo |
| `Documento` | `documento` | Arquivo anexado |
| `Notificacao` | `notificacao` | Avisos internos ao advogado |
| `ChecklistModelo` | `checklist_modelo` | Documentos exigidos por tipo de processo |
| `ChecklistProcesso` | `checklist_processo` | Checklist aplicado a um processo |
| `TipoProcesso` | `tipo_processo` | Trabalhista, Cível, Família... |
| `StatusProcesso` | `status_processo` | Fases do andamento |
| `Marcador` | `marcador` | Etiquetas de prioridade |
| `CategoriaDocumento` | `categoria_documento` | Classificação jurídica do arquivo |
| `ImportacaoLote` | `importacao_lote` | Carga de clientes vinda de planilha |
| `LogAuditoria` | `log_auditoria` | Registro de exclusões, restaurações e logins |

O banco tem 16 tabelas. A única sem Model própria é `processo_marcador`, tabela de ligação N:N entre processo e marcador, manipulada pelo `MarcadoresService` e pelas stored procedures.

---

## Rotas da API

Todas devolvem JSON, inclusive nos erros.

**Todas as rotas exigem login**, exceto `/api/status` e `/api/auth/login`. As demais só respondem se a requisição trouxer o cabeçalho `Authorization: Bearer <token>` com um token válido — sem ele, a resposta é `401`.

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login` | Recebe e-mail e senha, devolve o token e os dados do usuário |
| GET | `/api/usuarios/eu` | Dados de quem está logado, lidos do token |

### Diagnóstico

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/status` | Verifica se a API e o banco estão acessíveis |

### Clientes

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/clientes` | Lista clientes ativos (`?incluir_inativos=true` traz todos) |
| GET | `/api/clientes/busca?nome=` | Busca parcial por nome |
| GET | `/api/clientes/documento/<documento>` | Busca por CPF/CNPJ |
| GET | `/api/clientes/<id>` | Busca por id |
| POST | `/api/clientes` | Cadastra cliente e cria a pasta dele |
| PUT | `/api/clientes/<id>` | Atualiza dados |
| DELETE | `/api/clientes/<id>` | Desativa (exclusão lógica) |

### Processos

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/processos` | Lista processos (`?cliente_id=` filtra por cliente) |
| GET | `/api/processos/opcoes` | Tipos, status e advogados para os selects |
| GET | `/api/processos/busca` | Busca combinada via `sp_buscar_processos` |
| GET | `/api/processos/numero?valor=` | Busca pelo número da ação |
| GET | `/api/processos/<id>` | Busca por id |
| GET | `/api/processos/<id>/historico` | Histórico de mudanças de fase |
| GET | `/api/processos/<id>/checklist` | Checklist de documentos |
| POST | `/api/processos` | Abre processo e monta o checklist |
| PUT | `/api/processos/<id>` | Atualiza dados |
| PATCH | `/api/processos/<id>/status` | Muda a fase e registra no histórico |
| DELETE | `/api/processos/<id>` | Arquiva (exclusão lógica) |

### Documentos

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/documentos` | Lista o acervo (`?processo_id=`, `?cliente_id=`) |
| GET | `/api/documentos/categorias` | Categorias jurídicas |
| GET | `/api/documentos/<id>` | Busca por id |
| GET | `/api/documentos/<id>/arquivo` | Baixa o arquivo |
| POST | `/api/documentos` | Envia arquivo (multipart/form-data) |
| PUT | `/api/documentos/<id>` | Corrige a categoria |
| PATCH | `/api/documentos/<id>/restaurar` | Restaura documento excluído |
| DELETE | `/api/documentos/<id>` | Exclui logicamente (só Admin) |

### Usuários

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/usuarios` | Lista usuários |
| GET | `/api/usuarios/perfis` | Perfis disponíveis |
| GET | `/api/usuarios/advogados` | Somente advogados |
| GET | `/api/usuarios/<id>` | Busca por id |
| POST | `/api/usuarios` | Cadastra usuário (senha com hash) |
| PUT | `/api/usuarios/<id>` | Atualiza dados |
| PATCH | `/api/usuarios/<id>/senha` | Troca a senha |
| DELETE | `/api/usuarios/<id>` | Desativa |

### Notificações

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/notificacoes` | Avisos de quem está logado (`?nao_lidas=true`) |
| PATCH | `/api/notificacoes/<id>/lida` | Marca como lida |

### Configuração de checklist

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/checklists/opcoes` | Tipos de processo e categorias |
| GET | `/api/checklists?tipo_processo_id=` | Exigências de um tipo |
| POST | `/api/checklists` | Acrescenta uma exigência |
| PATCH | `/api/checklists/<id>/obrigatorio` | Alterna obrigatório/opcional |
| DELETE | `/api/checklists/<id>` | Remove a exigência do molde |

### Importação em lote

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/importacoes` | Histórico de cargas |
| GET | `/api/importacoes/modelo` | Baixa o CSV de exemplo |
| GET | `/api/importacoes/<id>/clientes` | Clientes de uma carga |
| POST | `/api/importacoes` | Envia a planilha (.csv ou .xlsx) |
| DELETE | `/api/importacoes/<id>` | Desfaz a carga |

---

## Funcionalidades Implementadas

Abaixo estão enumeradas as **10 funcionalidades completas entregues nesta etapa**, funcionando de ponta a ponta (Interface/Frontend → API Flask → Controller → Service → Model/Repository → Banco de Dados):

1. **Autenticação de Usuário (Login):** Validação de credenciais de acesso e emissão de token de sessão seguro (`AuthController` → `LoginService` → `Usuario` / `db.Model`).
2. **Cadastrar Cliente:** Cadastro de pessoas físicas e jurídicas com validação de regras de negócio de CPF/CNPJ e bloqueio de duplicidade no Service (`ClienteController` → `CriarClienteService` → `Cliente` / `db.Model`).
3. **Listar Clientes:** Consulta padronizada de registros de clientes ativos com paginação e filtros (`ClienteController` → `Cliente` / `db.Model.listar_todos`).
4. **Atualizar Cliente:** Edição de dados cadastrais com persistência direta (`ClienteController` → `Cliente` / `db.Model.atualizar`).
5. **Excluir Cliente:** Exclusão lógica (desativação) preservando histórico e integridade referencial (`ClienteController` → `Cliente` / `db.Model.remover`).
6. **Buscar Cliente por Nome:** Busca parcial com contagem agregada de processos via Stored Procedure (`ClienteController` → `ClienteRepository.buscar_por_nome` → `sp_buscar_clientes_por_nome`).
7. **Cadastrar Usuário:** Registro de membros da equipe com geração de hash com sal de senha no Service (`UsuarioController` → `CriarUsuarioService` → `Usuario` / `db.Model`).
8. **Cadastrar Processo:** Abertura de ações judiciais associadas a clientes e advogados (`ProcessoController` → `CriarProcessoService` → `Processo` / `db.Model`).
9. **Listar Processos:** Listagem geral de processos em andamento consumindo a API (`ProcessoController` → `Processo` / `db.Model.listar_todos`).
10. **Painel de Gestão (Dashboard):** Painel analítico de resumo com contagem de status e prazos vencidos via Stored Procedure (`PainelController` → `ProcessoRepository.resumo` → `sp_painel_resumo`).

---

### Funcionalidades Adicionais do Sistema

Além das 10 funcionalidades principais da entrega, o sistema contempla as seguintes capacidades integradas à arquitetura:

| # | Funcionalidade | Descrição / Onde está |
|---|---|---|
| 11 | Busca de Processos Avançada | Filtro multicritério via `ProcessoRepository` e `sp_buscar_processos` |
| 12 | Geração de Diretórios | Criação automática da árvore de pastas do cliente em disco (`utils/gerenciador_arquivos.py`) |
| 13 | Identificação de Categoria de Documento | Classificação jurídica de arquivos anexados (`DocumentoController` → `CategoriaDocumento`) |
| 14 | Renomeação Automática de Arquivos | Padronização dos nomes dos arquivos salvos (`montar_nome_padronizado`) |
| 15 | Checklist Obrigatório de Processo | Montagem automática de exigências documentais e avanço de fase (`CriarProcessoService`) |
| 16 | Mapeamento de Pendências | Identificação de documentos faltantes via `sp_pendencias_checklist` |
| 17 | Configuração de Checklists | Personalização de moldes de exigências por tipo de ação (`GerenciarModeloService`) |
| 18 | Marcadores e Filtros de Prioridade | Classificação por urgência com peso via `sp_processos_prioritarios` |
| 19 | Notificações com Direcionamento | Avisos automáticos direcionados ao advogado responsável (`sp_notificacoes_advogado`) |
| 20 | Importação em Lote e Legado | Carga em massa via CSV/XLSX e possibilidade de reversão (`ImportarClientesService`) |
| 21 | Restrição e Auditoria de Exclusão | Controle de permissão restrito a Admin (Erro 403) e log de auditoria (`ExcluirDocumentoService`) |

---

## Decisões de projeto

**Exclusão lógica em todas as entidades.** Nada é apagado do banco. Cliente e processo têm `ativo`; documento tem `excluido` mais o registro de quem excluiu e quando. Apagar de verdade quebraria as chaves estrangeiras e destruiria o histórico do escritório.

**Senha nunca em texto puro.** O `generate_password_hash` do Werkzeug gera um hash com sal. O campo `senha_hash` não aparece em nenhuma resposta da API.

**Checklist em duas tabelas.** `checklist_modelo` é o molde por tipo de processo; `checklist_processo` é a cópia aplicada. Alterar o molde não altera o checklist de um processo já protocolado.

**Máscaras somente no frontend.** Formatação é assunto de tela. O banco guarda o CPF como `52998224725`, limpo, porque é assim que se compara e se indexa.

**Avanço automático de fase, e só nele.** Quando o último documento obrigatório é anexado, o processo sai de "Aguardando documentos" para "Pronto para protocolo" sozinho, com registro no histórico. A regra é estreita de propósito: o sistema só decide o que ele mesmo consegue verificar. "A documentação está completa" é uma informação que vive inteira no banco; "foi protocolado no fórum" depende do mundo externo e continua sendo entrada manual. O avanço é sempre anunciado na tela — automação silenciosa faz o usuário achar que clicou errado.

**Importação parcial por natureza.** Uma linha ruim não derruba a planilha inteira. Cada erro é registrado com o número da linha, para a secretária corrigir só o que falhou. E a importação reaproveita o `CriarClienteService`: cada linha passa pelas mesmas regras do cadastro manual, senão o legado entraria com qualidade pior que o cadastro novo — que é exatamente o problema que o sistema veio resolver.

**Documento excluído reabre a pendência.** Se o arquivo atendia um item do checklist, o item volta a pendente — senão o processo pareceria completo sem estar.

---

## Terceira Etapa — Stored Procedures

As consultas que extrapolam o CRUD foram movidas para stored procedures do MySQL, chamadas exclusivamente pela camada Repository.

Execute `backend/database/procedures.sql` no MySQL Workbench **depois** do `create_database.sql`.

| Procedure | Funcionalidade | O que faz de complexo |
|---|---|---|
| `sp_buscar_clientes_por_nome` | 01 | `LIKE` + `LEFT JOIN` com contagem de processos |
| `sp_buscar_processos` | 03 | `JOIN` de 5 tabelas, busca em 3 campos, filtros opcionais |
| `sp_painel_resumo` | 06 | Agregação por status, com contagem de prazos vencidos |
| `sp_pendencias_checklist` | 12 | `JOIN` de 6 tabelas + `GROUP_CONCAT` + `HAVING` |
| `sp_processos_prioritarios` | 14 e 15 | `JOIN` N:N com marcadores, ordenação por peso e prazo |
| `sp_notificacoes_advogado` | 16 e 17 | `LEFT JOIN` trazendo o contexto do aviso |

O caminho é sempre o mesmo: **Rota → Controller → Service → Repository → Procedure**. Nenhum Service monta SQL, e nenhuma Model participa dessas consultas.

Rotas da Terceira Etapa:

| Método | Rota | Procedure |
|---|---|---|
| GET | `/api/painel/resumo` | `sp_painel_resumo` |
| GET | `/api/painel/pendencias` | `sp_pendencias_checklist` |
| GET | `/api/painel/prioritarios` | `sp_processos_prioritarios` |
| GET | `/api/painel/marcadores` | — (marcadores fixos) |
| GET | `/api/processos/busca` | `sp_buscar_processos` |
| GET | `/api/clientes/busca` | `sp_buscar_clientes_por_nome` |
| GET | `/api/notificacoes` | `sp_notificacoes_advogado` |
| GET | `/api/processos/<id>/marcadores` | — |
| POST | `/api/processos/<id>/marcadores` | — |
| DELETE | `/api/processos/<id>/marcadores/<id>` | — |

A tela `painel.html` reúne as três consultas principais e indica, em cada bloco, qual procedure o alimenta.

A tela `processos.html` demonstra a regra de decisão da arquitetura num lugar só: sem termo e sem filtro, a listagem é resolvida pela Model (Active Record); com qualquer termo ou filtro, a consulta passa para o Repository e a `sp_buscar_processos`. O rótulo no canto direito da barra de filtros mostra qual dos dois caminhos produziu o resultado na tela.

---

## Como executar

### Pré-requisitos

- Python 3.10 ou superior
- WAMP Server (Apache + MySQL)
- MySQL Workbench

### 1. Criar o banco

Abra `backend/database/create_database.sql` no MySQL Workbench e execute o script inteiro. O banco `tabflower` é criado com as 16 tabelas e a carga inicial (perfis, status, tipos de processo, categorias e checklists).

Em seguida execute `backend/database/procedures.sql`, que cria as 6 stored procedures da Terceira Etapa. Confira em SCHEMAS > tabflower > Stored Procedures.

### 2. Instalar as dependências

Na pasta `backend/`:

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar a conexão

```
copy .env.example .env
```

No WAMP, o usuário root normalmente não tem senha, então `DB_PASSWORD=` fica vazio. O `.env` está no `.gitignore` e não deve ir para o GitHub.

**Gere a sua própria `SECRET_KEY`.** Ela é a chave que assina os tokens de sessão. Se ficar no valor de exemplo (`troque-esta-chave`), qualquer pessoa que veja o código no GitHub consegue forjar um token de Administrador e entrar no sistema sem senha. Com o venv ativado:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado para a linha `SECRET_KEY=` do `.env`. Trocar a chave depois invalida os tokens já emitidos — quem estiver logado simplesmente entra de novo.

### 4. Subir a API

```
python run.py
```

A API responde em `http://localhost:5000`. Confira em `http://localhost:5000/api/status`.

### 5. Criar o primeiro usuário

O sistema exige login, então é preciso criar um usuário antes do primeiro acesso. Na pasta `backend/`, com a API parada e o WAMP ligado:

```
python criar_primeiro_usuario.py
```

O script pergunta nome, e-mail, perfil e senha. **Escolha o perfil Admin no primeiro usuário**, porque é o único que pode excluir registros e cadastrar outros usuários pela tela.

Se você rodar o script com um e-mail que já existe (como os advogados inseridos por SQL durante os testes, que ficaram com `senha_hash = 'TEMPORARIO'`), ele oferece redefinir a senha em vez de dar erro.

### 6. Abrir o sistema

Com o VS Code, clique com o botão direito em `frontend/login.html` e escolha **Show Preview** (Live Preview) ou **Open with Live Server**.

O CORS do backend está liberado para `http://127.0.0.1:3000` e `http://localhost:3000`, as portas do Live Preview. Se você usar o Live Server (porta 5500) ou outra ferramenta, acrescente a porta na lista em `backend/app.py`, senão o navegador bloqueia as chamadas à API.

---

## Roteiro de teste

1. **Cadastrar um cliente.** Tente um CPF inválido: a API recusa. Tente o mesmo CPF duas vezes: bloqueio de duplicidade. Confira que a pasta apareceu em `backend/arquivos/`.
2. **Cadastrar um usuário** com perfil Advogado.
3. **Abrir um processo** do tipo Trabalhista. Na tela de detalhe, o checklist já vem com quatro itens pendentes.
4. **Mudar a situação** do processo. O histórico registra a mudança com data e hora.
5. **Anexar um documento** da categoria Procuração. O arquivo é renomeado, o item do checklist vira verde e uma notificação é criada para o advogado (`SELECT * FROM notificacao;`).
6. **Excluir o documento.** A pendência do checklist volta a aparecer e o registro continua no banco com `excluido = 1`.
7. **Aplicar um marcador** de prioridade ao processo, na tela de detalhe.
8. **Abrir o painel.** O resumo por situação, a lista de prioridades e a de pendências devem refletir tudo que foi cadastrado — e cada bloco indica qual procedure o alimenta.

---

---

## Login e permissões

### Por que existe

Antes de existir login, o frontend informava quem estava operando (`usuario_id = 1`, fixo no JavaScript) e o backend acreditava. Isso tornava a Funcionalidade 20 — *bloquear a exclusão definitiva por usuários comuns* — apenas decorativa: bastava abrir o F12 do navegador e trocar esse número para virar Administrador.

O login resolve exatamente esse ponto: o backend passa a descobrir sozinho quem está falando, em vez de perguntar ao frontend.

### Como funciona, em uma frase

No login o servidor devolve um **crachá assinado** (o token). O navegador guarda esse crachá e o apresenta em toda requisição. O servidor confere a assinatura: se alguém falsificar ou editar o crachá, a assinatura não bate e o acesso é negado.

### O caminho completo

1. A pessoa digita e-mail e senha em `login.html`.
2. `LoginService` compara a senha com o hash guardado no banco (`werkzeug.check_password_hash`). Se o e-mail não existe, se a senha está errada ou se o usuário está inativo, a mensagem devolvida é sempre a mesma — *"E-mail ou senha inválidos"* —, para que o formulário não vire uma ferramenta de descobrir quais e-mails estão cadastrados.
3. Dando certo, `utils/token.py` gera um token assinado com a `SECRET_KEY` da aplicação, contendo apenas o id do usuário e o horário de emissão.
4. O `api.js` guarda o token no `localStorage` do navegador e passa a enviá-lo no cabeçalho `Authorization: Bearer <token>` em toda chamada.
5. No backend, `utils/autenticacao.py` roda **antes de qualquer Controller**, valida o token, carrega o usuário do banco e o disponibiliza em `flask.g.usuario_atual`.
6. Os Controllers leem `g.usuario_atual` em vez de qualquer campo vindo da requisição.

### As duas camadas de permissão

| Camada | Onde | O que faz |
|---|---|---|
| **Autenticação** | `utils/autenticacao.py` | Confere *se* a pessoa está logada. Sem token válido → `401`. |
| **Autorização** | Services de exclusão | Confere *o que* ela pode fazer, via `perfil.pode_excluir`. Sem permissão → `403`. |

A autorização continua saindo do banco, pelo id do perfil, exatamente como foi modelado na Primeira Etapa. O token não substitui isso — ele só garante que o `perfil_id` consultado é o da pessoa que realmente digitou a senha.

### Quem pode o quê

**Exclusões** (documento, cliente, processo, usuário e desfazer importação): somente perfis com `pode_excluir = TRUE`, hoje só o Admin. Cadastrar e editar clientes, processos e documentos continua liberado para qualquer pessoa logada — bloquear isso tornaria o sistema inútil para a secretária, que é quem mais o usa.

**O módulo de usuários é a exceção**, porque é por ele que se ganha poder no sistema:

| Rota | Quem pode |
|---|---|
| `GET` de usuários, perfis e advogados | Qualquer usuário logado |
| `POST /api/usuarios` | Somente Admin |
| `PUT /api/usuarios/<id>` | Somente Admin |
| `PATCH /api/usuarios/<id>/senha` | Admin, **ou** a própria pessoa trocando a senha dela |
| `DELETE /api/usuarios/<id>` | Somente Admin, e ninguém desativa a própria conta |

O motivo de as três primeiras serem restritas é o campo `perfil_id`. Sem essa trava, qualquer pessoa faria um `PUT` no próprio id mandando `perfil_id = 1` e viraria Administrador; ou trocaria a senha do Admin e entraria com a conta dele. A trava de exclusão continuaria correta e mesmo assim a Funcionalidade 20 seria contornada — bastava se promover antes.

As leituras ficaram liberadas de propósito: a tela de formulário precisa listar os perfis, e saber o nome dos colegas de escritório não é informação sensível neste sistema.

**Os botões continuam aparecendo para todos.** Quem não pode clica, e o backend responde `403` com uma frase explicando a regra. Um botão que some não ensina nada; *"o perfil Secretária não tem permissão para excluir documentos"* ensina.

### Escolhas de projeto e o porquê

**Token em vez de sessão de cookie.** O frontend roda no Live Preview (porta 3000) e a API no Flask (porta 5000) — origens diferentes. Cookie entre origens distintas exige `supports_credentials` no CORS, `credentials: 'include'` em toda chamada e ainda esbarra no bloqueio de cookies de terceiros do navegador. Quando falha, falha em silêncio: o usuário "desloga sozinho" sem mensagem de erro. O token no cabeçalho não tem nenhum desses problemas.

**`itsdangerous` em vez de JWT.** A biblioteca já vem instalada junto com o Flask, então o `requirements.txt` não mudou. Ela resolve o mesmo problema (assinar e verificar dados) com menos peça nova para a equipe manter.

**Proteção registrada uma vez, no `routes.py`.** Em vez de repetir uma checagem em cada Controller, o `before_request` é aplicado aos Blueprints em um único lugar. Assim nenhuma rota nova corre o risco de esquecer a proteção — o padrão é ser protegida, e ficar público é que exige ação explícita.

**Sessão de 8 horas.** Um turno de trabalho no escritório. Depois disso o token vence sozinho e a pessoa loga de novo.

**Download por JavaScript.** O navegador não envia o cabeçalho `Authorization` em um `<a href>` clicado, então os links de baixar documento e de baixar o modelo de importação passaram a buscar o arquivo por `fetch` (com o token) e disparar o download a partir do resultado.

### Limites desta implementação

Honestamente: isto é um login funcional e suficiente para o escopo do TCC, não um sistema de produção. O que ficou de fora, de propósito:

- Não há logout no servidor (revogação de token). Sair apaga o token do navegador; o token em si continua valendo até vencer.
- Não há bloqueio após várias tentativas de senha erradas.
- O `localStorage` é acessível por JavaScript da própria página. Num sistema real isso seria mitigado com cookie `HttpOnly`, que aqui traria os problemas de origem cruzada descritos acima.
- As checagens de permissão cobrem as exclusões e o módulo de usuários. Leitura, cadastro e edição de clientes, processos e documentos ficam liberados para qualquer pessoa logada — e isso é intencional, não esquecimento: é o trabalho do dia a dia da secretária.

## Limitações conhecidas

**O login é simples, de propósito.** Sem revogação de token no servidor, sem bloqueio por tentativas e sem recuperação de senha por e-mail. Os limites estão detalhados na seção *Login e permissões*.

**A validação de CPF/CNPJ confere os dígitos verificadores, não a existência.** Confirmar que o documento existe exigiria consulta à Receita Federal, fora do escopo.

**O upload é validado por extensão e tamanho, não pelo conteúdo do arquivo.** Alguém pode renomear um arquivo qualquer para `.pdf` e enviá-lo. Conferir os primeiros bytes do arquivo resolveria, e foi descartado por decisão da equipe: o sistema roda numa rede interna de escritório, entre pessoas conhecidas.

**Erros inesperados aparecem no `backend/tabflower.log`.** A tela mostra sempre uma frase genérica, porque a mensagem original de uma exceção pode conter nome de tabela ou trecho de SQL. Se algo der errado numa demonstração, o motivo real está nesse arquivo.

**A tabela `log_auditoria` registra exclusões, restaurações e logins.** Cadastros e edições comuns não são registrados — a tabela prevê as ações `CRIAR` e `ATUALIZAR`, e elas ficaram para depois.
