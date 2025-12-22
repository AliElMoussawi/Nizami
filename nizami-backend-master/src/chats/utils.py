import difflib
import io
import random
import re
import string
from datetime import datetime

import aspose.words as aw
import httpx
from langchain_openai import ChatOpenAI

from src import settings
from src.chats.classes import MostUsedFont


def create_document_review_llm():
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model_name='o3-mini',
        request_timeout=30000,
        http_client=httpx.Client(
            timeout=httpx.Timeout(30000, connect=0000),
            # headers={
            #     'Connection': 'close',
            # },
        ),
    )


def create_legal_advice_llm():
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model_name='gpt-5-mini',
        request_timeout=30000,
        http_client=httpx.Client(
            timeout=httpx.Timeout(30000, connect=0000),
            # headers={
            #     'Connection': 'close',
            # },
        ),
        reasoning_effort='low',
    )

def create_llm(model_name, **kwargs):
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model_name=model_name,
        request_timeout=30000,
        http_client=httpx.Client(
            timeout=httpx.Timeout(30000, connect=0000),
            # headers={
            #     'Connection': 'close',
            # },
        ),
        **kwargs,
    )


def create_translation_llm():
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model_name='gpt-4o-mini',
        temperature=0.1,
        top_p=0.3,
        request_timeout=30000,
        http_client=httpx.Client(
            timeout=httpx.Timeout(30000, connect=0000),
            # headers={
            #     'Connection': 'close',
            # },
        ),
    )

def create_description_llm():
    return ChatOpenAI(
        openai_api_key=settings.OPENAI_API_KEY,
        model_name='gpt-4.1-mini',
        request_timeout=30000,
        http_client=httpx.Client(
            timeout=httpx.Timeout(30000, connect=0000),
            # headers={
            #     'Connection': 'close',
            # },
        ),
    )


def get_random_unclear_request_message():
    messages = [
        "Your request is unclear. Could you please provide more details or clarify your instructions?",
        "I’m sorry, but I couldn’t fully understand your request. Please provide further clarification.",
        "The instructions seem ambiguous. Kindly specify what changes or adjustments are required.",
        "Could you elaborate on your request? I want to ensure the output meets your expectations.",
        "I need more clarity on the instructions to proceed effectively. Could you please elaborate?",
        "It seems that the request was not fully understood. Kindly provide more details or an example.",
        "To deliver accurate results, I need clearer guidance on your requirements.",
        "Your instructions are somewhat unclear. Please help me understand by providing more context.",
        "The request lacks sufficient details. Could you clarify what changes or updates you expect?",
        "I couldn't interpret the instructions properly. Additional information would help improve the outcome."
    ]

    # Select a random message from the list
    return random.choice(messages)


def get_updated_file_message():
    messages = [
        "Please find the updated file attached.",
        "The revised file has been attached.",
        "Attached is the updated version of the file.",
        "Here’s the updated file as requested.",
        "I have attached the updated file.",
        "The updated document is attached.",
        "As requested, the updated file is now attached.",
        "Please find the revised file in the attachment.",
        "The updated version of the document is attached.",
        "I've attached the updated file."
    ]

    # Select a random message from the list
    return random.choice(messages)


def get_no_changes_message():
    messages = [
        "No updates were necessary—your input remains unchanged.",
        "Looks like everything is already in order! No modifications were made.",
        "No changes applied this time. Let us know if you need adjustments!",
        "Your request didn’t require any updates. Try refining your input for a different result.",
        "All good! No edits were needed based on the current content.",
        "No modifications were detected. Your content remains as is.",
        "No changes were made—perhaps try a different approach?",
        "Your input is already optimal! No further refinements were applied.",
        "Nothing to tweak here! Your content stays the same.",
        "No alterations were necessary. Let us know if you’d like a different result.",
    ]

    return random.choice(messages)


bullet_like_prefixes = ("•", "-", "–", "·", "*", "‣", "⁃")

ordered_prefix_patterns = [
    r"^\d+[\.\)]",  # 1. or 1)
    r"^[a-zA-Z][\.\)]",  # a. or A) or i)
    r"^[(][a-zA-Z0-9]+[)]",  # (a), (1)
]


def is_ordered_item(text):
    for pattern in ordered_prefix_patterns:
        if re.match(pattern, text):
            return True
    return False


def is_unordered_item(text):
    for bullet in bullet_like_prefixes:
        if text.startswith(bullet + " "):
            return True

    return False


def extract_doc_data(doc: aw.Document):
    json_data = []

    i = 0
    for p in doc.get_child_nodes(aw.NodeType.PARAGRAPH, True):
        if skip_p(p):
            continue

        paragraph = p.as_paragraph()
        text = paragraph.to_string(aw.SaveFormat.TEXT).strip()

        json_data.append({
            'i': i,
            'old': text,
            't': 'p',
            's': paragraph.paragraph_format.style.name,
        })
        i += 1

    return json_data


def extract_used_styles(doc: aw.Document):
    styles_json = []

    styles = set()
    for p in doc.get_child_nodes(aw.NodeType.PARAGRAPH, True):
        if skip_p(p):
            continue

        if p is not None:
            styles.add(p.as_paragraph().paragraph_format.style_name)

    for style_name in styles:
        style = doc.styles.get_by_name(style_name)
        font = style.font

        style_json = {
            'name': style.name,
        }

        if font:
            style_json['font'] = {
                "name": font.name,
                "size": font.size,
                "bold": font.bold,
                "italic": font.italic,
                "color": font.color.to_argb() if font.color is not None else None,
            }

        styles_json.append(style_json)

    return styles_json


def make_contextual_replacement_parts_with_fixes(orig_words, i1, i2, context_size=3):
    old_main = ' '.join(orig_words[i1:i2])

    prefix_start = max(i1 - context_size, 0)
    prefix = ' '.join(orig_words[prefix_start:i1])

    suffix = ''
    if prefix_start == i1:
        suffix_end = min(i2 + context_size, len(orig_words))
        suffix = ' '.join(orig_words[i2:suffix_end])

    old_phrase = ' '.join(filter(None, [prefix, old_main, suffix]))

    return prefix, old_phrase, suffix


def make_contextual_replacement_parts_with_fixes_2(orig_words, i1, i2, new_words, j1, j2, context_size=3):
    old_main = ' '.join(orig_words[i1:i2])

    prefix_start = max(j1 - context_size, 0)
    prefix = ' '.join(new_words[prefix_start:j1])

    suffix = ''
    if prefix_start == j1:
        suffix_end = min(i2 + context_size, len(orig_words))
        suffix = ' '.join(orig_words[i2:suffix_end])

    old_phrase = ' '.join(filter(None, [prefix, old_main, suffix]))

    return prefix, old_phrase, suffix


def make_contextual_replacement_parts(orig_words, i1, i2, new_words, j1, j2, context_size=3):
    prefix, old_phrase, suffix = make_contextual_replacement_parts_with_fixes_2(orig_words, i1, i2, new_words, j1, j2,
                                                                                context_size)

    new_main = ' '.join(new_words[j1:j2])

    new_phrase = ' '.join(filter(None, [prefix, new_main, suffix]))

    return old_phrase, new_phrase


def skip_p(p):
    text = p.as_paragraph().to_string(aw.SaveFormat.TEXT).strip()

    if p.get_ancestor(aw.NodeType.TABLE):
        return True

    footer = p.get_ancestor(aw.NodeType.HEADER_FOOTER)
    if footer and footer.as_header_footer().header_footer_type in (
            aw.HeaderFooterType.FOOTER_PRIMARY,
            aw.HeaderFooterType.FOOTER_FIRST,
            aw.HeaderFooterType.FOOTER_EVEN
    ):
        return True

    if is_inside_field(p):
        return True

    if is_inside_comment(p):
        return True

    if text == "":
        return True

    return False


def prepend_modifications(builder, doc, records, author, initial_author, date):
    modifications = []

    for record in records:
        if (record.get('i', None) is None or record.get('old', None) in [None, '']) and 'new' in record:
            modifications.append(record)
        else:
            break

    if len(modifications) > 0:
        builder.move_to_document_start()
        for record in modifications:
            builder.insert_html(record['new'].strip())

            reason = record.get('reason').strip()

            if reason:
                builder.current_paragraph.append_child(create_comment(reason, doc, author, initial_author, date))


def append_modifications(builder, doc, records):
    modifications = []

    for record in reversed(records):
        if (record.get('i', None) is None or record.get('old', None) in [None, '']) and 'new' in record:
            modifications.append(record)
        else:
            break

    for record in reversed(modifications):
        builder.move_to(doc.first_section)
        builder.insert_html(record['new'])


def create_comment(text, doc, author, initial_author, date):
    cmt = aw.Comment(doc, author, initial_author, date)
    cmt.set_text(text)
    return cmt


def get_run_index_at_char(run_positions, char_pos):
    for i, (run, start, end) in enumerate(run_positions):
        if start <= char_pos < end:
            return i, char_pos - start

    return None, None


def rejoin(words, breaker=' '):
    return breaker + pure_rejoin(words) + breaker


def pure_rejoin(words):
    text = ""
    for i, word in enumerate(words):
        if word in string.punctuation:
            text += word
        else:
            if i > 0:
                text += " " + word
            else:
                text += word

    return text


def apply_inline_tracked_changes(doc: aw.Document, old_para: aw.Paragraph, new_text, author_name, date_time):
    has_updates = False

    old_text = extract_text(old_para)
    matcher = difflib.SequenceMatcher(None, old_text.split(), new_text.split())

    old_text = old_text.split()
    new_text = new_text.split()

    run_positions = fill_run_positions(old_para)

    options = aw.replacing.FindReplaceOptions(aw.replacing.FindReplaceDirection.FORWARD)

    options.ignore_deleted = True
    options.ignore_inserted = True
    options.match_case = True

    for tag, i1, i2, j1, j2 in reversed(matcher.get_opcodes()):
        if tag == "equal":
            continue

        if ''.join(new_text[j1:j2]) == ''.join(old_text[i1:i2]):
            continue

        start_run_idx, start_offset = get_run_index_at_char(run_positions, i1)
        end_run_idx, end_offset = get_run_index_at_char(run_positions, i2 - 1 if i2 > 0 else 0)

        if tag in ("replace", "delete"):
            runs = []
            for idx in range(start_run_idx, end_run_idx + 1):

                run, run_start, run_end = run_positions[idx]
                if run is None:
                    continue

                text_start = run_start
                text_end = run_end

                local_start = max(0, i1 - text_start)
                run_text_length = len(run.text.split())
                local_end = min(run_text_length, i2 - text_start)

                if local_start > 0:
                    local_run = run.clone(True).as_run()
                    old_para.insert_before(local_run, run)

                    local_run.text = pure_rejoin(run.text.split()[:local_start]) + ' '
                    text = pure_rejoin(run.text.split()[local_start:])
                    if run.text.endswith(' '):
                        text += ' '
                    run.text = text

                    # if local_run.text == '':
                    #     local_run.remove()

                if local_end < run_text_length:
                    local_run = run.clone(True).as_run()
                    old_para.insert_after(local_run, run)
                    text = ' ' + pure_rejoin(run.text.split()[local_end - local_start:])
                    if run.text.endswith(' '):
                        text += ' '
                    local_run.text = text
                    run.text = pure_rejoin(run.text.split()[:local_end - local_start])

                    # if local_run.text == '':
                    #     local_run.remove()

                runs.append(run)

            if tag == 'delete':
                doc.start_track_revisions(author_name, date_time)
                for to_remove_run in runs:
                    to_remove_run.remove()
                doc.stop_track_revisions()

                run_positions = fill_run_positions(old_para)
                has_updates = True
                continue

            run_positions = fill_run_positions(old_para)
            start_run_idx, start_offset = get_run_index_at_char(run_positions, i1)
            end_run_idx, end_offset = get_run_index_at_char(run_positions, i2 - 1 if i2 > 0 else 0)

            new_run = runs[-1].clone(True).as_run()
            old_para.insert_after(new_run, runs[-1])

            # if run_positions and len(run_positions) > 0:
            #     if (end_run_idx + 1) < len(run_positions):
            #         current_run = run_positions[end_run_idx + 1][0]
            #         new_run = current_run.clone(True).as_run()
            #         old_para.insert_before(new_run, current_run)
            #         print(end_run_idx, len(run_positions))
            #         print('before', i2, old_text[i1:i2], new_text[j1:j2])
            #     else:
            #         current_run = run_positions[-1][0]
            #         new_run = current_run.clone(True).as_run()
            #         old_para.insert_after(new_run, current_run)
            #         print('after', old_text[i1:i2], new_text[j1:j2])
            #
            #
            # if not new_run:
            #    # check
            # new_run = aw.Run(doc)
            # old_para.append_child(new_run)

            doc.start_track_revisions(author_name, date_time)
            for to_remove_run in runs:
                to_remove_run.remove()
            doc.stop_track_revisions()

            text = pure_rejoin(new_text[j1:j2])
            if not text.startswith(' ') and start_run_idx > 0:
                text = ' ' + text

            if not text.endswith(' ') and (end_run_idx + 1) < len(run_positions) and run_positions[end_run_idx + 1][
                0].get_text() and not run_positions[end_run_idx + 1][0].get_text()[0].startswith(' '):
                text += ' '

            new_run.text = ''

            doc.start_track_revisions(author_name, date_time)
            new_run.text = text
            doc.stop_track_revisions()

            has_updates = True

        elif tag == 'insert':
            run, run_start, run_end = run_positions[start_run_idx]
            if run is None:
                continue

            text_start = run_start

            local_start = max(0, i1 - text_start)

            local_run = run.clone(True).as_run()
            old_para.insert_before(local_run, run)

            local_run.text = pure_rejoin(run.text.split()[:local_start])
            run.text = pure_rejoin(run.text.split()[local_start:]) + (' ' if run.text.endswith(' ') else '')

            new_run = run.clone(True).as_run()
            new_run.text = ''
            old_para.insert_before(new_run, run)

            doc.start_track_revisions(author_name, date_time)
            new_run.text = ' ' + pure_rejoin(new_text[j1:j2]) + ' '
            doc.stop_track_revisions()

            has_updates = True
            run_positions = fill_run_positions(old_para)

    return has_updates


def fill_run_positions(old_para):
    runs = list(old_para.get_child_nodes(aw.NodeType.RUN, True))
    run_positions = []
    pos = 0
    for r in runs:
        run: aw.Run = r.as_run()
        run_len = len(run.text.split())
        run_positions.append((run, pos, pos + run_len))
        pos += run_len
    return run_positions


def extract_text(old_para):
    runs = list(old_para.get_child_nodes(aw.NodeType.RUN, True))
    text = []

    for r in runs:
        run: aw.Run = r.as_run()
        text.append(run.text)

    return ' '.join(text)


def aspose_word_replace_json(file, old, records):
    new_records = {}

    last_i = None
    for i, record in enumerate(records):
        if record.get('old', '') != '' or 'new' not in record:
            last_i = record['i']
            continue

        if record.get('i', None) is None:
            index = None

            if last_i is not None:
                index = last_i

            if new_records.get(index, None) is None:
                new_records[index] = []

            new_records[index].append(record)
            continue

        index = record['i']
        last_i = index
        if new_records.get(index, None) is None:
            new_records[index] = []

        new_records[index].append(record)

    mapped_records = {}
    for i, record in enumerate(records):
        # no updates
        if 'new' not in record:
            continue

        old = record.get('old', '').strip()
        new = record.get('new', '').strip()

        # same sentence
        if old == new:
            continue

        # replacing empty string
        if old == '':
            continue

        # new added strings
        if record.get('i', None) is None:
            continue

        mapped_records[record['i']] = record

    doc = aw.Document(file)
    builder = aw.DocumentBuilder(doc)

    # Enable track changes
    now = datetime.now()
    author = "JP AI"
    initial_author = "JP"

    options = aw.replacing.FindReplaceOptions(aw.replacing.FindReplaceDirection.FORWARD)

    options.ignore_deleted = True
    options.ignore_inserted = True
    options.match_case = True

    i = 0
    for p in doc.get_child_nodes(aw.NodeType.PARAGRAPH, True):
        if skip_p(p):
            continue

        mapped_record = mapped_records.get(i)
        i += 1

        # replace or delete some paragraph
        if mapped_record is None:
            continue

        new = mapped_record.get('new', '').strip()
        reason = mapped_record.get('reason', '').strip()

        has_update = apply_inline_tracked_changes(doc, p.as_paragraph(), new, author, now)

        if has_update and reason:
            p.as_paragraph().append_child(create_comment(reason, doc, author, initial_author, now))

    doc.start_track_revisions(author, now)
    add_new_content(doc, i, new_records, author, initial_author, now)

    prepend_modifications(builder, doc, records, author, initial_author, now)
    # append_modifications(builder, doc, records)

    # Stop tracking changes
    doc.stop_track_revisions()

    # Save the document to a memory stream
    output_stream = io.BytesIO()
    doc.save(output_stream, aw.SaveFormat.DOCX)
    output_stream.seek(0)  # Move to the beginning of the stream

    return output_stream


def copy_font_attributes(source_font: aw.Font, target_font: aw.Font):
    target_font.name = source_font.name
    target_font.size = source_font.size
    target_font.bold = source_font.bold
    target_font.italic = source_font.italic
    target_font.underline = source_font.underline
    target_font.color = source_font.color
    target_font.highlight_color = source_font.highlight_color
    target_font.strike_through = source_font.strike_through
    target_font.double_strike_through = source_font.double_strike_through
    target_font.subscript = source_font.subscript
    target_font.superscript = source_font.superscript
    target_font.shadow = source_font.shadow
    target_font.outline = source_font.outline
    target_font.emboss = source_font.emboss
    target_font.engrave = source_font.engrave
    target_font.all_caps = source_font.all_caps
    target_font.small_caps = source_font.small_caps
    target_font.spacing = source_font.spacing
    target_font.position = source_font.position
    target_font.scaling = source_font.scaling
    target_font.kerning = source_font.kerning
    target_font.locale_id = source_font.locale_id
    target_font.locale_id_bi = source_font.locale_id_bi
    target_font.locale_id_far_east = source_font.locale_id_far_east
    target_font.name_bi = source_font.name_bi
    target_font.name_far_east = source_font.name_far_east
    target_font.theme_color = source_font.theme_color
    target_font.theme_font = source_font.theme_font


def add_new_content(doc: aw.Document, i, new_records, author, initial_author, now):
    i -= 1
    for p in reversed(doc.get_child_nodes(aw.NodeType.PARAGRAPH, True).to_array()):
        if skip_p(p):
            continue

        list_of_records = new_records.get(i)
        i -= 1

        if list_of_records is None:
            continue

        most_used_font = MostUsedFont(doc)

        # append new paragraph with known index
        html_doc = aw.Document()

        for style in doc.styles:
            html_doc.styles.add_copy(style)

        b = aw.DocumentBuilder(html_doc)

        for i_r, x in enumerate(list_of_records):
            b.insert_html(x['new'].strip())
            end = b.current_paragraph
            reason = x.get('reason', '').strip()

            if reason:
                end.append_child(create_comment(reason, html_doc, author, initial_author, now))

        target_para = p.as_paragraph()
        body = p.parent_node

        # KEEP_DIFFERENT_STYLES does not work
        # USE_DESTINATION_STYLES prints 100% fonts but wrong fonts in the final doc
        # KEEP_SOURCE_FORMATTING
        nodes = html_doc.first_section.body.get_child_nodes(aw.NodeType.ANY, False).to_array()
        for n_i, node in enumerate(nodes):
            imported = doc.import_node(node, True, aw.ImportFormatMode.USE_DESTINATION_STYLES)

            # skip empty paragraph that aw adds at the end of the temporary document
            if (
                    n_i == len(nodes) - 1 and
                    imported.node_type == aw.NodeType.PARAGRAPH and
                    not imported.get_text().strip()
            ):
                continue

            body.insert_after(imported, target_para)

            for run in imported.as_paragraph().runs:
                run_font = run.as_run().font

                font_t = most_used_font.most_used_font_for_style(imported.as_paragraph().paragraph_format.style.name)

                if font_t is not None:
                    run_font.name = font_t['name']
                    run_font.size = font_t['size']
                    continue

                p_font = imported.as_paragraph().paragraph_format.style.font
                copy_font_attributes(p_font, run.as_run().font)

            target_para = imported


def is_inside_field(node):
    current = node
    while current is not None:
        if isinstance(current, aw.fields.FieldStart):
            if current.field_type in (
                    aw.fields.FieldType.FIELD_HYPERLINK,
                    aw.fields.FieldType.FIELD_PAGE,
                    aw.fields.FieldType.FIELD_NUM_PAGES,
                    aw.fields.FieldType.FIELD_SECTION_PAGES
            ):
                return True

        current = current.previous_sibling

    return False


def is_inside_comment(node) -> bool:
    if node.get_ancestor(aw.NodeType.COMMENT):
        return True

    if isinstance(node, aw.CommentRangeStart) or isinstance(node, aw.CommentRangeEnd):
        return True

    return False


def truncate_to_complete_words(text, max_length=255):
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rstrip()
    if ' ' not in truncated:
        return text[:max_length]
    return truncated[:truncated.rfind(' ')]


def detect_language(text):
    arabic_count = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    english_count = sum(1 for char in text if 'A' <= char <= 'Z' or 'a' <= char <= 'z')

    if arabic_count > english_count:
        return "ar"
    elif english_count > arabic_count:
        return "en"
    elif arabic_count == english_count and arabic_count != 0:
        return "ar"
    else:
        return "ar"
