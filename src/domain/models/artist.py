from dataclasses import dataclass

@dataclass
class Artist:
    id: str
    name: str

    def __str__(self) -> str:
        return f"Artist: {self.name}, id: {self.id}"