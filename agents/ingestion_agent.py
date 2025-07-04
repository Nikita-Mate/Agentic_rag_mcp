import tempfile
import os
import PyPDF2
import docx
from PIL import Image
import pytesseract
from langchain.text_splitter import RecursiveCharacterTextSplitter
class IngestionAgent:
    def process_document(self, uploaded_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name        
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if file_extension == '.pdf':
                text = self._extract_pdf_text(tmp_file_path)
            elif file_extension in ['.docx', '.doc']:
                text = self._extract_docx_text(tmp_file_path)
            elif file_extension == '.txt':
                text = self._extract_txt_text(tmp_file_path)
            elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                text = self._extract_image_text(tmp_file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            chunks = splitter.split_text(text)            
        except Exception as e:
            chunks = []
        finally:
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                pass        
        return chunks    
    def _extract_pdf_text(self, file_path):
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            return ""    
    def _extract_docx_text(self, file_path):
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return ""    
    def _extract_txt_text(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
            return text
        except Exception as e:
            return ""    
    def _extract_image_text(self, file_path):
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting image text: {str(e)}")
            return ""