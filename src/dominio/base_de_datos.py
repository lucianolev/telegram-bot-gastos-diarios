from abc import ABC, abstractmethod


class BaseDeDatos(ABC):
    @abstractmethod
    def agregar_fila(self, rango, valores):
        raise NotImplementedError

    @abstractmethod
    def leer_filas(self, rango):
        raise NotImplementedError

    @abstractmethod
    def limpiar_rango(self, rango):
        raise NotImplementedError
