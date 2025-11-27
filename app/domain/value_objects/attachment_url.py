
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class AttachmentType(str, Enum):
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"


@dataclass(frozen=True)
class AttachmentUrl:

    url: str
    attachment_type: AttachmentType
    
    ALLOWED_EXTENSIONS = {
        AttachmentType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        AttachmentType.AUDIO: ['.mp3', '.m4a', '.wav', '.ogg'],
        AttachmentType.VIDEO: ['.mp4', '.mov', '.avi', '.webm']
    }
    
    def __post_init__(self):
        if not isinstance(self.url, str):
            raise ValueError(f"URL debe ser un string, recibido: {type(self.url)}")
        
        if not isinstance(self.attachment_type, AttachmentType):
            raise ValueError(
                f"attachment_type debe ser AttachmentType, recibido: {type(self.attachment_type)}"
            )
        
        if not self.url.strip():
            raise ValueError("La URL del archivo adjunto no puede estar vacía")
        
        self._validate_url_format()
        
        self._validate_file_extension()
    
    def _validate_url_format(self) -> None:

        try:
            parsed = urlparse(self.url)
            
            if not parsed.scheme:
                raise ValueError(f"URL inválida: falta el scheme (http/https) en {self.url}")
            
            if not parsed.netloc:
                raise ValueError(f"URL inválida: falta el dominio en {self.url}")
            
            if parsed.scheme not in ['http', 'https']:
                raise ValueError(
                    f"URL debe usar HTTP o HTTPS, recibido: {parsed.scheme}"
                )
        except Exception as e:
            raise ValueError(f"Formato de URL inválido: {self.url}") from e
    
    def _validate_file_extension(self) -> None:

        parsed = urlparse(self.url)
        path = parsed.path.lower()
        
        extension = None
        for ext in self.ALLOWED_EXTENSIONS[self.attachment_type]:
            if path.endswith(ext):
                extension = ext
                break
        
        if not extension:
            allowed = ', '.join(self.ALLOWED_EXTENSIONS[self.attachment_type])
            raise ValueError(
                f"Extensión de archivo no permitida para {self.attachment_type.value}. "
                f"Extensiones permitidas: {allowed}"
            )
    
    @classmethod
    def create_image(cls, url: str) -> 'AttachmentUrl':

        return cls(url=url, attachment_type=AttachmentType.IMAGE)
    
    @classmethod
    def create_audio(cls, url: str) -> 'AttachmentUrl':

        return cls(url=url, attachment_type=AttachmentType.AUDIO)
    
    @classmethod
    def create_video(cls, url: str) -> 'AttachmentUrl':

        return cls(url=url, attachment_type=AttachmentType.VIDEO)
    
    def get_url(self) -> str:

        return self.url
    
    def get_type(self) -> AttachmentType:

        return self.attachment_type
    
    def __str__(self) -> str:
        return self.url
    
    def __repr__(self) -> str:
        return f"AttachmentUrl(url='{self.url}', type={self.attachment_type.value})"