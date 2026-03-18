from abc import ABC, abstractmethod


class GenerateKakaoOAuthUrlPort(ABC):

    @abstractmethod
    def generate(self) -> str:
        pass
