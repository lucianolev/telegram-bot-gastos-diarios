from abc import ABC, abstractmethod


class AsistentePersonal(ABC):
    @abstractmethod
    def construir_mensaje(self, carga_util):
        raise NotImplementedError

    @abstractmethod
    def enviar_mensaje(self, chat_id, texto):
        raise NotImplementedError

    @abstractmethod
    def responder_a(self, mensaje, texto):
        raise NotImplementedError
