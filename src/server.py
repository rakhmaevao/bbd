from lsprotocol import types

from src.semantic import TOKEN_TYPES, SimpleSemanticServer


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
        token_modifiers=[],  # не используем
    ),
)
def semantic_tokens(ls: SimpleSemanticServer, params: types.SemanticTokensParams):
    data = []
    for token in ls.cached_tokens.get(params.text_document.uri, []):
        data.extend(token)
    return types.SemanticTokens(data=data)
