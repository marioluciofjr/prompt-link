# prompt-link

![license - MIT](https://img.shields.io/badge/license-MIT-green)
![site - prazocerto.me](https://img.shields.io/badge/site-prazocerto.me-230023)
![linkedin - @marioluciofjr](https://img.shields.io/badge/linkedin-marioluciofjr-blue)

## Índice

* [Introdução](#introdução)
* [Estrutura do projeto](#estrutura-do-projeto)
* [Requisitos](#requisitos)
* [Como instalar no Claude Cowork](#como-instalar-no-claude-cowork)
* [Como instalar no Claude Code](#como-instalar-no-claude-code)
* [Exemplos de uso](#exemplos-de-uso)
* [Links úteis](#links-úteis)
* [Contribuições](#contribuições)
* [Licença](#licença)
* [Contato](#contato)

## Introdução
O plugin prompt-link transforma qualquer texto em um link de prompt pronto. O link abre o Claude, o ChatGPT, o Perplexity ou o Grok com o texto já preenchido. O plugin codifica o texto, confere o limite de tamanho, encurta pelo zip1.io, testa o link e entrega o endereço aprovado.

## Estrutura do projeto
Quem recebe um prompt em texto precisa copiar e colar. Um link de prompt elimina esses dois passos.

O plugin resolve três problemas dessa conversão:

1. A codificação quebra com acento, emoji e quebra de linha. O plugin aplica a norma RFC 3986 byte a byte.
2. O encurtador recusa URLs muito longas. O plugin mede a URL antes de enviar.
3. Um link malformado leva a pessoa a uma conversa vazia. O plugin confere no zip1.io para onde o link curto leva antes de entregar, sem abrir o link.

### Destinos suportados

| Destino | Chave | Base da URL |
|---------|-------|-------------|
| Claude | `claude` | `https://claude.ai/new?q=` |
| ChatGPT | `chatgpt` | `https://chatgpt.com/?q=` |
| Perplexity | `perplexity` | `https://perplexity.ai/search/new?q=` |
| Grok | `grok` | `https://grok.com/?q=` |

O plugin não tem destino padrão. Se você não informar o destino, o Claude pergunta antes de codificar.

### Formato da entrega

A entrega final mostra dois endereços:

| Endereço | Para que serve |
|----------|----------------|
| Link curto | Abre o LLM com o prompt preenchido |
| Link de estatísticas | Mostra cliques totais e únicos do link curto. O zip1.io gera um link de estatísticas para cada link curto |

A URL longa fica fora da entrega. Ela já existe dentro do link curto e atrapalha a leitura.

Dois casos abrem exceção:

1. O zip1.io devolve erro ou não responde. O plugin entrega a URL longa e informa o código e o significado do erro. Exemplo: o erro `429` indica o limite de 10 links por minuto por IP.
2. Você pede o link completo. O plugin entrega os dois endereços.

### Limite de tamanho

O limite é de **7.500 caracteres de URL**. A contagem soma a base do destino e a query codificada.

Acima desse limite, o fluxo para na etapa 1 e devolve esta mensagem:

```
Não foi possível encurtar o link, pois o prompt tem mais de 7500 caracteres
```

O percent-encoding infla o texto. Um `á` ocupa 6 caracteres. Uma quebra de linha ocupa 3. O fator de expansão em português fica entre 1,4 e 2,0.

Na prática, o teto de texto fica entre 3.700 e 5.300 caracteres. O script informa o fator medido e o teto estimado a cada execução.

### Regra de codificação

O plugin aplica a norma RFC 3986 de forma estrita. Passam como literais apenas `A-Z`, `a-z`, `0-9`, `-`, `.`, `_` e `~`.

Todo o resto vira `%XX`. O `XX` é o valor da coluna Hex da tabela ASCII, em maiúsculas. O espaço vira `%20`, nunca `+`.

O plugin codifica caracteres fora do ASCII em UTF-8, byte a byte. O `ç` vira `%C3%A7`.

A skill traz três referências e um modelo:

- `references/tabela-ascii.md` — os 128 valores Hex com o percent-encoding correspondente
- `references/regras-encoding.md` — ordem de operações, caracteres críticos, UTF-8, bases por destino, limites e verificação de round-trip
- `references/erros-zip1.md` — códigos de erro do zip1.io e o significado de cada um
- `assets/formato-entrega.md` — modelo único da entrega final e das exceções

### Componentes

| Tipo | Nome | Função |
|------|------|--------|
| Skill | `prompt-link` | Regras de codificação, bases por destino e a ligação entre as três etapas |
| Agente | `analisador` | Confere prompt, destino e limite de 7.500 caracteres e devolve as pendências com o feedback |
| Agente | `montador` | Monta a URL longa codificada e confere o round-trip |
| Agente | `encurtador` | Encurta pelo zip1.io, confere no zip1.io o destino do link curto e faz a entrega final |
| Conector | `zip1` | Servidor MCP do encurtador zip1.io (`https://zip1.io/mcp`) |

### Arquitetura do script

O script é orientado a objetos, com alta coesão e baixo acoplamento. Cada classe tem uma responsabilidade e recebe suas dependências no construtor.

| Camada | Classe | Responsabilidade |
|--------|--------|------------------|
| Domínio | `Destino` | Formato de URL de um LLM |
| Domínio | `CatalogoDeDestinos` | Resolve chaves e identifica destino por URL |
| Texto | `NormalizadorDePrompt` | Padroniza quebras e espaços |
| Texto | `CodificadorRFC3986` | Percent-encoding e decodificação |
| Domínio | `Link` | Resultado imutável da montagem |
| Domínio | `ConstrutorDeLink` | Compõe normalizador, codificador e destino |
| Domínio | `AuditorDeTamanho` e `LaudoDeTamanho` | Aplica os limites de URL |
| Domínio | `AnalisadorDeEntrada`, `AnaliseDeEntrada` e `Pendencia` | Confere prompt, destino e limite e junta as pendências |
| Domínio | `LeitorDeLink` e `LinkLido` | Decompõe uma URL existente |
| Domínio | `ConferidorDeLink` e `Conferencia` | Compara um link com o prompt original |
| Aplicação | `ServicoDeLink` | Orquestra os casos de uso |
| Interface | `LeitorDeTexto` | Lê o prompt de arquivo, argumento ou stdin, em UTF-8 |
| Interface | `InterfaceLinhaDeComando` | Traduz argumentos em chamadas ao serviço, sem regra de negócio |

`Normalizador` e `Codificador` são protocolos. Trocar a estratégia de codificação não exige alterar o construtor nem o serviço. Todo script Python deste plugin segue esse padrão.

### Configuração

O arquivo `.mcp.json` declara o conector `zip1` como servidor MCP por HTTP. O conector não exige variáveis de ambiente. O agente `encurtador` usa o zip1 com qualquer um dos dois nomes: o conector vinculado à conta no Cowork ou o servidor do plugin no Claude Code.

O agente `analisador` grava o prompt em `${CLAUDE_PLUGIN_DATA}/prompt.txt`, a pasta de dados do plugin. Os três agentes leem esse arquivo, e o texto não é recopiado entre as etapas.

O plugin não abre o link curto para testar. O zip1.io conta cada acesso como clique, então a conferência usa a consulta de estatísticas do conector. O link chega à pessoa com as estatísticas zeradas.

### Privacidade

O prompt viaja dentro da URL. Quem recebe o link lê o texto completo. O zip1.io é um serviço externo e guarda a URL longa para redirecionar.

Não use este plugin com prompt que contenha dado pessoal, credencial ou informação confidencial.

O link curto não expira por padrão. Para limitar o acesso, peça uma senha, um prazo de validade ou um número máximo de cliques. O conector `zip1` aceita os três controles.

## Requisitos

| Item | Necessário | Se faltar |
|------|------------|-----------|
| Python 3.8 ou superior | Sim | O script de codificação não roda. No Windows, o comando costuma ser `python` em vez de `python3` |
| Conector `zip1` | Não | O plugin entrega a URL longa, sem encurtar, e informa o código e o significado do erro |

O script usa apenas a biblioteca padrão do Python. Você não instala nenhuma dependência externa.

## Como instalar no Claude Cowork

O Cowork instala o plugin pelo marketplace do repositório.

1. Abra a aba **Cowork** no aplicativo Claude.
2. Selecione **Personalizar** na barra lateral esquerda.
3. Clique na aba **Plugins**.
4. Clique no botão **Adicionar**.
5. Escolha **Adicionar marketplace**.
6. Escolha **Adicioar de um repositório**.
7. Informe o endereço `https://github.com/marioluciofjr/prompt-link`.
8. Instale o plugin prompt-link na lista que aparece.

O Cowork guarda o plugin no seu computador. Instale plugins apenas de fontes que você conhece.

### Depois de instalar

Autorize o conector `zip1` quando o aplicativo pedir. Sem essa autorização, o plugin monta e testa o link, mas entrega a URL longa.

## Como instalar no Claude Code

Execute os dois comandos no terminal:

```
/plugin marketplace add marioluciofjr/prompt-link
/plugin install prompt-link@marioluciofjr
```

## Exemplos de uso

Peça em linguagem natural:

- "Transforma esse texto em um link do ChatGPT"
- "Gera um link de prompt com isso aqui"
- "Encurta esse prompt em link pra eu compartilhar no Perplexity"
- "Como fica esse texto em percent-encoding pro grok.com/?q="

O fluxo roda em três etapas:

| Etapa | Ação | Responsável |
|-------|------|-------------|
| 1 | Confere se há prompt, se há destino válido e se a URL cabe no limite | Agente `analisador` |
| 2 | Codifica o texto e monta a URL longa | Agente `montador` |
| 3 | Encurta pelo zip1.io, testa e entrega o link | Agente `encurtador` |

O `analisador` aponta todas as pendências de uma vez. Se faltar algo, o Claude pergunta antes de montar o link.

## Links úteis
* []()
* []()
* []()
* []()
* []()
* []()
* []()
* []()
* []()
* []()

## Contribuições
Abra uma issue para relatar erro de codificação, destino fora do ar ou pedido de novo LLM. Para enviar código, abra um pull request. Todo script Python deste plugin segue o padrão descrito em "Arquitetura do script".

## Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato
Mário Lúcio - Prazo Certo®
<div>
  <a href="https://www.linkedin.com/in/marioluciofjr" target="_blank"><img src="https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a>
  <a href = "mailto:marioluciofjr@gmail.com" target="_blank"><img src="https://img.shields.io/badge/-Gmail-%23333?style=for-the-badge&logo=gmail&logoColor=white"></a>
  <a href="https://prazocerto.me/contato" target="_blank"><img src="https://img.shields.io/badge/prazocerto.me/contato-230023?style=for-the-badge&logo=wordpress&logoColor=white"></a>
</div>

