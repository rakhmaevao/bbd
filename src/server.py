import operator
from functools import reduce

from lsprotocol import types

from src.semantic import SimpleSemanticServer
from src.token import TOKEN_TYPES

server = SimpleSemanticServer("bracket-semantic-server", "v1")


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def on_change(ls: SimpleSemanticServer, params: types.DidChangeTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.cached_tokens[doc.uri] = ls.lex_and_tokenize(doc)


@server.feature(
    types.TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    types.SemanticTokensLegend(
        token_types=TOKEN_TYPES,
        token_modifiers=[],
    ),
)
def semantic_tokens(ls: SimpleSemanticServer, params: types.SemanticTokensParams):
    data = []
    for token in ls.cached_tokens.get(params.text_document.uri, []):
        data.extend(
            [
                token.line,
                token.offset,
                len(token.text),
                TOKEN_TYPES.index(token.tok_type),
                reduce(operator.or_, token.tok_modifiers, 0),
            ]
        )
    return types.SemanticTokens(data=data)
