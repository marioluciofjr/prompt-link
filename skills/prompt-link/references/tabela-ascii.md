# Tabela ASCII completa — Hex, percent-encoding e uso na query string

Fonte dos valores da coluna Hex: https://en.wikipedia.org/wiki/ASCII

Regra geral: o percent-encoding de um caractere ASCII é `%` seguido do valor da coluna **Hex** em dois dígitos maiúsculos. Exemplo: LF (quebra de linha) tem Hex `0A`, então vira `%0A`.


## 1. Caracteres de controle (0x00–0x1F)

Todos **devem** ser percent-encoded. Nunca aparecem literais em uma URL.

| Hex | Dec | Abrev. | Nome | Escape | Percent |
|-----|-----|--------|------|--------|---------|
| `00` | 0 | NUL | Nulo | `\0` | `%00` |
| `01` | 1 | SOH | Início de cabeçalho | — | `%01` |
| `02` | 2 | STX | Início de texto | — | `%02` |
| `03` | 3 | ETX | Fim de texto | — | `%03` |
| `04` | 4 | EOT | Fim de transmissão | — | `%04` |
| `05` | 5 | ENQ | Consulta | — | `%05` |
| `06` | 6 | ACK | Reconhecimento | — | `%06` |
| `07` | 7 | BEL | Sino / alerta | `\a` | `%07` |
| `08` | 8 | BS | Retrocesso | `\b` | `%08` |
| `09` | 9 | HT | Tabulação horizontal | `\t` | `%09` |
| `0A` | 10 | LF | Quebra de linha | `\n` | `%0A` |
| `0B` | 11 | VT | Tabulação vertical | `\v` | `%0B` |
| `0C` | 12 | FF | Avanço de página | `\f` | `%0C` |
| `0D` | 13 | CR | Retorno de carro | `\r` | `%0D` |
| `0E` | 14 | SO | Shift Out | — | `%0E` |
| `0F` | 15 | SI | Shift In | — | `%0F` |
| `10` | 16 | DLE | Escape de enlace de dados | — | `%10` |
| `11` | 17 | DC1 | Controle de dispositivo 1 (XON) | — | `%11` |
| `12` | 18 | DC2 | Controle de dispositivo 2 | — | `%12` |
| `13` | 19 | DC3 | Controle de dispositivo 3 (XOFF) | — | `%13` |
| `14` | 20 | DC4 | Controle de dispositivo 4 | — | `%14` |
| `15` | 21 | NAK | Reconhecimento negativo | — | `%15` |
| `16` | 22 | SYN | Ocioso síncrono | — | `%16` |
| `17` | 23 | ETB | Fim do bloco de transmissão | — | `%17` |
| `18` | 24 | CAN | Cancelar | — | `%18` |
| `19` | 25 | EM | Fim do meio | — | `%19` |
| `1A` | 26 | SUB | Substituto | — | `%1A` |
| `1B` | 27 | ESC | Escape | `\e` | `%1B` |
| `1C` | 28 | FS | Separador de arquivo | — | `%1C` |
| `1D` | 29 | GS | Separador de grupo | — | `%1D` |
| `1E` | 30 | RS | Separador de registro | — | `%1E` |
| `1F` | 31 | US | Separador de unidade | — | `%1F` |

## 2. Caracteres imprimíveis (0x20–0x7E)

A coluna **Codificar?** segue a RFC 3986: apenas `A-Z`, `a-z`, `0-9`, `-`, `.`, `_`, `~` são *unreserved* e passam literais. Todo o resto vira percent.

| Hex | Dec | Caractere | Nome | Codificar? | Percent |
|-----|-----|-----------|------|------------|---------|
| `20` | 32 | `(espaço)` | Espaço | **Sim** | `%20` |
| `21` | 33 | `!` | Ponto de exclamação | **Sim** | `%21` |
| `22` | 34 | `"` | Aspas duplas | **Sim** | `%22` |
| `23` | 35 | `#` | Cerquilha / hash | **Sim** | `%23` |
| `24` | 36 | `$` | Cifrão | **Sim** | `%24` |
| `25` | 37 | `%` | Porcentagem | **Sim** | `%25` |
| `26` | 38 | `&` | E comercial | **Sim** | `%26` |
| `27` | 39 | `'` | Apóstrofo | **Sim** | `%27` |
| `28` | 40 | `(` | Parêntese esquerdo | **Sim** | `%28` |
| `29` | 41 | `)` | Parêntese direito | **Sim** | `%29` |
| `2A` | 42 | `*` | Asterisco | **Sim** | `%2A` |
| `2B` | 43 | `+` | Sinal de mais | **Sim** | `%2B` |
| `2C` | 44 | `,` | Vírgula | **Sim** | `%2C` |
| `2D` | 45 | `-` | Hífen-menos | Não (unreserved) | `%2D` |
| `2E` | 46 | `.` | Ponto final | Não (unreserved) | `%2E` |
| `2F` | 47 | `/` | Barra | **Sim** | `%2F` |
| `30` | 48 | `0` | Dígito 0 | Não (unreserved) | `%30` |
| `31` | 49 | `1` | Dígito 1 | Não (unreserved) | `%31` |
| `32` | 50 | `2` | Dígito 2 | Não (unreserved) | `%32` |
| `33` | 51 | `3` | Dígito 3 | Não (unreserved) | `%33` |
| `34` | 52 | `4` | Dígito 4 | Não (unreserved) | `%34` |
| `35` | 53 | `5` | Dígito 5 | Não (unreserved) | `%35` |
| `36` | 54 | `6` | Dígito 6 | Não (unreserved) | `%36` |
| `37` | 55 | `7` | Dígito 7 | Não (unreserved) | `%37` |
| `38` | 56 | `8` | Dígito 8 | Não (unreserved) | `%38` |
| `39` | 57 | `9` | Dígito 9 | Não (unreserved) | `%39` |
| `3A` | 58 | `:` | Dois-pontos | **Sim** | `%3A` |
| `3B` | 59 | `;` | Ponto e vírgula | **Sim** | `%3B` |
| `3C` | 60 | `<` | Menor que | **Sim** | `%3C` |
| `3D` | 61 | `=` | Igual | **Sim** | `%3D` |
| `3E` | 62 | `>` | Maior que | **Sim** | `%3E` |
| `3F` | 63 | `?` | Interrogação | **Sim** | `%3F` |
| `40` | 64 | `@` | Arroba | **Sim** | `%40` |
| `41` | 65 | `A` | Letra maiúscula A | Não (unreserved) | `%41` |
| `42` | 66 | `B` | Letra maiúscula B | Não (unreserved) | `%42` |
| `43` | 67 | `C` | Letra maiúscula C | Não (unreserved) | `%43` |
| `44` | 68 | `D` | Letra maiúscula D | Não (unreserved) | `%44` |
| `45` | 69 | `E` | Letra maiúscula E | Não (unreserved) | `%45` |
| `46` | 70 | `F` | Letra maiúscula F | Não (unreserved) | `%46` |
| `47` | 71 | `G` | Letra maiúscula G | Não (unreserved) | `%47` |
| `48` | 72 | `H` | Letra maiúscula H | Não (unreserved) | `%48` |
| `49` | 73 | `I` | Letra maiúscula I | Não (unreserved) | `%49` |
| `4A` | 74 | `J` | Letra maiúscula J | Não (unreserved) | `%4A` |
| `4B` | 75 | `K` | Letra maiúscula K | Não (unreserved) | `%4B` |
| `4C` | 76 | `L` | Letra maiúscula L | Não (unreserved) | `%4C` |
| `4D` | 77 | `M` | Letra maiúscula M | Não (unreserved) | `%4D` |
| `4E` | 78 | `N` | Letra maiúscula N | Não (unreserved) | `%4E` |
| `4F` | 79 | `O` | Letra maiúscula O | Não (unreserved) | `%4F` |
| `50` | 80 | `P` | Letra maiúscula P | Não (unreserved) | `%50` |
| `51` | 81 | `Q` | Letra maiúscula Q | Não (unreserved) | `%51` |
| `52` | 82 | `R` | Letra maiúscula R | Não (unreserved) | `%52` |
| `53` | 83 | `S` | Letra maiúscula S | Não (unreserved) | `%53` |
| `54` | 84 | `T` | Letra maiúscula T | Não (unreserved) | `%54` |
| `55` | 85 | `U` | Letra maiúscula U | Não (unreserved) | `%55` |
| `56` | 86 | `V` | Letra maiúscula V | Não (unreserved) | `%56` |
| `57` | 87 | `W` | Letra maiúscula W | Não (unreserved) | `%57` |
| `58` | 88 | `X` | Letra maiúscula X | Não (unreserved) | `%58` |
| `59` | 89 | `Y` | Letra maiúscula Y | Não (unreserved) | `%59` |
| `5A` | 90 | `Z` | Letra maiúscula Z | Não (unreserved) | `%5A` |
| `5B` | 91 | `[` | Colchete esquerdo | **Sim** | `%5B` |
| `5C` | 92 | `\` | Barra invertida | **Sim** | `%5C` |
| `5D` | 93 | `]` | Colchete direito | **Sim** | `%5D` |
| `5E` | 94 | `^` | Acento circunflexo | **Sim** | `%5E` |
| `5F` | 95 | `_` | Sublinhado | Não (unreserved) | `%5F` |
| `60` | 96 | `` ` `` | Acento grave | **Sim** | `%60` |
| `61` | 97 | `a` | Letra minúscula a | Não (unreserved) | `%61` |
| `62` | 98 | `b` | Letra minúscula b | Não (unreserved) | `%62` |
| `63` | 99 | `c` | Letra minúscula c | Não (unreserved) | `%63` |
| `64` | 100 | `d` | Letra minúscula d | Não (unreserved) | `%64` |
| `65` | 101 | `e` | Letra minúscula e | Não (unreserved) | `%65` |
| `66` | 102 | `f` | Letra minúscula f | Não (unreserved) | `%66` |
| `67` | 103 | `g` | Letra minúscula g | Não (unreserved) | `%67` |
| `68` | 104 | `h` | Letra minúscula h | Não (unreserved) | `%68` |
| `69` | 105 | `i` | Letra minúscula i | Não (unreserved) | `%69` |
| `6A` | 106 | `j` | Letra minúscula j | Não (unreserved) | `%6A` |
| `6B` | 107 | `k` | Letra minúscula k | Não (unreserved) | `%6B` |
| `6C` | 108 | `l` | Letra minúscula l | Não (unreserved) | `%6C` |
| `6D` | 109 | `m` | Letra minúscula m | Não (unreserved) | `%6D` |
| `6E` | 110 | `n` | Letra minúscula n | Não (unreserved) | `%6E` |
| `6F` | 111 | `o` | Letra minúscula o | Não (unreserved) | `%6F` |
| `70` | 112 | `p` | Letra minúscula p | Não (unreserved) | `%70` |
| `71` | 113 | `q` | Letra minúscula q | Não (unreserved) | `%71` |
| `72` | 114 | `r` | Letra minúscula r | Não (unreserved) | `%72` |
| `73` | 115 | `s` | Letra minúscula s | Não (unreserved) | `%73` |
| `74` | 116 | `t` | Letra minúscula t | Não (unreserved) | `%74` |
| `75` | 117 | `u` | Letra minúscula u | Não (unreserved) | `%75` |
| `76` | 118 | `v` | Letra minúscula v | Não (unreserved) | `%76` |
| `77` | 119 | `w` | Letra minúscula w | Não (unreserved) | `%77` |
| `78` | 120 | `x` | Letra minúscula x | Não (unreserved) | `%78` |
| `79` | 121 | `y` | Letra minúscula y | Não (unreserved) | `%79` |
| `7A` | 122 | `z` | Letra minúscula z | Não (unreserved) | `%7A` |
| `7B` | 123 | `{` | Chave esquerda | **Sim** | `%7B` |
| `7C` | 124 | `\|` | Barra vertical | **Sim** | `%7C` |
| `7D` | 125 | `}` | Chave direita | **Sim** | `%7D` |
| `7E` | 126 | `~` | Til | Não (unreserved) | `%7E` |

## 3. DEL

| Hex | Dec | Abrev. | Nome | Percent |
|-----|-----|--------|------|---------|
| `7F` | 127 | DEL | Delete | `%7F` |
