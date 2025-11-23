import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.common.document_loaders import TextLoader
from src.reference_documents.models import ReferenceDocument, ReferenceDocumentPart
from src.reference_documents.utils import generate_description_for_text
from src.settings import vectorstore, embeddings


def clean_up_reference_document_parts(reference_document: ReferenceDocument):
    parts = ReferenceDocumentPart.objects.filter(reference_document=reference_document).values('id')
    ids = list(map(lambda x: x['id'], parts))
    if len(ids) == 0:
        return

    vectorstore.delete(ids)
    ReferenceDocumentPart.objects.filter(reference_document=reference_document).delete()


def analyze_reference_document(reference_document_id):
    try:
        reference_document = ReferenceDocument.objects.get(id=reference_document_id)
    except ReferenceDocument.DoesNotExist:
        return

    clean_up_reference_document_parts(reference_document)

    reference_document.status = 'processing'
    reference_document.save()
    ids = []

    try:
        text_loader = TextLoader(reference_document.file.path)
        documents = text_loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
        all_splits = text_splitter.split_documents(documents)

        for split in all_splits:
            split.metadata['reference_document_id'] = reference_document_id
            split.metadata['language'] = reference_document.language.lower()
            ids.append(str(uuid.uuid4()))

        batch_size = 100
        for i in range(0, len(all_splits), batch_size):
            batch = all_splits[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            output_ids = vectorstore.add_documents(documents=batch, ids=batch_ids)

            parts = [ReferenceDocumentPart(id=_id, reference_document=reference_document) for _id in output_ids]
            ReferenceDocumentPart.objects.bulk_create(parts)

        reference_document.status = 'processed'

        if reference_document.description in [None, '']:
            reference_document.description = generate_description_for_text(
                '\n'.join(doc.page_content for doc in documents), reference_document.language)
            reference_document.description_embedding = embeddings.embed_query(reference_document.description)

        reference_document.save()

        return f"Reference Document {reference_document_id} processed successfully!"
    except:
        clean_up_reference_document_parts(reference_document)

        reference_document.status = 'failed'
        reference_document.save()

        raise
