# TabFlower

Sistema de gestão documental e processual para escritórios de advocacia.

Projeto de Conclusão de Curso do Colégio COTEMIG
Disciplina: Projeto de Software (Prof. Gleison Brito)

**Equipe:** Gabriel Mazzega, Gabriel Almeida, Gabriel Fernandes, Vitor Papini, Nnamdi Delfino

---

## O problema

A parte administrativa de um escritório de advocacia perde um tempo absurdo com tarefa manual: criar pasta para cada cliente, renomear PDF escaneado um por um, conferir checklist no papel e ainda manter planilha paralela que nunca bate com a realidade. Resultado: demora para achar arquivo, risco de sumir documento e ninguém sabe dizer quem mexeu em quê quando algo dá errado.

O TabFlower junta cliente, processo e documento num só lugar, cria a pasta do cliente automaticamente, padroniza o nome dos arquivos, troca o checklist de papel por um digital e guarda quem fez cada ação.

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

- `Cliente.salvar()`: CRUD puro, resolvido pela Model via Active Record.
- `ClienteRepository.buscar_por_nome()`: usa `LIKE` com filtro parcial, então mora no Repository.
- `CriarProcessoService` orquestra: valida vínculos, chama a Model para salvar, monta o checklist a partir do molde e grava o histórico. Nenhuma dessas decisões cabe na Model nem no Controller.

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

**Todas as rotas exigem login**, exceto `/api/status` e `/api/auth/login`. As demais só respondem se a requisição trouxer o cabeçalho `Authorization: Bearer <token>` com um token válido. Sem ele, a resposta é `401`.

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
3. **Listar Clientes:** Listagem dos clientes ativos em ordem alfabética, com filtro para incluir também os inativos (`ClienteController` → `Cliente` / `db.Model.listar_todos`).
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

**Exclusão lógica em tudo.** Não apagamos nada do banco de verdade. Cliente e processo ganharam um campo `ativo`; documento tem `excluido`, mais quem excluiu e quando. Apagar de verdade quebraria as chaves estrangeiras e perderia o histórico do escritório.

Duas escolhas sobre o que vai gravado no banco. A senha passa pelo `generate_password_hash` do Werkzeug, que já gera com sal, e o `senha_hash` nunca aparece em resposta da API. O CPF vai no sentido contrário: fica salvo limpo, só número (`52998224725`), porque assim é mais fácil comparar e indexar. Formatar bonito é problema de tela.

O checklist ficou em duas tabelas. `checklist_modelo` é o molde por tipo de processo; `checklist_processo` é a cópia que de fato é usada num processo. Assim, mexer no molde depois não bagunça o checklist de um processo que já estava rodando.

**Avanço automático de fase, mas só quando dá para ter certeza.** Quando o último documento obrigatório é anexado, o processo passa sozinho de "Aguardando documentos" para "Pronto para protocolo", com registro no histórico. Limitamos isso de propósito: o sistema só decide sozinho o que ele mesmo consegue confirmar no banco. Se já foi protocolado no fórum ou não, isso depende do mundo lá fora e continua sendo entrada manual. E o avanço automático sempre avisa na tela, senão a pessoa acha que clicou em algo errado.

**Importação não trava tudo por causa de uma linha ruim.** Cada erro fica registrado com o número da linha, para a secretária corrigir só o que deu problema. E a importação usa o mesmo `CriarClienteService` do cadastro manual, senão o cliente que veio de planilha entraria com qualidade pior que o cadastro normal, que é exatamente o problema que a gente queria resolver.

**Excluir documento reabre a pendência do checklist.** Se aquele arquivo cobria um item do checklist e some, o item volta a aparecer como pendente. Senão o processo ia parecer completo sem estar.

---

## Terceira Etapa: Stored Procedures

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
| GET | `/api/painel/marcadores` | não usa (marcadores fixos) |
| GET | `/api/processos/busca` | `sp_buscar_processos` |
| GET | `/api/clientes/busca` | `sp_buscar_clientes_por_nome` |
| GET | `/api/notificacoes` | `sp_notificacoes_advogado` |
| GET | `/api/processos/<id>/marcadores` | não usa |
| POST | `/api/processos/<id>/marcadores` | não usa |
| DELETE | `/api/processos/<id>/marcadores/<id>` | não usa |

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

Copie o resultado para a linha `SECRET_KEY=` do `.env`. Trocar a chave depois invalida os tokens já emitidos, e quem estiver logado simplesmente entra de novo.

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
8. **Abrir o painel.** O resumo por situação, a lista de prioridades e a de pendências devem refletir tudo que foi cadastrado, e cada bloco indica qual procedure o alimenta.

---

---

## Login e permissões

### Por que existe

Antes do login, o frontend simplesmente informava quem estava operando (`usuario_id = 1`, fixo no JavaScript) e o backend acreditava. Isso fazia da Funcionalidade 20, que bloqueia a exclusão definitiva por usuário comum, algo decorativo: bastava abrir o F12 e trocar esse número para virar Administrador.

O login resolve isso: o backend passa a descobrir sozinho quem está falando, sem perguntar para o frontend.

### Como funciona, resumindo

No login o servidor devolve um token assinado. O navegador guarda esse token e manda ele em toda requisição. O servidor confere a assinatura: se alguém tentar editar ou forjar o token, a assinatura não bate e é barrado.

### O caminho completo

1. A pessoa digita e-mail e senha em `login.html`.
2. `LoginService` compara a senha com o hash do banco (`werkzeug.check_password_hash`). Se o e-mail não existe, a senha está errada ou o usuário está inativo, a mensagem devolvida é sempre a mesma, "E-mail ou senha inválidos", para não dar pista de quais e-mails existem no sistema.
3. Dando certo, `utils/token.py` gera um token assinado com a `SECRET_KEY`, guardando só o id do usuário e o horário.
4. `api.js` guarda o token no `localStorage` e manda ele no cabeçalho `Authorization: Bearer <token>` em toda chamada.
5. No backend, `utils/autenticacao.py` roda antes de qualquer Controller, confere o token, busca o usuário no banco e deixa disponível em `flask.g.usuario_atual`.
6. Os Controllers usam esse `g.usuario_atual`, nunca um campo vindo direto da requisição.

### As duas camadas de permissão

| Camada | Onde | O que faz |
|---|---|---|
| **Autenticação** | `utils/autenticacao.py` | Confere se a pessoa está logada. Sem token válido, `401`. |
| **Autorização** | Services de exclusão | Confere o que ela pode fazer, olhando `perfil.pode_excluir`. Sem permissão, `403`. |

A autorização continua vindo do banco, pelo id do perfil, do jeito que já foi modelado desde a Primeira Etapa. O token não muda isso, só garante que o `perfil_id` consultado é mesmo da pessoa que digitou a senha.

### Quem pode o quê

Só perfil com `pode_excluir = TRUE` (hoje, só o Admin) pode excluir documento, cliente, processo, usuário ou desfazer importação. Cadastrar e editar continua liberado para qualquer um logado, porque travar isso ia inutilizar o sistema para a secretária, que é quem mais usa no dia a dia.

O módulo de usuários é diferente, porque é por ali que dá para ganhar poder no sistema:

| Rota | Quem pode |
|---|---|
| `GET` de usuários, perfis e advogados | Qualquer usuário logado |
| `POST /api/usuarios` | Só Admin |
| `PUT /api/usuarios/<id>` | Só Admin |
| `PATCH /api/usuarios/<id>/senha` | Admin, ou a própria pessoa trocando a senha dela |
| `DELETE /api/usuarios/<id>` | Só Admin, e ninguém desativa a própria conta |

As três primeiras rotas são restritas por causa do campo `perfil_id`: sem essa trava, qualquer um faria um `PUT` no próprio id mandando `perfil_id = 1` e virava Admin, ou trocava a senha do Admin e entrava com a conta dele. Só a trava de exclusão não seria suficiente: dava para se promover antes.

As leituras ficaram liberadas de propósito: a tela de formulário precisa listar os perfis, e saber o nome dos colegas de escritório não é informação sensível aqui.

Os botões continuam aparecendo para todo mundo. Quem não pode, clica e o backend devolve `403` com uma frase explicando a regra, que é melhor do que o botão simplesmente sumir sem dizer por quê.

### Escolhas de projeto

**Token em vez de cookie de sessão.** O frontend roda no Live Preview (porta 3000) e a API no Flask (porta 5000), origens diferentes. Cookie entre origens diferentes dá dor de cabeça: `supports_credentials` no CORS, `credentials: 'include'` em toda chamada, e ainda esbarra no bloqueio de cookie de terceiro do navegador. Quando falha, falha calado: o usuário "desloga sozinho" sem aviso. Token no header não tem esses problemas.

**`itsdangerous` em vez de JWT.** Já vem instalado junto com o Flask, então nem mexeu no `requirements.txt`. Resolve o mesmo problema (assinar e conferir dado) sem adicionar mais uma lib para manter.

**Proteção registrada uma vez só, no `routes.py`.** Em vez de repetir a checagem em cada Controller, o `before_request` fica nos Blueprints, num lugar só. Assim rota nova já nasce protegida por padrão.

**Sessão de 8 horas**, um turno de trabalho no escritório. Depois disso o token vence e a pessoa loga de novo.

**Download feito por JavaScript**, porque um `<a href>` normal não manda o cabeçalho `Authorization`. Os links de baixar documento e de baixar o modelo de importação usam `fetch` (com o token) e disparam o download a partir do resultado.

### O que ficou de fora

Esse login é suficiente para o escopo do TCC, não é sistema de produção. Ficou faltando, de propósito:

- Logout no servidor (revogar token). Sair só apaga o token do navegador; ele continua valendo até vencer.
- Bloqueio depois de várias tentativas de senha erradas.
- `localStorage` é acessível por JavaScript da própria página. Num sistema real usaria cookie `HttpOnly`, mas aí voltam os problemas de origem cruzada citados acima.
- Leitura, cadastro e edição de clientes, processos e documentos ficam liberados para qualquer um logado. Isso é proposital, não esquecimento: é o trabalho do dia a dia da secretária.

## Limitações conhecidas

**Login simples, de propósito.** Sem revogar token no servidor, sem bloqueio por tentativas e sem recuperação de senha por e-mail. Detalhes na seção *Login e permissões*.

**Validação de CPF/CNPJ confere só os dígitos verificadores, não se o documento existe de verdade.** Isso exigiria consulta à Receita Federal, fora do escopo do projeto.

**Upload é validado por extensão e tamanho, não pelo conteúdo do arquivo.** Dá para renomear qualquer coisa para `.pdf` e enviar. A equipe decidiu não conferir os bytes do arquivo porque o sistema roda numa rede interna, entre pessoas conhecidas.

**Erro inesperado vai para o log (`backend/tabflower.log`).** Na tela aparece sempre uma frase genérica, porque o erro original pode conter nome de tabela ou trecho de SQL. Se algo der errado numa demonstração, o motivo real está nesse arquivo.

**`log_auditoria` registra só exclusões, restaurações e logins.** Cadastro e edição comuns não entram ali, está previsto (`CRIAR`, `ATUALIZAR`), mas ficou para depois.
