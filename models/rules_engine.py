from pydantic import BaseModel

class GameRules(BaseModel):
    criticals: bool = False
    max_rounds: int = 20
