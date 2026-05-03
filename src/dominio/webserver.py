from abc import ABC, abstractmethod


class WebServer(ABC):
    @abstractmethod
    def manejar(self, request):
        raise NotImplementedError
