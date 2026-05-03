from dataclasses import dataclass


@dataclass(frozen=True)
class Mensaje:
    chat_id: int
    usuario: str
    texto: str
    mensaje_id: int | None = None

    def texto_normalizado(self):
        return self.texto.strip()
