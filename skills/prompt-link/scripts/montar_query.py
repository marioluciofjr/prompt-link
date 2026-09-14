#!/usr/bin/env python3
"""Analisa, monta e confere a URL de prompt de um LLM a partir de um texto.

Destinos suportados:
    claude      https://claude.ai/new?q=
    chatgpt     https://chatgpt.com/?q=
    perplexity  https://perplexity.ai/search/new?q=
    grok        https://grok.com/?q=

Uso (um modo por agente do plugin):
    analisador  python3 montar_query.py --analisar --arquivo prompt.txt [--destino grok]
    montador    python3 montar_query.py --destino claude --arquivo prompt.txt
    encurtador  python3 montar_query.py --conferir "https://..." --arquivo prompt.txt --destino claude
    apoio       python3 montar_query.py --decodificar "https://grok.com/?q=..."
    apoio       python3 montar_query.py --listar-destinos

O texto vem de --arquivo (UTF-8, recomendado), do argumento posicional ou de
stdin. No Windows, se "python3" nao existir, use "python".

Regra de codificacao: RFC 3986 estrita (safe=""), UTF-8, espaco como %20.
Limite do encurtador zip1.io: 7500 caracteres de URL.

Codigos de retorno:
    0  aprovado
    1  entrada invalida ou pendente (prompt ausente, destino ausente ou invalido)
    2  round-trip ou conferencia do link falhou
    3  URL acima de 7500 caracteres

Arquitetura: cada classe tem uma responsabilidade unica e depende apenas de
abstracoes recebidas no construtor. Nenhuma classe de dominio conhece a CLI,
e a CLI nao conhece os detalhes de codificacao, medicao ou parsing.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Iterable, Iterator, Protocol
from urllib.parse import quote, unquote, urlparse


# ---------------------------------------------------------------------------
# Dominio: destino
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Destino:
    """Um LLM de destino e o formato da URL de prompt que ele aceita."""

    chave: str
    rotulo: str
    base: str
    host: str
    caminho: str

    def montar_url(self, query_codificada: str) -> str:
        return f"{self.base}{query_codificada}"

    def corresponde_host(self, host: str) -> bool:
        return self._normalizar_host(host) == self.host

    def corresponde_caminho(self, caminho: str) -> bool:
        return caminho.rstrip("/") == self.caminho.rstrip("/")

    def como_dicionario(self) -> dict:
        return {
            "chave": self.chave,
            "rotulo": self.rotulo,
            "base": self.base,
            "host": self.host,
            "caminho": self.caminho,
        }

    @staticmethod
    def _normalizar_host(host: str) -> str:
        # Remove porta e o prefixo "www." sem usar str.removeprefix,
        # que so existe a partir do Python 3.9.
        host = host.strip().lower().split(":")[0]
        return host[4:] if host.startswith("www.") else host


class DestinoDesconhecidoError(ValueError):
    """Levantada quando a chave de destino nao existe no catalogo."""


class CatalogoDeDestinos:
    """Guarda os destinos suportados e resolve chaves e URLs."""

    def __init__(self, destinos: Iterable[Destino]) -> None:
        self._destinos: dict[str, Destino] = {d.chave: d for d in destinos}

    def __iter__(self) -> Iterator[Destino]:
        return iter(self._destinos.values())

    def __contains__(self, chave: object) -> bool:
        return chave in self._destinos

    @property
    def chaves(self) -> list[str]:
        return sorted(self._destinos)

    def obter(self, chave: str) -> Destino:
        try:
            return self._destinos[chave]
        except KeyError as erro:
            disponiveis = ", ".join(self.chaves)
            raise DestinoDesconhecidoError(
                f"destino invalido: {chave} (use {disponiveis})"
            ) from erro

    def identificar_por_host(self, host: str) -> Destino | None:
        for destino in self._destinos.values():
            if destino.corresponde_host(host):
                return destino
        return None

    def como_dicionario(self) -> dict:
        return {d.chave: d.como_dicionario() for d in self._destinos.values()}


def catalogo_padrao() -> CatalogoDeDestinos:
    return CatalogoDeDestinos(
        [
            Destino("claude", "Claude", "https://claude.ai/new?q=", "claude.ai", "/new"),
            Destino("chatgpt", "ChatGPT", "https://chatgpt.com/?q=", "chatgpt.com", "/"),
            Destino(
                "perplexity",
                "Perplexity",
                "https://perplexity.ai/search/new?q=",
                "perplexity.ai",
                "/search/new",
            ),
            Destino("grok", "Grok", "https://grok.com/?q=", "grok.com", "/"),
        ]
    )


# ---------------------------------------------------------------------------
# Texto: normalizacao e codificacao
# ---------------------------------------------------------------------------


class Normalizador(Protocol):
    def normalizar(self, texto: str) -> str: ...


class Codificador(Protocol):
    def codificar(self, texto: str) -> str: ...

    def decodificar(self, codificado: str) -> str: ...


class NormalizadorDePrompt:
    """Padroniza quebras de linha e espacos sem alterar o conteudo."""

    def normalizar(self, texto: str) -> str:
        texto = texto.replace("\r\n", "\n").replace("\r", "\n")
        linhas = [linha.rstrip() for linha in texto.split("\n")]
        return "\n".join(linhas).strip()


class CodificadorRFC3986:
    """Percent-encoding estrito: apenas A-Z a-z 0-9 - . _ ~ passam literais."""

    CONJUNTO_SEGURO = ""

    def codificar(self, texto: str) -> str:
        return quote(texto, safe=self.CONJUNTO_SEGURO)

    def decodificar(self, codificado: str) -> str:
        # unquote (e nao unquote_plus): um "+" literal continua sendo "+",
        # ja que o espaco e sempre codificado como %20.
        return unquote(codificado)


# ---------------------------------------------------------------------------
# Dominio: link
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Link:
    """Resultado imutavel da montagem: texto, query e URL de um destino."""

    destino: Destino
    texto_original: str
    query_codificada: str
    round_trip_ok: bool

    @property
    def url(self) -> str:
        return self.destino.montar_url(self.query_codificada)

    @property
    def caracteres_url(self) -> int:
        return len(self.url)

    @property
    def caracteres_texto(self) -> int:
        return len(self.texto_original)

    @property
    def fator_de_expansao(self) -> float:
        if not self.caracteres_texto:
            return 0.0
        return round(self.caracteres_url / self.caracteres_texto, 2)

    def como_dicionario(self) -> dict:
        return {
            "destino": self.destino.chave,
            "destino_rotulo": self.destino.rotulo,
            "base": self.destino.base,
            "prompt_original": self.texto_original,
            "caracteres_original": self.caracteres_texto,
            "query_codificada": self.query_codificada,
            "url": self.url,
            "caracteres_url": self.caracteres_url,
            "fator_de_expansao": self.fator_de_expansao,
            "round_trip_ok": self.round_trip_ok,
        }


class ConstrutorDeLink:
    """Compoe normalizador, codificador e destino para produzir um Link."""

    def __init__(
        self,
        catalogo: CatalogoDeDestinos,
        normalizador: Normalizador | None = None,
        codificador: Codificador | None = None,
    ) -> None:
        self._catalogo = catalogo
        self._normalizador = normalizador or NormalizadorDePrompt()
        self._codificador = codificador or CodificadorRFC3986()

    def construir(self, texto: str, chave_destino: str) -> Link:
        destino = self._catalogo.obter(chave_destino)
        original = self._normalizador.normalizar(texto)
        codificada = self._codificador.codificar(original)
        round_trip_ok = self._codificador.decodificar(codificada) == original
        return Link(
            destino=destino,
            texto_original=original,
            query_codificada=codificada,
            round_trip_ok=round_trip_ok,
        )


# ---------------------------------------------------------------------------
# Dominio: auditoria de tamanho
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LaudoDeTamanho:
    """Veredito do auditor sobre um Link, sem conhecer como ele foi montado."""

    caracteres_url: int
    limite_seguro: int
    limite_encurtador: int
    acima_do_limite_seguro: bool
    acima_do_limite_encurtador: bool
    mensagem_bloqueio: str | None = None
    excedente: int = 0
    teto_de_texto_estimado: int | None = None

    @property
    def pode_encurtar(self) -> bool:
        return not self.acima_do_limite_encurtador

    @property
    def margem_restante(self) -> int:
        return max(self.limite_encurtador - self.caracteres_url, 0)

    def como_dicionario(self) -> dict:
        dados = {
            "caracteres_url": self.caracteres_url,
            "limite_seguro": self.limite_seguro,
            "acima_do_limite_seguro": self.acima_do_limite_seguro,
            "limite_encurtador": self.limite_encurtador,
            "acima_do_limite_encurtador": self.acima_do_limite_encurtador,
            "pode_encurtar": self.pode_encurtar,
            "margem_restante": self.margem_restante,
        }
        if self.acima_do_limite_encurtador:
            dados["mensagem_bloqueio"] = self.mensagem_bloqueio
            dados["excedente"] = self.excedente
            dados["teto_de_texto_estimado"] = self.teto_de_texto_estimado
        return dados


class AuditorDeTamanho:
    """Aplica os limites de URL. Nao codifica, nao encurta, nao formata."""

    MENSAGEM_BLOQUEIO = (
        "Não foi possível encurtar o link, pois o prompt tem mais de 7500 caracteres"
    )

    def __init__(self, limite_encurtador: int = 7500, limite_seguro: int = 2000) -> None:
        self._limite_encurtador = limite_encurtador
        self._limite_seguro = limite_seguro

    def auditar(self, link: Link) -> LaudoDeTamanho:
        caracteres = link.caracteres_url
        acima_encurtador = caracteres > self._limite_encurtador

        return LaudoDeTamanho(
            caracteres_url=caracteres,
            limite_seguro=self._limite_seguro,
            limite_encurtador=self._limite_encurtador,
            acima_do_limite_seguro=caracteres > self._limite_seguro,
            acima_do_limite_encurtador=acima_encurtador,
            mensagem_bloqueio=self.MENSAGEM_BLOQUEIO if acima_encurtador else None,
            excedente=caracteres - self._limite_encurtador if acima_encurtador else 0,
            teto_de_texto_estimado=(
                self._estimar_teto(link) if acima_encurtador else None
            ),
        )

    def _estimar_teto(self, link: Link) -> int | None:
        if not link.fator_de_expansao:
            return None
        return int(self._limite_encurtador / link.fator_de_expansao)


# ---------------------------------------------------------------------------
# Dominio: analise de entrada (etapa do agente analisador)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Pendencia:
    """Algo que impede a montagem do link e precisa de retorno da pessoa usuaria."""

    PROMPT_AUSENTE = "prompt_ausente"
    DESTINO_AUSENTE = "destino_ausente"
    DESTINO_INVALIDO = "destino_invalido"
    ACIMA_DO_LIMITE = "acima_do_limite"

    tipo: str
    mensagem: str

    @property
    def e_de_entrada(self) -> bool:
        # Pendencias de entrada se resolvem com uma pergunta; a de tamanho, nao.
        return self.tipo != self.ACIMA_DO_LIMITE

    def como_dicionario(self) -> dict:
        return {"tipo": self.tipo, "mensagem": self.mensagem}


@dataclass(frozen=True)
class AnaliseDeEntrada:
    """Resultado das tres conferencias: prompt, destino e limite de tamanho."""

    caracteres_texto: int
    destino: Destino | None
    laudos: dict[str, LaudoDeTamanho]
    pendencias: tuple[Pendencia, ...]

    @property
    def aprovada(self) -> bool:
        return not self.pendencias

    @property
    def tem_pendencia_de_entrada(self) -> bool:
        return any(p.e_de_entrada for p in self.pendencias)

    @property
    def destinos_que_cabem(self) -> list[str]:
        return [chave for chave, laudo in self.laudos.items() if laudo.pode_encurtar]

    def como_dicionario(self) -> dict:
        return {
            "aprovada": self.aprovada,
            "prompt_informado": self.caracteres_texto > 0,
            "caracteres_texto": self.caracteres_texto,
            "destino": self.destino.chave if self.destino else None,
            "destino_rotulo": self.destino.rotulo if self.destino else None,
            "tamanhos": {c: l.como_dicionario() for c, l in self.laudos.items()},
            "destinos_que_cabem": self.destinos_que_cabem,
            "pendencias": [p.como_dicionario() for p in self.pendencias],
        }


class AnalisadorDeEntrada:
    """Confere prompt, destino e limite antes de qualquer montagem.

    Junta todas as pendencias de uma vez, para que a pessoa usuaria receba
    o feedback completo em uma unica resposta.
    """

    def __init__(
        self,
        catalogo: CatalogoDeDestinos,
        construtor: ConstrutorDeLink,
        auditor: AuditorDeTamanho,
        normalizador: Normalizador | None = None,
    ) -> None:
        self._catalogo = catalogo
        self._construtor = construtor
        self._auditor = auditor
        self._normalizador = normalizador or NormalizadorDePrompt()

    def analisar(self, texto: str, chave_destino: str | None) -> AnaliseDeEntrada:
        pendencias: list[Pendencia] = []
        original = self._normalizador.normalizar(texto)
        if not original:
            pendencias.append(
                Pendencia(Pendencia.PROMPT_AUSENTE, "Nenhum texto de prompt foi informado.")
            )

        destino = self._resolver_destino(chave_destino, pendencias)
        laudos = self._medir(original, destino) if original else {}
        self._conferir_limite(laudos, pendencias)

        return AnaliseDeEntrada(
            caracteres_texto=len(original),
            destino=destino,
            laudos=laudos,
            pendencias=tuple(pendencias),
        )

    def _resolver_destino(
        self, chave: str | None, pendencias: list[Pendencia]
    ) -> Destino | None:
        if not chave:
            pendencias.append(
                Pendencia(Pendencia.DESTINO_AUSENTE, "O LLM de destino não foi informado.")
            )
            return None
        if chave not in self._catalogo:
            disponiveis = ", ".join(self._catalogo.chaves)
            pendencias.append(
                Pendencia(
                    Pendencia.DESTINO_INVALIDO,
                    f"Destino inválido: {chave}. Use {disponiveis}.",
                )
            )
            return None
        return self._catalogo.obter(chave)

    def _medir(self, texto: str, destino: Destino | None) -> dict[str, LaudoDeTamanho]:
        # Sem destino definido, mede todos: o feedback ja diz onde o texto cabe.
        destinos = [destino] if destino else list(self._catalogo)
        return {
            d.chave: self._auditor.auditar(self._construtor.construir(texto, d.chave))
            for d in destinos
        }

    @staticmethod
    def _conferir_limite(
        laudos: dict[str, LaudoDeTamanho], pendencias: list[Pendencia]
    ) -> None:
        # So vira pendencia quando nenhum destino medido comporta a URL.
        if laudos and not any(laudo.pode_encurtar for laudo in laudos.values()):
            pendencias.append(
                Pendencia(Pendencia.ACIMA_DO_LIMITE, AuditorDeTamanho.MENSAGEM_BLOQUEIO)
            )


# ---------------------------------------------------------------------------
# Dominio: leitura reversa e conferencia (etapa do agente encurtador)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LinkLido:
    """URL existente decomposta em host, caminho, destino e prompt."""

    url: str
    host: str
    caminho: str
    prompt: str
    destino: Destino | None

    @property
    def host_esperado(self) -> bool:
        return bool(self.destino) and self.destino.corresponde_host(self.host)

    @property
    def caminho_esperado(self) -> bool:
        return bool(self.destino) and self.destino.corresponde_caminho(self.caminho)

    def pertence_a(self, destino: Destino | None) -> bool:
        """Diz se o link foi reconhecido como do destino pedido.

        Sem destino pedido, basta o link ser de algum destino conhecido.
        """
        if self.destino is None:
            return False
        return destino is None or self.destino.chave == destino.chave

    def como_dicionario(self) -> dict:
        return {
            "url": self.url,
            "host": self.host,
            "path": self.caminho,
            "destino": self.destino.chave if self.destino else "desconhecido",
            "destino_rotulo": self.destino.rotulo if self.destino else None,
            "prompt_decodificado": self.prompt,
            "caracteres": len(self.prompt),
            "host_esperado": self.host_esperado,
            "path_esperado": self.caminho_esperado,
        }


class LeitorDeLink:
    """Decompoe uma URL de prompt de volta ao texto e identifica o destino."""

    def __init__(
        self,
        catalogo: CatalogoDeDestinos,
        codificador: Codificador | None = None,
        parametro: str = "q",
    ) -> None:
        self._catalogo = catalogo
        self._codificador = codificador or CodificadorRFC3986()
        self._parametro = parametro

    def ler(self, url: str) -> LinkLido:
        partes = urlparse(url.strip())
        return LinkLido(
            url=url,
            host=partes.netloc,
            caminho=partes.path,
            prompt=self._extrair_parametro(partes.query),
            destino=self._catalogo.identificar_por_host(partes.netloc),
        )

    def _extrair_parametro(self, query: str) -> str:
        # Leitura manual em vez de parse_qs: parse_qs troca "+" por espaco
        # e alteraria um prompt que contenha o sinal de mais.
        for par in query.split("&"):
            nome, _, valor = par.partition("=")
            if nome == self._parametro:
                return self._codificador.decodificar(valor)
        return ""


@dataclass(frozen=True)
class Conferencia:
    """Compara um link (longo ou de destino final) com o prompt original."""

    lido: LinkLido
    destino_pedido: Destino | None
    prompt_identico: bool

    @property
    def destino_confere(self) -> bool:
        return self.lido.pertence_a(self.destino_pedido)

    @property
    def aprovada(self) -> bool:
        return (
            self.destino_confere
            and self.lido.host_esperado
            and self.lido.caminho_esperado
            and self.prompt_identico
        )

    def como_dicionario(self) -> dict:
        return {
            **self.lido.como_dicionario(),
            "destino_pedido": self.destino_pedido.chave if self.destino_pedido else None,
            "destino_confere": self.destino_confere,
            "prompt_identico": self.prompt_identico,
            "aprovada": self.aprovada,
        }


class ConferidorDeLink:
    """Decide se um link leva ao destino certo com o prompt intacto."""

    def __init__(
        self,
        catalogo: CatalogoDeDestinos,
        leitor: LeitorDeLink,
        normalizador: Normalizador | None = None,
    ) -> None:
        self._catalogo = catalogo
        self._leitor = leitor
        self._normalizador = normalizador or NormalizadorDePrompt()

    def conferir(self, url: str, texto: str, chave_destino: str | None) -> Conferencia:
        destino = self._catalogo.obter(chave_destino) if chave_destino else None
        lido = self._leitor.ler(url)
        original = self._normalizador.normalizar(texto)
        return Conferencia(
            lido=lido,
            destino_pedido=destino,
            prompt_identico=lido.prompt == original,
        )


# ---------------------------------------------------------------------------
# Aplicacao: casos de uso
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Resultado:
    """Saida de um caso de uso: dados serializaveis e codigo de retorno."""

    dados: dict
    codigo: int = 0


class ServicoDeLink:
    """Orquestra os casos de uso. Unico ponto que conhece varias classes."""

    SUCESSO = 0
    ERRO_ENTRADA = 1
    ERRO_ROUND_TRIP = 2
    ERRO_TAMANHO = 3

    def __init__(
        self,
        construtor: ConstrutorDeLink,
        auditor: AuditorDeTamanho,
        analisador: AnalisadorDeEntrada,
        leitor: LeitorDeLink,
        conferidor: ConferidorDeLink,
        catalogo: CatalogoDeDestinos,
    ) -> None:
        self._construtor = construtor
        self._auditor = auditor
        self._analisador = analisador
        self._leitor = leitor
        self._conferidor = conferidor
        self._catalogo = catalogo

    def analisar(self, texto: str, chave_destino: str | None) -> Resultado:
        analise = self._analisador.analisar(texto, chave_destino)
        if analise.aprovada:
            return Resultado(analise.como_dicionario(), self.SUCESSO)
        if analise.tem_pendencia_de_entrada:
            return Resultado(analise.como_dicionario(), self.ERRO_ENTRADA)
        return Resultado(analise.como_dicionario(), self.ERRO_TAMANHO)

    def montar(self, texto: str, chave_destino: str) -> Resultado:
        link = self._construtor.construir(texto, chave_destino)
        laudo = self._auditor.auditar(link)
        dados = {**link.como_dicionario(), **laudo.como_dicionario()}

        if not link.round_trip_ok:
            return Resultado(dados, self.ERRO_ROUND_TRIP)
        if not laudo.pode_encurtar:
            return Resultado(dados, self.ERRO_TAMANHO)
        return Resultado(dados, self.SUCESSO)

    def conferir(self, url: str, texto: str, chave_destino: str | None) -> Resultado:
        conferencia = self._conferidor.conferir(url, texto, chave_destino)
        codigo = self.SUCESSO if conferencia.aprovada else self.ERRO_ROUND_TRIP
        return Resultado(conferencia.como_dicionario(), codigo)

    def decodificar(self, url: str) -> Resultado:
        return Resultado(self._leitor.ler(url).como_dicionario(), self.SUCESSO)

    def listar_destinos(self) -> Resultado:
        return Resultado(self._catalogo.como_dicionario(), self.SUCESSO)

    @classmethod
    def padrao(cls) -> "ServicoDeLink":
        catalogo = catalogo_padrao()
        construtor = ConstrutorDeLink(catalogo)
        auditor = AuditorDeTamanho()
        leitor = LeitorDeLink(catalogo)
        return cls(
            construtor=construtor,
            auditor=auditor,
            analisador=AnalisadorDeEntrada(catalogo, construtor, auditor),
            leitor=leitor,
            conferidor=ConferidorDeLink(catalogo, leitor),
            catalogo=catalogo,
        )


# ---------------------------------------------------------------------------
# Interface: leitura do texto e CLI
# ---------------------------------------------------------------------------


class LeitorDeTexto:
    """Obtem o texto do prompt de um arquivo, do argumento ou de stdin, em UTF-8.

    Ler o arquivo ou os bytes de stdin como UTF-8 evita que o Windows
    interprete acentos e emojis com a codificacao cp1252 do console.
    """

    def __init__(self, entrada=None) -> None:
        self._entrada = entrada if entrada is not None else sys.stdin

    def ler(self, arquivo: str | None, texto: str | None) -> str:
        if arquivo:
            # utf-8-sig descarta o BOM que alguns editores gravam no inicio.
            with open(arquivo, encoding="utf-8-sig") as origem:
                return origem.read()
        if texto is not None:
            return texto
        return self._ler_entrada_padrao()

    def _ler_entrada_padrao(self) -> str:
        if self._entrada is None or self._entrada.isatty():
            return ""
        buffer = getattr(self._entrada, "buffer", None)
        if buffer is not None:
            return buffer.read().decode("utf-8")
        return self._entrada.read()


class ParserDeArgumentos(argparse.ArgumentParser):
    """ArgumentParser que sai com codigo 1, e nao 2, em argumento invalido.

    O codigo 2 fica reservado para falha de round-trip ou de conferencia.
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        print(f"erro: {message}", file=sys.stderr)
        raise SystemExit(1)


class InterfaceLinhaDeComando:
    """Traduz argumentos e stdin em chamadas ao servico. Nao contem regra."""

    def __init__(
        self,
        servico: ServicoDeLink,
        leitor: LeitorDeTexto | None = None,
        saida=None,
        erro=None,
    ) -> None:
        self._servico = servico
        self._leitor = leitor or LeitorDeTexto()
        self._saida = saida or sys.stdout
        self._erro = erro or sys.stderr

    def executar(self, argv: list[str] | None = None) -> int:
        args = self._analisar_argumentos(argv)

        if args.listar_destinos:
            return self._emitir(self._servico.listar_destinos())
        if args.decodificar:
            return self._emitir(self._servico.decodificar(args.decodificar))

        try:
            texto = self._leitor.ler(args.arquivo, args.texto)
        except (OSError, UnicodeDecodeError) as falha:
            return self._falhar(f"nao foi possivel ler o texto ({falha})")

        try:
            if args.analisar:
                return self._emitir(self._servico.analisar(texto, args.destino))
            if not texto.strip():
                return self._falhar("nenhum texto informado")
            if args.conferir:
                return self._emitir(
                    self._servico.conferir(args.conferir, texto, args.destino)
                )
            if not args.destino:
                return self._falhar(
                    "informe --destino (use --analisar para ver o que falta)"
                )
            return self._emitir(self._servico.montar(texto, args.destino))
        except DestinoDesconhecidoError as falha:
            return self._falhar(str(falha))

    @staticmethod
    def _analisar_argumentos(argv: list[str] | None) -> argparse.Namespace:
        parser = ParserDeArgumentos(
            description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument("texto", nargs="?", help="texto do prompt (ou --arquivo, ou stdin)")
        parser.add_argument("--arquivo", metavar="CAMINHO", help="arquivo UTF-8 com o prompt")
        parser.add_argument(
            "--destino",
            metavar="CHAVE",
            help="LLM de destino: " + ", ".join(catalogo_padrao().chaves) + " (sem padrao)",
        )

        modos = parser.add_mutually_exclusive_group()
        modos.add_argument(
            "--analisar",
            action="store_true",
            help="confere prompt, destino e limite e lista as pendencias",
        )
        modos.add_argument(
            "--conferir",
            metavar="URL",
            help="confere se a URL leva ao destino com o prompt identico ao original",
        )
        modos.add_argument(
            "--decodificar",
            metavar="URL",
            help="decodifica uma URL de prompt de volta ao texto original",
        )
        modos.add_argument(
            "--listar-destinos",
            action="store_true",
            help="lista os destinos suportados e suas bases",
        )
        return parser.parse_args(argv)

    def _emitir(self, resultado: Resultado) -> int:
        print(
            json.dumps(resultado.dados, ensure_ascii=False, indent=2),
            file=self._saida,
        )
        return resultado.codigo

    def _falhar(self, mensagem: str) -> int:
        print(f"erro: {mensagem}", file=self._erro)
        return ServicoDeLink.ERRO_ENTRADA


def _usar_utf8_no_console() -> None:
    # No Windows a saida padrao usa cp1252 e quebra ao imprimir emojis.
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    _usar_utf8_no_console()
    return InterfaceLinhaDeComando(ServicoDeLink.padrao()).executar(argv)


if __name__ == "__main__":
    raise SystemExit(main())
