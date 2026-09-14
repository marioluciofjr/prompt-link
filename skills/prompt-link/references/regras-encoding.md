# Regras de percent-encoding para a query string de um prompt-link

## 1. Anatomia da URL

```
https://claude.ai/new?q={prompt_codificado}
└─ esquema ─┘└─ host ─┘└path┘└ ─┘└──── valor da query ────┘
                                ^ nome do parâmetro: q
```

Apenas o **valor** de `q` é codificado. A base da URL é fixa e nunca sofre encoding.

### Bases por destino

| Destino | Chave | Base | Host | Caminho |
|---------|-------|------|------|---------|
| Claude | `claude` | `https://claude.ai/new?q=` | `claude.ai` | `/new` |
| ChatGPT | `chatgpt` | `https://chatgpt.com/?q=` | `chatgpt.com` | `/` |
| Perplexity | `perplexity` | `https://perplexity.ai/search/new?q=` | `perplexity.ai` | `/search/new` |
| Grok | `grok` | `https://grok.com/?q=` | `grok.com` | `/` |

O parâmetro é sempre `q` nos quatro destinos, e a regra de codificação do valor é idêntica em todos. Só a base muda.

## 2. Conjunto *unreserved* (RFC 3986, seção 2.3)

Passam literais, sem codificação:

```
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
a b c d e f g h i j k l m n o p q r s t u v w x y z
0 1 2 3 4 5 6 7 8 9
- . _ ~
```

**Todo o resto vira percent-encoding.** Isso inclui os caracteres *reserved* (`: / ? # [ ] @ ! $ & ' ( ) * + , ; =`), o espaço, todos os caracteres de controle e todos os caracteres fora do ASCII.

## 3. Caracteres ASCII: `%` + coluna Hex

Para qualquer caractere ASCII, o percent-encoding é `%` seguido do valor da coluna **Hex** da tabela ASCII, em dois dígitos maiúsculos.

| Caractere | Hex | Percent | Por que importa |
|-----------|-----|---------|-----------------|
| espaço | `20` | `%20` | separador mais comum em prompts |
| `"` | `22` | `%22` | aspas duplas em instruções |
| `#` | `23` | `%23` | **crítico**: sem codificar, tudo após o `#` vira fragmento e é perdido |
| `%` | `25` | `%25` | **crítico**: deve ser codificado primeiro, senão corrompe as outras sequências |
| `&` | `26` | `%26` | **crítico**: sem codificar, inicia um novo parâmetro e trunca o prompt |
| `+` | `2B` | `%2B` | literal `+` seria lido como espaço por alguns parsers |
| `/` | `2F` | `%2F` | comum em datas e caminhos |
| `=` | `3D` | `%3D` | separador de parâmetro |
| `?` | `3F` | `%3F` | inicia query string |
| LF | `0A` | `%0A` | quebra de linha — estrutura o prompt em parágrafos |
| CR | `0D` | `%0D` | usar `%0D%0A` só se precisar de CRLF; `%0A` sozinho basta |
| TAB | `09` | `%09` | indentação |

A tabela completa dos 128 valores está em `tabela-ascii.md`.

## 4. Caracteres fora do ASCII (acentos, emoji, símbolos)

Caracteres não-ASCII **não têm um único byte hex**. O procedimento é:

1. Codificar o caractere em **UTF-8**, obtendo de 2 a 4 bytes.
2. Escrever cada byte como `%XX`.

Exemplos relevantes para português:

| Caractere | Bytes UTF-8 | Percent-encoding |
|-----------|-------------|------------------|
| `á` | C3 A1 | `%C3%A1` |
| `ã` | C3 A3 | `%C3%A3` |
| `â` | C3 A2 | `%C3%A2` |
| `é` | C3 A9 | `%C3%A9` |
| `ê` | C3 AA | `%C3%AA` |
| `í` | C3 AD | `%C3%AD` |
| `ó` | C3 B3 | `%C3%B3` |
| `ô` | C3 B4 | `%C3%B4` |
| `õ` | C3 B5 | `%C3%B5` |
| `ú` | C3 BA | `%C3%BA` |
| `ç` | C3 A7 | `%C3%A7` |
| `Ç` | C3 87 | `%C3%87` |
| `–` (travessão) | E2 80 93 | `%E2%80%93` |
| `“` | E2 80 9C | `%E2%80%9C` |
| `”` | E2 80 9D | `%E2%80%9D` |
| `→` | E2 86 92 | `%E2%86%92` |

## 5. Ordem de operações

Sempre nesta ordem, para não corromper a saída:

1. Normalizar o texto (remover espaços duplicados no fim das linhas, padronizar quebras `\r\n` → `\n`).
2. Codificar em UTF-8.
3. Percent-encodar byte a byte, com `%` (Hex `25`) tratado junto dos demais — nunca em uma segunda passada.
4. Concatenar com a base do destino escolhido (tabela da seção 1).

Nunca codificar duas vezes: `%20` virando `%2520` é o erro mais comum e quebra o prompt silenciosamente.

## 6. Limites práticos

| Limite | Valor | Consequência |
|--------|-------|--------------|
| URL segura em todos os navegadores | ~2.000 caracteres | acima disso, Chrome/Safari podem truncar |
| **Limite do encurtador zip1.io** | **7.500 caracteres** | **acima disso o link não é gerado** |
| Limite comum de servidor | 8.192 bytes na linha de requisição | HTTP 414 |
| Limite duro do Chrome | 32.779 caracteres | erro de navegação |

O limite operacional do plugin é **7.500 caracteres de URL**, medido sobre a URL completa (base do destino + query codificada), não sobre o texto original. Acima dele o fluxo para na etapa de análise (agente `analisador`) e devolve, literalmente:

```
Não foi possível encurtar o link, pois o prompt tem mais de 7500 caracteres
```

Como o percent-encoding infla o texto (um `á` vira 6 caracteres, uma quebra de linha vira 3), um prompt de 400 caracteres em português já pode passar de 1.000 na URL. O fator de expansão típico em português fica entre 1,4x e 2,0x, o que coloca o teto prático de texto por volta de 3.700 a 5.300 caracteres. O script devolve o fator medido em cada caso no campo `fator_de_expansao`, e o teto estimado do texto em `teto_de_texto_estimado` quando há bloqueio.

## 7. Verificação (round-trip)

Um link só é considerado correto se a decodificação devolver exatamente o texto de origem:

```python
from urllib.parse import quote, unquote

BASES = {
    "claude": "https://claude.ai/new?q=",
    "chatgpt": "https://chatgpt.com/?q=",
    "perplexity": "https://perplexity.ai/search/new?q=",
    "grok": "https://grok.com/?q=",
}

original = "Explique o que é RFC 3986.\nCite 3 exemplos práticos."
codificado = quote(original, safe="")
url = BASES["claude"] + codificado

assert unquote(codificado) == original   # round-trip obrigatório
assert len(url) <= 7500                  # limite do encurtador
```

Se o `assert` falhar, o problema é dupla codificação ou um caractere não normalizado — refazer do passo 1.
