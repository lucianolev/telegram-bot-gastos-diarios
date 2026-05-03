from abc import ABC, abstractmethod


class Reloj(ABC):
    @abstractmethod
    def ahora(self):
        raise NotImplementedError
