#! /home/rakhmaevao/Projects/personal/bbd-language-extension/.venv/bin/python
import re
from typing import List
from lsprotocol import types
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument

# Стандартные типы токенов — используем только те, что есть в темах
TOKEN_TYPES = ["variable", "keyword"]  # порядок важен!

class SimpleSemanticServer(LanguageServer):
    def __init__(self, name, version):
        super().__init__(name, version)
        self.cached_tokens = {}

    def lex_and_tokenize(self, doc: TextDocument):
        tokens = []
        prev_line = 0
        prev_col = 0

        for line_idx, line in enumerate(doc.lines):
            # Находим все непробельные фрагменты вне и внутри скобок
            pos = 0
            inside = False
            while pos < len(line):
                # Пропускаем пробелы
                if line[pos].isspace():
                    pos += 1
                    continue

                if line[pos] == '[':
                    inside = True
                    pos += 1
                    continue
                elif line[pos] == ']':
                    inside = False
                    pos += 1
                    continue
                else:
                    # Читаем слово (всё до следующей скобки или пробела)
                    start = pos
                    while pos < len(line) and line[pos] not in "[] \t\n\r":
                        pos += 1
                    word = line[start:pos]
                    if not word:
                        continue

                    # Определяем тип
                    tok_type = "keyword" if inside else "variable"
                    tok_type_index = TOKEN_TYPES.index(tok_type)

                    # Относительные координаты
                    delta_line = line_idx - prev_line
                    delta_start = start - (prev_col if delta_line == 0 else 0)

                    tokens.append((
                        delta_line,
                        delta_start,
                        len(word),
                        tok_type_index,
                        0  # modifiers = 0
                    ))

                    prev_line = line_idx
                    prev_col = start

        return tokens

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

if __name__ == "__main__":
    server.start_io()