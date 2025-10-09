import json
import os
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from enum import Enum

import aspose.words as aw
import math
from django.core.files.base import ContentFile
from django.db import models, transaction
from langchain_core.messages import SystemMessage, HumanMessage

from src.chats.models import Message, MessageFile, MessageLog
from src.chats.utils import get_random_unclear_request_message, aspose_word_replace_json, create_document_review_llm, \
    create_legal_advice_llm, extract_used_styles, extract_doc_data
from src.common.utils import chunk_array
from src.prompts.enums import PromptType
from src.prompts.utils import get_prompt_value_by_name


class UpdateCurrentFile:
    def __init__(self, chat_id, text, user_message: Message, message_files, user):
        self.user_message = user_message
        self.chat_id = chat_id
        self.text = text
        self.message_files = message_files
        self.user = user

    @transaction.atomic
    def execute(self):
        document_review_llm = create_document_review_llm()
        legal_advice_llm = create_legal_advice_llm()

        template = get_prompt_value_by_name(PromptType.REVIEW_DOCX)

        template_answer = get_prompt_value_by_name(PromptType.REPHRASE_REVIEW_DOCX)

        def process_chunk(single_chunk):

            chunk_json = json.dumps(single_chunk)

            user_prompt = f"""
                ##USER_PROMPT
                {self.user_message.text}

                ###JSON_LEGAL_DOCUMENT
                {chunk_json}
            """

            messages = [
                SystemMessage(
                    content=template.format(
                        styles=json.dumps(styles_json),
                        styles_names=json.dumps([style['name'] for style in styles_json]),
                    ),
                ),
                HumanMessage(content=user_prompt)
            ]

            answer = document_review_llm.invoke(messages).content

            if answer.startswith('```json') and answer.endswith('```'):
                answer = answer[7:-3].strip()

            try:

                return json.loads(answer)
            except json.decoder.JSONDecodeError as e:
                print(answer)
                raise e

        system_message = None
        for message_file in self.message_files:
            file: models.FileField = message_file.file

            doc = aw.Document(file.path)

            styles_json = extract_used_styles(doc)
            json_data = extract_doc_data(doc)

            answers = []

            if len(answers) <= 0:
                max_objects_in_chunk = 400
                count_of_objects = len(json_data)
                count_of_chunks = math.ceil(count_of_objects / max_objects_in_chunk)

                chunks = chunk_array(json_data, count_of_objects // count_of_chunks)

                with ThreadPoolExecutor(max_workers=4) as executor:
                    results = executor.map(process_chunk, chunks)
                    for result in results:
                        answers += result

                MessageLog.logs_objects.create(
                    message=self.user_message,
                    response=answers,
                )

                if len(answers) == 0:
                    return Message.objects.create(
                        chat_id=self.chat_id,
                        parent=self.user_message,
                        text=get_random_unclear_request_message(),
                        role='ai',
                        uuid=uuid.uuid4(),
                    )

            output_file = aspose_word_replace_json(file.path, json_data, answers)

            if system_message is None:
                modifications = []
                for i, record in enumerate(answers):
                    if 'new' not in record:
                        continue

                    old = record.get('old', '').strip()
                    new = record.get('new', '').strip()

                    # not changed
                    if old == new:
                        continue

                    reason = record.get('reason', '').strip()

                    modifications.append({
                        'old': old,
                        'new': new,
                        'reason': reason,
                    })

                messages = [
                    SystemMessage(content=template_answer.format(response=modifications,
                                                                 count_of_modifications=len(modifications),
                                                                 user_query=self.user_message.text)),
                    #         HumanMessage(content=answer)
                ]

                answer_to_user = legal_advice_llm.invoke(messages).content

                system_message = Message.objects.create(
                    chat_id=self.chat_id,
                    parent=self.user_message,
                    text=answer_to_user,
                    role='ai',
                    uuid=uuid.uuid4(),
                )

            file_name = os.path.splitext(message_file.file_name)[0]
            new_file_name = file_name + '.' + message_file.extension if 'revised' in file_name else file_name + '-revised.' + message_file.extension

            MessageFile.objects.create(
                user=self.user,
                file=ContentFile(
                    name=new_file_name,
                    content=output_file.getvalue(),
                ),
                message=system_message,
            )

        if system_message is not None:
            system_message.refresh_from_db(fields=['messageFiles'])

        return system_message


class Answer(Enum):
    Yes = 1
    No = 2
    Other = 3


class UpdatePreviousFile:
    def __init__(self, chat_id, text, validated_data, user):
        self.chat_id = chat_id
        self.text = text
        self.user = user
        self.previous_message = None
        self.validated_data = validated_data

    def load_previous_message(self):
        self.previous_message = (Message.objects.filter(chat_id=self.chat_id)
                                 .order_by('-created_at')
                                 .prefetch_related('messageFiles')
                                 .first())

    def is_asking_for_additional_updates_to_file(self):
        self.load_previous_message()

        if self.previous_message is None:
            return False

        if self.previous_message.messageFiles is None or len(self.previous_message.messageFiles.all()) <= 0:
            return False

        llm = create_legal_advice_llm()

        system_message = get_prompt_value_by_name(PromptType.UPDATING_FILE_FROM_PREVIOUS_MESSAGES)

        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=self.text),
        ]

        response = llm.invoke(messages)

        answer = response.content

        answers = {
            'yes': Answer.Yes,
            'no': Answer.No,
            'other': Answer.Other,
        }

        return answers.get(answer.lower(), Answer.Other)

    def execute(self):
        user_message = Message.objects.filter(uuid=self.validated_data['uuid']).first()
        if user_message is None:
            user_message = Message.objects.create(
                role='user',
                chat_id=self.chat_id,
                text=self.text,
                uuid=self.validated_data['uuid'],
            )

        return UpdateCurrentFile(
            chat_id=self.chat_id,
            text=self.text,
            user=self.user,
            user_message=user_message,
            message_files=self.previous_message.messageFiles.all(),
        ).execute()
