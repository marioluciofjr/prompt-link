# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). Versionamento semântico.

## [0.4.0] - 2026-09-14

### Alterado (instalação)

- O README ficou só com a instalação pelo marketplace do repositório. A instalação pelo arquivo `.plugin` saiu da documentação.

### Alterado (agentes)

- Os cinco agentes (`revisor`, `query`, `investiga`, `testa` e `entrega`) deram lugar a três: `analisador`, `montador` e `encurtador`.
- O `analisador` confere prompt, destino e limite de uma vez e devolve todas as pendências juntas. A pergunta de destino continua sendo feita pela conversa principal, porque subagentes não usam AskUserQuestion.
- O prompt é gravado em arquivo uma única vez, e os três agentes leem esse arquivo. O texto não é mais recopiado entre as etapas.
- O `encurtador` encurta, testa e faz a entrega final. Ele herda as ferramentas da sessão, exceto as de escrita, e por isso enxerga o zip1 como conector do Cowork ou como servidor do plugin no Claude Code.
- O formato da entrega passou a ter uma fonte única, na pasta de modelos da skill: `assets/formato-entrega.md`.
- A entrega segue o formato validado no Claude Cowork: título "Link do prompt", link curto, estatísticas e a tabela de verificações (destino, round-trip, redirecionamento, parâmetro q e tamanho da URL longa).

### Corrigido (estatísticas)

- O link de estatísticas vem da linha `View stats` da resposta do `create_short_url`, único para cada link curto. O plugin não monta mais esse endereço a partir do código.

### Alterado (marketplace)

- A versão do plugin fica só no `plugin.json`. A entrada do `marketplace.json` perdeu o campo `version`, que o Claude Code ignorava sem aviso.
- A entrada do `marketplace.json` perdeu `"strict": false` e voltou ao padrão (`true`): o `plugin.json` e as pastas do plugin definem os componentes.

### Corrigido (referências)

- `tabela-ascii.md` não quebra mais a tabela: a crase (`60`) usa um trecho de código com duas crases, a barra invertida (`5C`) aparece com uma barra só e as células de escape vazias mostram "—".

### Corrigido

- O plugin não abre mais o link curto para testar. O `encurtador` consulta a URL guardada pelo `get_url_stats` do zip1 e confere essa URL no script. Antes, o teste com `curl` e navegador somava cliques falsos nas estatísticas, e Claude e ChatGPT respondiam `403` ao `curl`, reprovando links corretos.
- O script não assume mais `claude` quando falta `--destino`.
- O script roda em Python 3.8, como o README informa (saiu `str.removeprefix`).
- No Windows, o script lê o texto em UTF-8 e imprime emojis sem erro.
- `--decodificar` preserva o sinal `+` literal do prompt.
- Argumento inválido sai com código `1`; o código `2` fica só para falha de round-trip ou de conferência.
- Os comandos indicam `python` quando `python3` não existe.

### Adicionado

- Modos `--analisar`, `--conferir` e `--arquivo` no script.
- Arquivo `references/erros-zip1.md`. Quando o zip1 devolve erro, a entrega informa o código HTTP e o significado. Exemplo: `429` indica o limite de 10 links por minuto por IP.

## [0.3.0] - 2026-09-13

### Alterado (nome da skill)

- A skill `query-string-claude` passou a se chamar `prompt-link`, igual ao plugin. Quem usa o nome antigo em atalho ou anotação precisa atualizar.
- O README foi reescrito no padrão PZCT-PTS100 e ganhou a seção de instalação no Claude Cowork.

### Adicionado

- Arquivo `.claude-plugin/marketplace.json`, que permite instalar o plugin por `/plugin marketplace add`.
- Link de estatísticas do zip1.io (`https://zip1.io/stats/<código>`) na entrega final.
- Seções de instalação, requisitos, privacidade, contribuição e licença no README.
- Arquivo `LICENSE` com o texto da licença MIT.

### Alterado

- A entrega final mostra apenas o link curto e o link de estatísticas. A URL longa saiu do formato padrão.
- O agente `testa` passa o código do encurtador e o link de estatísticas ao agente `entrega`.

### Comportamento preservado

- A URL longa continua aparecendo quando o encurtador falha e quando a pessoa usuária pede o link completo.

## [0.2.0]

### Adicionado

- Destinos ChatGPT, Perplexity e Grok, além do Claude.
- Agente `revisor`, que confirma o LLM de destino antes de qualquer codificação.
- Limite de 7500 caracteres de URL, aplicado pelo agente `investiga`.

## [0.1.0]

### Adicionado

- Versão inicial: codificação RFC 3986 para `claude.ai/new?q=`, encurtamento pelo zip1.io e teste do link.
