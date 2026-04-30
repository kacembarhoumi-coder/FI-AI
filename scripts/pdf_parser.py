import fitz
def open_pdf(path):
    doc = fitz.open(path)
    return doc

def extract_pages(doc):
    pages_text = []
    for page in doc:
        text = page.get_text()
        pages_text.append(text)
    return pages_text

def clean_text(pages_text):
    full_text = "\n".join(pages_text)
    
    # Remove extra blank lines
    lines = [line.strip() for line in full_text.splitlines()]
    lines = [line for line in lines if line]  # remove empty lines
    
    return "\n".join(lines)

def extract_pdf(path):
    doc = open_pdf(path)
    pages = extract_pages(doc)
    text = clean_text(pages)
    return text

