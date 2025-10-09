import docx
import fitz  # PyMuPDF
import magic


def extract_text_from_file(file_path):
    # Detect file type using python-magic (MIME type detection)
    file_type = magic.Magic(mime=True).from_file(file_path)

    # Handle PDF files
    if file_type == 'application/pdf':
        return extract_text_from_pdf(file_path)

    # Handle DOCX files
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)

    # Handle DOC files (older MS Word format)
    # elif file_path.endswith('.doc'):
    #     return extract_text_from_doc(file_path)

    # Handle plain text files
    elif file_type == 'text/plain' or file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)

    # If unsupported type
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def extract_text_from_pdf(file_path):
    # Extract text from a PDF file using PyMuPDF (fitz)
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(file_path):
    # Extract text from a DOCX file using python-docx
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


# def extract_text_from_doc(file_path):
#     Extract text from a DOC file using textract
# text = textract.process(file_path).decode('utf-8')  # Ensure decoding to string
# return text


def extract_text_from_txt(file_path):
    # Extract text from a plain text file
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text
