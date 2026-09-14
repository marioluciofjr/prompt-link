# Erros do zip1.io

Fonte: documentação da API do zip1.io (https://zip1.io/api), seções "Error Responses" e "Rate Limiting".

## Quando usar

Sempre que o `create_short_url` ou o `get_url_stats` devolver erro. A resposta do conector chega como texto: procurar nela o código HTTP (três dígitos), o `reason` (quando vier) e a `message`.

Informar o erro nesta linha, com o significado da tabela:

```markdown
**Erro do zip1:** <código HTTP> <reason, se houver> — <significado>
```

Exemplo:

```markdown
**Erro do zip1:** 429 — Limite de criação atingido: o zip1.io aceita 10 links por minuto por IP. Tente de novo em 1 minuto.
```

## 1. Criar link curto (`create_short_url`)

A documentação lista os valores de `reason` do código 400 sem descrever cada um. Os significados dessas linhas seguem o nome do código. Quando a resposta trouxer a `message`, resumir essa mensagem em português junto do significado.

| Código | `reason` | Significado |
|--------|----------|-------------|
| 400 | `empty` | A URL chegou vazia ao zip1.io. |
| 400 | `no_scheme` | A URL não começa com `https://` ou `http://`. |
| 400 | `scheme_typo` | O início da URL está escrito errado, por exemplo `htps://`. |
| 400 | `unsupported_scheme` | O tipo de endereço não é aceito. O zip1.io só encurta `http` e `https`. |
| 400 | `email` | O texto enviado parece um e-mail, não uma URL. |
| 400 | `own_domain` | A URL aponta para o próprio zip1.io. |
| 400 | `ip_address` | A URL usa um endereço IP em vez de um domínio. |
| 400 | `not_public` | A URL aponta para um endereço que não é público, como uma rede local. |
| 400 | `no_tld` | O domínio não tem extensão, como `.com` ou `.ai`. |
| 400 | `whitespace` | A URL contém espaços. Indica falha de codificação. |
| 400 | `too_long` | A URL passou do tamanho que o zip1.io aceita. |
| 400 | `malformed` | A URL está malformada. |
| 400 | sem `reason` | O zip1.io recusou um parâmetro opcional: alias, senha, limite de cliques, prazo de expiração ou descrição. |
| 400 | sem `reason` (`Invalid JSON data`) | A requisição chegou vazia ao zip1.io. Falha do conector. Tente de novo mais tarde. |
| 403 | `blocked` | O destino está na lista de bloqueio do zip1.io, ou a URL já é um link curto. |
| 403 | `destination-velocity` | Muitos links para este mesmo destino foram criados na última hora, e o zip1.io pausou esse destino. É temporário e não depende da pessoa usuária. Tente de novo em 1 hora. |
| 403 | `unsafe-destination` | O Google Safe Browsing classifica o destino como inseguro. O campo `threat` diz o tipo de ameaça. |
| 403 | `redirect-destination` | A URL redireciona para um destino bloqueado. O campo `target` mostra esse destino. |
| 409 | `duplicate` | O alias escolhido já existe. Escolha outro alias. |
| 415 | sem `reason` | A requisição chegou sem o formato JSON esperado. Falha do conector. Tente de novo mais tarde. |
| 429 | sem `reason` | Limite de criação atingido: o zip1.io aceita 10 links por minuto por IP. Tente de novo em 1 minuto. |
| 503 | `not-saved` | O zip1.io não conseguiu gravar o link, e nenhum link foi criado. Tente de novo em instantes. |

### Ação do agente `encurtador`

| Erro | Ação |
|------|------|
| `whitespace` ou `malformed` | Reprovar e devolver ao `montador`: a codificação falhou. |
| `too_long` | Reprovar e devolver ao `analisador`: o limite de tamanho não foi respeitado. |
| Qualquer outro | Entregar a URL longa no formato de exceção 2 de `assets/formato-entrega.md`, com a linha do erro. |

## 2. Consultar estatísticas (`get_url_stats`)

| Código | Significado |
|--------|-------------|
| 404 | O zip1.io não encontrou o link curto. Confira o código do link. |
| 429 | Limite de consulta atingido: o zip1.io aceita 30 consultas de estatísticas por minuto por IP. Tente de novo em 1 minuto. |

Erro nesta consulta não reprova o link. A célula "Redirecionamento" da entrega recebe `Não verificado — erro <código>: <significado>`.

## 3. Resposta sem código

Conector desconectado, sem resposta ou com erro sem código HTTP:

```markdown
**Erro do zip1:** sem código — O conector zip1 não está disponível nesta sessão.
```

## Regras

- Nunca inventar um código. Sem código na resposta, usar a seção 3.
- Código fora das tabelas: informar o código e resumir em português a `message` recebida.
- Não repetir a requisição automaticamente. A orientação de nova tentativa é para a pessoa usuária.
