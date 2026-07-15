import os
import re
from pathlib import Path
import uuid
import filetype
import unicodedata

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent.parent.parent


ALLOWED_FILE_TYPES = { 
                      "application/pdf",                                            
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                      "image/jpeg",                                                 
                      "image/png"  
                      }


MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 МБ


def detect_document_type(filename: str) -> tuple[str | None, dict | None]:
    """
    Определяет тип документа по паттернам в имени файла.
    Возвращает кортеж: (detected_type, warning_issue)
    """
    name_lower = unicodedata.normalize('NFC', filename.lower())

    if re.search(r'договор', name_lower):
        return 'contract', None
    
    if re.search(r'спецификаци', name_lower):
        return 'specification', None
    
    if re.search(r'сч[её]т', name_lower):
        return 'invoice', None
    
    if re.search(r'акт|упд', name_lower):
        return 'act', None
        
    # Если ни один паттерн не подошел
    warning = {
        "level": "warning",
        "message": f"Не удалось определить тип документа: «{filename}»"
    }
    return None, warning




async def file_type_error(file: UploadFile):
    
    if file.content_type not in ALLOWED_FILE_TYPES:
        return {
            "level": "error",
            "message": f"Недопустимый формат файла - {file.content_type}"
        }

    head_bytes = await file.read(2048)
    await file.seek(0) 
    
    kind = filetype.guess(head_bytes)
    if kind is None or kind.mime not in ALLOWED_FILE_TYPES:
        return {
            "level": "error",
            "message": f"Файл «{file.filename}» замаскирован. Реальное содержимое не является PDF/DOCX/JPG/PNG."
        }
    
    return None


async def file_size_error(file: UploadFile):
    
    content = await file.read()
    await file.seek(0)
    if len(content) > MAX_FILE_SIZE_BYTES:
        return {
            "level": "error",
            "message": f"Размер файла «{file.filename}» превышает допустимый объём - 20 МБ"
        }
    return None
    