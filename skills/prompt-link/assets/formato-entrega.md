# Formato da entrega final do prompt-link

Modelo único da saída. O agente `encurtador` e a conversa principal (quando não há subagentes) preenchem este modelo. Nada entra antes nem depois dele.

## 1. Entrega padrão — link curto aprovado

```markdown
## Link do prompt — <rótulo do destino>

**Link curto:** <url_curta>

**Estatísticas:** <link de estatísticas devolvido pelo zip1>

| Verificação | Resultado |
|-------------|-----------|
| Destino | <host><caminho> |
| Round-trip do texto | OK |
| Redirecionamento | <resultado da conferência no zip1> |
| Parâmetro q preenchido | <resultado da conferência do parâmetro q> |
| Tamanho da URL longa | <n> de 7500 caracteres |
```

Exemplo preenchido:

```markdown
## Link do prompt — Grok

**Link curto:** https://zip1.io/KVEAM1

**Estatísticas:** https://zip1.io/stats/KVEAM1

| Verificação | Resultado |
|-------------|-----------|
| Destino | grok.com/ |
| Round-trip do texto | OK |
| Redirecionamento | Confirmado pelo zip1 → grok.com/ |
| Parâmetro q preenchido | Sim — "Fazendo um teste legal" |
| Tamanho da URL longa | 48 de 7500 caracteres |
```

### Como preencher

| Campo | Origem | Valor |
|-------|--------|-------|
| Rótulo do destino | Chave do destino | `Claude`, `ChatGPT`, `Perplexity` ou `Grok` |
| Link curto | Linha `Short URL created` da resposta do `create_short_url` | Copiar sem alterar |
| Estatísticas | Linha `View stats` da resposta do `create_short_url` | Copiar sem alterar |
| Destino | Host e caminho da URL longa | `grok.com/`, `claude.ai/new`, `chatgpt.com/`, `perplexity.ai/search/new` |
| Round-trip do texto | Campo `aprovada` do `--conferir` | `OK` |
| Redirecionamento | `Original URL` do `get_url_stats`, aprovada no `--conferir` | `Confirmado pelo zip1 → <host><caminho>` |
| Redirecionamento | Erro na consulta de estatísticas (`references/erros-zip1.md`) | `Não verificado — erro <código>: <significado>` |
| Parâmetro q preenchido | Campo `prompt_decodificado` do `--conferir` | `Sim — "<início do prompt>"` |
| Tamanho da URL longa | Campo `caracteres_url` do script | `<n> de 7500 caracteres` |

O início do prompt ocupa até 60 caracteres. Se o prompt for maior, cortar e terminar com `...`.

O link de estatísticas é único para cada link curto e vem pronto na resposta do conector zip1. Nunca montar esse endereço a partir do código. Se a resposta não trouxer a linha `View stats`, omitir a linha **Estatísticas**.

## 2. Exceção — erro ou indisponibilidade do zip1

Sem link curto, entregar a URL longa, informar o erro e omitir a linha de estatísticas:

```markdown
## Link do prompt — <rótulo do destino>

**Link direto:** <url_longa>

O zip1.io não encurtou o link. Este é o link direto, sem encurtamento.

**Erro do zip1:** <código HTTP> <reason, se houver> — <significado>

| Verificação | Resultado |
|-------------|-----------|
| Destino | <host><caminho> |
| Round-trip do texto | OK |
| Redirecionamento | Não se aplica |
| Parâmetro q preenchido | <resultado da conferência do parâmetro q> |
| Tamanho da URL longa | <n> de 7500 caracteres |
```

Preencher a linha **Erro do zip1** com `references/erros-zip1.md`. Exemplo: `**Erro do zip1:** 429 — Limite de criação atingido: o zip1.io aceita 10 links por minuto por IP. Tente de novo em 1 minuto.`

## 3. Exceção — a pessoa usuária pede o link completo

Entregar o formato padrão e acrescentar esta linha logo depois da linha de estatísticas:

```markdown
**Link completo:** <url_longa>
```

## 4. Link reprovado

```markdown
## Link do prompt reprovado — <rótulo do destino>

**Motivo:** <o que falhou>

**Etapa a refazer:** analisador / montador / encurtador
```

## Regras

- Sem emojis.
- Sem mensagem introdutória antes do formato e sem conclusão depois dele.
- A URL longa não aparece na entrega padrão. Ela só aparece nas exceções 2 e 3.
- Com mais de um destino, repetir o bloco uma vez por destino, na ordem pedida.
- Não alterar, reencurtar ou reescrever os links recebidos.
- Não prometer permanência do link curto: o zip1.io é um serviço externo.
