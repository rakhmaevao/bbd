from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument

from src.token import Token


class SimpleSemanticServer(LanguageServer):
    def __init__(self, name, version):
        super().__init__(name, version)
        self.cached_tokens: dict[str, list[Token]] = {}

    def lex_and_tokenize(self, doc: TextDocument) -> list[Token]:
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

                if line[pos] == "[":
                    inside = True
                    pos += 1
                    continue
                elif line[pos] == "]":
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

                    # Относительные координаты
                    delta_line = line_idx - prev_line
                    delta_start = start - (prev_col if delta_line == 0 else 0)

                    tokens.append(
                        Token(
                            line=delta_line,
                            offset=delta_start,
                            text=word,
                            tok_type=tok_type,
                        )
                    )

                    prev_line = line_idx
                    prev_col = start

        return tokens
