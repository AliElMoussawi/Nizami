"""
Tests for chat attachments: sha256 dedupe, summary cache, soft-wait branching, idempotent final answer.
"""

import uuid
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from src.chats.attachment_flow import _infer_intent,_poll_extraction_statuses
from src.chats.models import Chat, Message, PendingDocIntent
from src.uploads.models import File, FileExtraction, FileSummary
from src.users.models import User
from src.prompts.enums import PendingDocIntentIntentType, PendingDocIntentStatus


@override_settings(AWS_STORAGE_BUCKET_NAME=None)  # Skip S3 in init for dedupe test
class UploadInitDedupeTest(TestCase):
    """SHA256 dedupe: init with same (tenant, sha256) returns file_id and reused: true."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_init_with_sha256_reuses_existing_file(self):
        sha = "a" * 64
        existing = File.objects.create(
            id=uuid.uuid4(),
            tenant=self.user,
            original_filename="doc.pdf",
            mime_type="application/pdf",
            size_bytes=100,
            sha256=sha,
            s3_bucket="test",
            s3_key_raw="tenants/1/files/x/raw/doc.pdf",
        )
        response = self.client.post(
            "/api/v1/attachments/init",
            {
                "file_name": "doc.pdf",
                "file_size": 100,
                "mime_type": "application/pdf",
                "sha256": sha,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get("reused"))
        self.assertEqual(str(existing.id), data["file_id"])
        self.assertNotIn("upload_url", data)


class InferIntentTest(TestCase):
    def test_infer_summary(self):
        self.assertEqual(
            _infer_intent(text="Please summarize this document"),
            PendingDocIntent.IntentType.SUMMARY,
        )
        self.assertEqual(
            _infer_intent(text="Give me an overview"),
            PendingDocIntent.IntentType.SUMMARY,
        )

    def test_infer_qa(self):
        self.assertEqual(
            _infer_intent(text="What is the deadline in this contract?"),
            PendingDocIntent.IntentType.QA,
        )


class SoftWaitBranchingTest(TestCase):
    """Soft-wait: _poll_extraction_statuses returns READY / PREVIEW_READY / PROCESSING."""

    def setUp(self):
        self.user = User.objects.create_user(email="u@t.com", password="pw")
        self.file1 = File.objects.create(
            id=uuid.uuid4(),
            tenant=self.user,
            original_filename="a.pdf",
            mime_type="application/pdf",
            size_bytes=10,
            sha256="b" * 64,
        )
        self.file2 = File.objects.create(
            id=uuid.uuid4(),
            tenant=self.user,
            original_filename="b.pdf",
            mime_type="application/pdf",
            size_bytes=10,
            sha256="c" * 64,
        )

    def test_poll_all_ready(self):
        FileExtraction.objects.create(
            file=self.file1,
            status=FileExtraction.Status.READY,
        )
        FileExtraction.objects.create(
            file=self.file2,
            status=FileExtraction.Status.READY,
        )
        status, _ = _poll_extraction_statuses(
            file_ids=[str(self.file1.id), str(self.file2.id)],
            user_id=self.user.id,
        )
        self.assertEqual(status, "READY")

    def test_poll_any_preview_ready(self):
        FileExtraction.objects.create(
            file=self.file1,
            status=FileExtraction.Status.PREVIEW_READY,
        )
        status, _ = _poll_extraction_statuses(
            file_ids=[str(self.file1.id), str(self.file2.id)],
            user_id=self.user.id,
        )
        self.assertEqual(status, "PREVIEW_READY")

    def test_poll_processing(self):
        FileExtraction.objects.create(
            file=self.file1,
            status=FileExtraction.Status.EXTRACTING,
        )
        status, _ = _poll_extraction_statuses(
            file_ids=[str(self.file1.id), str(self.file2.id)],
            user_id=self.user.id,
        )
        self.assertIn(status, ("PROCESSING", "PREVIEW_READY"))


class SummaryCacheTest(TestCase):
    """When FileSummary exists for (tenant, file, type, version), generate_final_answer uses it (no LLM)."""

    def setUp(self):
        self.user = User.objects.create_user(email="u2@t.com", password="pw")
        self.chat = Chat.objects.create(user=self.user, title="Test")
        self.user_msg = Message.objects.create(
            chat=self.chat,
            role="user",
            text="Summarize this",
            uuid=uuid.uuid4(),
        )
        self.file = File.objects.create(
            id=uuid.uuid4(),
            tenant=self.user,
            original_filename="x.pdf",
            mime_type="application/pdf",
            size_bytes=10,
            sha256="d" * 64,
        )
        FileExtraction.objects.create(
            file=self.file,
            status=FileExtraction.Status.READY,
            full_text_s3_key="tenants/1/files/x/extracted/full.txt",
        )
        self.file.s3_bucket = "test"
        self.file.save()

    @patch("src.uploads.final_answer.download_text_from_s3")
    @patch("src.uploads.final_answer.create_llm")
    def test_summary_intent_uses_cache(self, mock_llm, mock_download):
        mock_download.return_value = "Some document text."
        FileSummary.objects.create(
            tenant=self.user,
            file=self.file,
            summary_type="general",
            prompt_version="1",
            summary_text="Cached summary here.",
        )
        intent = PendingDocIntent.objects.create(
            tenant=self.user,
            conversation=self.chat,
            user_message=self.user_msg,
            file_ids=[str(self.file.id)],
            user_question="Summarize this",
            intent_type=PendingDocIntentIntentType.SUMMARY,
            status=PendingDocIntentStatus.PENDING,
        )
        from src.uploads.final_answer import run_generate_final_answer

        run_generate_final_answer(pending_intent_id=intent.id)
        mock_llm.assert_not_called()
        intent.refresh_from_db()
        self.assertEqual(intent.status, PendingDocIntentStatus.DONE)
        assistant = Message.objects.filter(chat=self.chat, role="ai", parent=self.user_msg).first()
        self.assertIsNotNone(assistant)
        self.assertIn("Cached summary here", assistant.text)


class IdempotentFinalAnswerTest(TestCase):
    """generate_final_answer called twice for same intent: only one assistant message, intent DONE once."""

    def setUp(self):
        self.user = User.objects.create_user(email="u3@t.com", password="pw")
        self.chat = Chat.objects.create(user=self.user, title="Test")
        self.user_msg = Message.objects.create(
            chat=self.chat,
            role="user",
            text="What is this?",
            uuid=uuid.uuid4(),
        )
        self.file = File.objects.create(
            id=uuid.uuid4(),
            tenant=self.user,
            original_filename="y.pdf",
            mime_type="application/pdf",
            size_bytes=10,
            sha256="e" * 64,
            s3_bucket="test",
        )
        FileExtraction.objects.create(
            file=self.file,
            status=FileExtraction.Status.READY,
            full_text_s3_key="tenants/1/files/y/extracted/full.txt",
        )

    @patch("src.uploads.final_answer.download_text_from_s3")
    @patch("src.uploads.final_answer.create_llm")
    def test_double_call_posts_once(self, mock_llm, mock_download):
        mock_download.return_value = "Document content."
        from langchain_core.messages import AIMessage
        mock_llm.return_value.invoke.return_value = AIMessage(content="The answer.")
        intent = PendingDocIntent.objects.create(
            tenant=self.user,
            conversation=self.chat,
            user_message=self.user_msg,
            file_ids=[str(self.file.id)],
            user_question="What is this?",
            intent_type=PendingDocIntent.IntentType.QA,
            status=PendingDocIntentStatus.PENDING,
        )
        from src.uploads.final_answer import run_generate_final_answer

        run_generate_final_answer(pending_intent_id=intent.id)
        run_generate_final_answer(pending_intent_id=intent.id)
        count = Message.objects.filter(chat=self.chat, role="ai", parent=self.user_msg).count()
        self.assertEqual(count, 1)
        intent.refresh_from_db()
        self.assertEqual(intent.status, PendingDocIntentStatus.DONE)
