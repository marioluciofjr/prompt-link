---
name: prompt-link
description: Use SEMPRE que a pessoa usuária quiser um prompt-link — qualquer pedido para transformar um texto em link de prompt, gerar link de prompt, criar URL com o prompt preenchido, montar query string de um prompt, encurtar um prompt em link ou compartilhar um prompt como link, para Claude, ChatGPT, Perplexity ou Grok. Também quando mencionar prompt-link, claude.ai/new?q, chatgpt.com/?q, perplexity.ai/search/new?q, grok.com/?q, query string, percent-encoding, %0A, %20, codificar texto para URL ou encurtador zip1.io. Se faltar o prompt ou o destino, ou se o texto passar do limite, o fluxo avisa antes de montar qualquer link.
---

# Prompt-link

Converter um texto em uma URL de prompt do LLM escolhido, conferir o limite de tamanho, encurtar pelo zip1.io, testar e entregar.

## Quando esta skill roda

Sempre que o pedido for um prompt-link, em qualquer formulação. Não esperar pelas palavras exatas: "vira link", "manda como link", "link pra abrir já com o prompt", "compartilha esse prompt" e equivalentes são pedidos de prompt-link.

## Destinos suportados

| Destino | Chave | Base da URL |
|---------|-------|-------------|
| Claude | `claude` | `https://claude.ai/new?q=` |
| ChatGPT | `chatgpt` | `https://chatgpt.com/?q=` |
| Perplexity | `perplexity` | `https://perplexity.ai/search/new?q=` |
| Grok | `grok` | `https://grok.com/?q=` |

Nenhum outro destino é aceito. Nunca assumir Claude como padrão.

## Fluxo obrigatório

Executar as três etapas em ordem. Não pular nenhuma.

| Etapa | Agente | Faz | Sai com |
|-------|--------|-----|---------|
| 1 | `analisador` | Confere se há prompt, se há destino válido e se a URL cabe em 7500 caracteres | APROVADO, ou a lista de pendências com o feedback |
| 2 | `montador` | Monta a URL longa e confere o round-trip | URL longa aprovada |
| 3 | `encurtador` | Encurta pelo zip1.io, testa e faz a entrega final | Entrega no formato padrão |

## Papel da conversa principal

Os subagentes não enxergam o histórico da conversa e não fazem perguntas à pessoa usuária. A conversa principal liga as etapas:

1. **Chamar o `analisador`** com o pedido da pessoa usuária, literalmente, sem resumir nem reescrever.
2. **Tratar o veredito PENDENTE.** Mostrar o feedback do `analisador` e resolver o que falta:
   - Destino ausente ou inválido: perguntar com AskUserQuestion, oferecendo os quatro destinos com o rótulo e a base da URL.
   - Prompt ausente: pedir o texto que vai virar link.
   - Acima do limite: mostrar a mensagem padrão e os caminhos possíveis, e parar.

   Com a resposta, chamar o `analisador` de novo, passando o pedido original e o complemento.
3. **Chamar o `montador`** com o caminho do arquivo do prompt e a chave do destino, depois do veredito APROVADO.
4. **Chamar o `encurtador`** com a URL longa, o caminho do arquivo do prompt e a chave do destino.
5. **Repassar a entrega** do `encurtador` sem reescrever.

Mais de um destino: rodar as etapas 2 e 3 uma vez por destino.

### Sem subagentes

Quando a sessão não oferece subagentes, a conversa principal executa as três etapas por conta própria, seguindo em ordem as instruções de:

- `${CLAUDE_PLUGIN_ROOT}/agents/analisador.md`
- `${CLAUDE_PLUGIN_ROOT}/agents/montador.md`
- `${CLAUDE_PLUGIN_ROOT}/agents/encurtador.md`

Nesse caso, a própria conversa principal faz a pergunta de destino com AskUserQuestion.

## Script do plugin

Todo número, URL e conferência sai do script, nunca de cálculo manual:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/prompt-link/scripts/montar_query.py" --analisar --arquivo "<arquivo>" --destino <chave>
python3 "${CLAUDE_PLUGIN_ROOT}/skills/prompt-link/scripts/montar_query.py" --destino <chave> --arquivo "<arquivo>"
python3 "${CLAUDE_PLUGIN_ROOT}/skills/prompt-link/scripts/montar_query.py" --conferir "<url>" --arquivo "<arquivo>" --destino <chave>
python3 "${CLAUDE_PLUGIN_ROOT}/skills/prompt-link/scripts/montar_query.py" --decodificar "<url>"
python3 "${CLAUDE_PLUGIN_ROOT}/skills/prompt-link/scripts/montar_query.py" --listar-destinos
```

Se `python3` não existir (comum no Windows), usar `python`. O script não tem destino padrão: sem `--destino`, a montagem é recusada.

Códigos de retorno: `0` aprovado, `1` entrada inválida ou pendente, `2` round-trip ou conferência falhou, `3` URL acima de 7500 caracteres.

## Regras de codificação

- **RFC 3986 estrita.** Só passam literais `A-Z`, `a-z`, `0-9`, `-`, `.`, `_`, `~`. Todo o resto vira `%XX`, com o valor Hex em maiúsculas. Espaço é `%20`, nunca `+`.
- **Fora do ASCII**, cada byte UTF-8 vira `%XX`. Exemplo: `ç` → `%C3%A7`.
- **Preservar a estrutura.** Quebras de linha viram `%0A` e mantêm parágrafos e listas legíveis quando o prompt abre no LLM.
- **Não editar o prompt.** A skill codifica, não reescreve, resume ou "melhora" o texto, a menos que a pessoa usuária peça.
- **Codificar uma única vez.** `%20` virando `%2520` é dupla codificação e corrompe o prompt.

Consultar `references/tabela-ascii.md` para os 128 valores Hex e `references/regras-encoding.md` para a ordem de operações, os caracteres críticos (`#`, `&`, `%`) e os limites de tamanho.

## Limite de tamanho

Limite: **7500 caracteres de URL**, contando a base do destino e a query codificada. Acima dele, o fluxo para na etapa 1 com a mensagem padrão, literalmente:

```
Não foi possível encurtar o link, pois o prompt tem mais de 7500 caracteres
```

Essa frase é fixa. Não reescrever, não traduzir, não suavizar.

## Formato da entrega

O modelo de saída está em `assets/formato-entrega.md`, fonte única para o `encurtador` e para a execução sem subagentes. Com o encurtamento aprovado, a entrega mostra o link curto, o link de estatísticas e a tabela de verificações; a URL longa só aparece se o encurtador falhar ou se a pessoa usuária pedir o link completo.

O link de estatísticas é único para cada link curto e vem pronto na resposta do `create_short_url` (linha `View stats`). Nunca montar esse endereço a partir do código.

Quando o zip1 devolve erro, a entrega informa o código HTTP e o significado do erro, conforme `references/erros-zip1.md`.

## Padrão de código

Qualquer script Python deste plugin é orientado a objetos, com alta coesão e baixo acoplamento: uma responsabilidade por classe, dependências recebidas no construtor, domínio separado da interface de linha de comando. Alterações no script seguem esse padrão.
