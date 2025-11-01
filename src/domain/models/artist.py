from dataclasses import dataclass

@dataclass
class Artist:
    id: str
    name: str

    def __str__(self) -> str:
        return f"id: {self.id}\n" + \
               f"name: {self.name}\n"