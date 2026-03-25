import uuid

import django.db.models.deletion
import pgvector.django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference_documents', '0019_ragsourcedocument'),
    ]

    operations = [
        # --- RagSourceDocument: add description, description_embedding, is_embedded ---
        migrations.AddField(
            model_name='ragsourcedocument',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ragsourcedocument',
            name='description_embedding',
            field=pgvector.django.VectorField(dimensions=1536, null=True),
        ),
        migrations.AddField(
            model_name='ragsourcedocument',
            name='is_embedded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='ragsourcedocument',
            index=pgvector.django.HnswIndex(
                fields=['description_embedding'],
                m=12,
                ef_construction=120,
                name='rag_doc_desc_embedding_hnsw_idx',
                opclasses=['vector_cosine_ops'],
            ),
        ),
        # --- RagSourceDocumentChunk ---
        migrations.CreateModel(
            name='RagSourceDocumentChunk',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('embedding', pgvector.django.VectorField(dimensions=1536)),
                ('chunk_index', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'rag_source_document',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='chunks',
                        to='reference_documents.ragsourcedocument',
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name='ragsourcedocumentchunk',
            index=pgvector.django.HnswIndex(
                fields=['embedding'],
                m=12,
                ef_construction=120,
                name='rag_chunk_embedding_hnsw_idx',
                opclasses=['vector_cosine_ops'],
            ),
        ),
    ]
