# TabFlower

Sistema de gestão de clientes, processos e documentos para escritório de advocacia.

Projeto de Conclusão de Curso — Colégio COTEMIG
Disciplina: Projeto de Software — Prof. Gleison Brito

**Equipe:** Gabriel Mazzega, Gabriel Almeida, Gabriel Fernandes, Vitor Papini, Nnamdi Delfino

---

## O problema que a gente foi resolver

A gente entrevistou pessoas que trabalham na parte administrativa de escritório de advocacia e o que mais apareceu foi tempo perdido com coisa manual. Criar pasta para cada cliente novo. Renomear PDF escaneado um por um. Conferir checklist impresso para ver se falta algum documento. Manter planilha paralela que sempre fica desatualizada.

O pior de tudo era a parte de rastreabilidade. Quando um arquivo sumia, ninguém sabia dizer quem tinha mexido nele.

Então o TabFlower faz quatro coisas principais:

- guarda cliente, processo e documento num lugar só
- cria a pasta do cliente e renomeia o arquivo sozinho, num padrão
- troca o checklist de papel por um digital que se atualiza sozinho
- registra quem fez o quê

---

## Tecnologias

| Camada | O que usamos |
|---|---|
| Backend | Python 3 com Flask |
| Acesso ao banco | SQLAlchemy |
| Banco | MySQL 8 (pelo WAMP) |
| Frontend | HTML, CSS e JavaScript puro |

## Como o sistema é organizado

Toda ação do sistema segue o mesmo caminho, sempre nesta ordem:

```
tela  ->  rota  ->  controller  ->  service  ->  model  ->  banco
```

O que cada parada faz:

- **rota** (`routes.py`) só diz qual endereço chama qual função. Não tem regra nenhuma aqui.
- **controller** pega o que veio da requisição e devolve a resposta em JSON. É o tradutor entre o mundo HTTP e o resto.
- **service** é onde mora a regra de negócio de verdade. Conferir CPF, bloquear duplicidade, checar permissão, criar pasta.
- **model** é a tabela do banco virada classe Python. Cliente, Processo, Documento.
- **repository** aparece só quando a consulta é complicada demais para o ORM. É de lá que a gente chama as stored procedures.

A vantagem dessa organização é que se você entende uma ação inteira, entende todas as outras, porque o caminho é sempre igual.

### Estrutura das pastas

```
backend/
  routes.py          enderecos da API
  app.py             montagem da aplicacao
  run.py             sobe o servidor
  controllers/       recebe requisicao, devolve JSON
  services/          regras de negocio
  models/            tabelas
  repositories/      consultas complexas e procedures
  utils/             validador de CPF, token, nome de arquivo
  database/          scripts SQL
  arquivos/          onde os documentos ficam guardados
frontend/
  *.html             as telas
  js/api.js          conversa com a API
  js/*.js            um arquivo por tela
  css/estilo.css
```

---

## Como rodar

### Antes de começar

- Python 3.10 ou mais novo
- WAMP Server ligado (precisa do MySQL)
- MySQL Workbench

### 1. Criar o banco

No MySQL Workbench, abra `backend/database/create_database.sql` e execute o script inteiro. Ele cria o banco `tabflower` com as 16 tabelas e já preenche as tabelas de apoio: perfis, status, tipos de processo, categorias de documento e os checklists modelo.

Depois execute `backend/database/procedures.sql`, que cria as 6 stored procedures.

Para conferir se deu certo:

```sql
SELECT * FROM status_processo;
```

Se vier vazio, o script parou no meio e precisa rodar de novo.

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

No WAMP o usuário root costuma não ter senha, então `DB_PASSWORD=` fica vazio mesmo.

**Gere a sua própria SECRET_KEY.** Ela é a chave que assina os tokens de login. Se deixar o valor de exemplo, qualquer pessoa que veja o código no GitHub consegue fabricar um token de Administrador e entrar sem senha.

Com o venv ativado:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

Cole o resultado na linha `SECRET_KEY=` do `.env`. O `.env` está no `.gitignore` e não vai para o GitHub.

### 4. Subir a API

```
python run.py
```

A API responde em `http://localhost:5000`. Para conferir, abra `http://localhost:5000/api/status` no navegador.

### 5. Criar o primeiro usuário

O sistema exige login, então não dá para entrar antes de existir alguém cadastrado. Com o WAMP ligado, na pasta `backend/`:

```
python criar_primeiro_usuario.py
```

Ele pergunta nome, e-mail, perfil e senha. **Escolha Admin no primeiro**, porque só o Admin cadastra outros usuários pela tela.

### 6. Abrir o sistema

No VS Code, clique com o botão direito em `frontend/login.html` e escolha **Show Preview**.

⚠️ **Atenção na porta.** O backend só aceita chamadas vindas de `localhost:3000` e `127.0.0.1:3000`, que são as portas do Live Preview. Se você abrir com Live Server, que usa a porta 5500, o navegador bloqueia tudo e parece que o sistema quebrou. Nesse caso é só acrescentar a porta na lista dentro de `backend/app.py`.

---

## O que o sistema faz

As 20 funcionalidades que a gente combinou com o professor:

**Busca e cadastro**
1. Busca de cliente por nome
2. Busca por CPF ou CNPJ
3. Busca por número de processo
4. Validação de CPF e CNPJ pelos dígitos verificadores
5. Bloqueio de cliente duplicado

**Processos**
6. Painel central com os processos e o que está pendente
7. Atualização de fase do processo, com histórico

**Documentos**
8. Criação automática da pasta do cliente
9. Identificação da categoria do documento
10. Renomeação automática num padrão
11. Checklist de documentos obrigatórios por tipo de processo
12. Mapa das pendências

**Organização**
13. Configuração de quais documentos cada tipo de processo exige
14. Marcadores visuais (Urgente, Prioridade, Prazo curto)
15. Filtro por prioridade

**Avisos**
16. Notificação quando documento é anexado
17. Aviso direcionado ao advogado responsável

**Legado**
18. Importação de clientes por planilha CSV ou XLSX
19. Organização dos dados antigos do escritório

**Controle**
20. Só o Administrador pode excluir

---

## Decisões que a gente tomou e por quê

Essa parte é a que mais deu discussão no grupo.

**Nada é apagado de verdade.** Cliente e processo têm um campo `ativo`, documento tem `excluido`. Quando alguém "exclui", o registro continua no banco, só some da tela. A gente fez assim porque processo aponta para advogado, documento aponta para processo, e o log de auditoria aponta para quem agiu. Apagar de verdade quebraria essas ligações e destruiria justamente o histórico que o escritório queria ter.

**Senha nunca fica em texto puro.** A gente usa o `generate_password_hash` do Werkzeug, que gera um hash com sal. O campo `senha_hash` não aparece em nenhuma resposta da API.

**Checklist em duas tabelas.** `checklist_modelo` é o molde de cada tipo de processo. `checklist_processo` é a cópia que fica presa naquele processo específico. Isso serve para que mudar o molde hoje não altere um processo que já foi protocolado mês passado.

**Máscara só na tela.** O CPF fica no banco como `52998224725`, sem ponto nem traço. Formatação é assunto de interface, e guardar limpo facilita comparar e indexar.

**O processo avança de fase sozinho, mas só numa situação.** Quando o último documento obrigatório é anexado, o processo sai de "Aguardando documentos" e vai para "Pronto para protocolo" automaticamente. A gente deixou essa regra bem estreita de propósito: o sistema só decide o que ele mesmo consegue conferir. Saber que a documentação está completa é informação que está inteira no banco. Saber que foi protocolado no fórum depende do mundo lá fora, então continua sendo o usuário quem marca. E o avanço sempre aparece na tela, porque automação silenciosa faz a pessoa achar que clicou errado.

**Importação não é tudo ou nada.** Se uma linha da planilha estiver ruim, ela é reportada com o número da linha e o resto entra normal. E cada linha passa pelo mesmo `CriarClienteService` do cadastro manual. Se a gente tivesse feito um caminho separado só para importação, o dado antigo entraria com qualidade pior que o dado novo, que é exatamente o problema que o sistema veio resolver.

**Excluir documento reabre a pendência.** Se aquele arquivo estava fechando um item do checklist, o item volta a pendente. Senão o processo pareceria completo sem estar.

---

## Como o login funciona

Explicado do jeito que a gente entendeu:

Quando você acerta e-mail e senha, o servidor te devolve um crachá assinado com a chave secreta da aplicação. O navegador guarda esse crachá e apresenta ele em toda requisição seguinte. O servidor confere a assinatura antes de responder qualquer coisa.

Se alguém editar o crachá, a assinatura não bate mais e o acesso é negado. O crachá vale 8 horas.

Existem duas camadas de permissão, e elas fazem coisas diferentes:

- a primeira pergunta **quem é você** (o crachá é válido?)
- a segunda pergunta **o que você pode** (o seu perfil tem `pode_excluir`?)

Por isso 401 e 403 são erros diferentes. 401 é "não sei quem você é". 403 é "sei quem você é, e você não pode isso".

### Quem pode o quê

No dia a dia, todo mundo logado pode a mesma coisa: ver, buscar, cadastrar e editar cliente, processo e documento.

A diferença aparece só em duas situações, e as duas são exclusivas do Admin:

- **excluir** qualquer coisa
- **mexer em usuário** — cadastrar gente nova ou mudar o perfil de alguém

Advogado e Secretária têm exatamente as mesmas permissões entre si.

---

---

## Testes

O projeto tem um roteiro de teste manual com 88 verificações, dividido em 13 blocos: ambiente, autenticação, clientes, processos, documentos, permissões, tentativa de escalada de privilégio, auditoria, importação, checklists, painel, notificações e limpeza.

Parte dos testes é feita pela tela e parte por `curl`, para conferir que a regra vale na API e não só no botão. Testar a permissão só pela tela não provaria nada, porque esconder o botão não impede ninguém de chamar o endereço direto.

