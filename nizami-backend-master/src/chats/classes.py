from collections import Counter

import aspose.words as aw


class MostUsedFont:
    def __init__(self, document: aw.Document):
        self.document = document
        self._font_cache = {}

    def format(self, tup):
        if tup is None:
            return None

        return {
            'name': tup[0],
            'size': tup[1],
        }

    def most_used_font_for_style(self, style_name: str):
        if style_name in self._font_cache:
            return self.format(self._font_cache[style_name])


        font_usage = []

        for paragraph in self.document.get_child_nodes(aw.NodeType.PARAGRAPH, True):
            paragraph = paragraph.as_paragraph()
            if paragraph.paragraph_format.style.name == style_name:
                for run in paragraph.runs:
                    font = run.as_run().font
                    if font.name and font.size:
                        font_usage.append((font.name, font.size))

        if not font_usage:
            self._font_cache[style_name] = None
            return None

        most_common_font = Counter(font_usage).most_common(1)[0][0]
        self._font_cache[style_name] = most_common_font

        return self.format(most_common_font)
