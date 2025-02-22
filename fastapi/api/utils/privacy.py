import os
import json

from dotenv import load_dotenv

load_dotenv()
HASHED_TEAMS = json.loads(os.getenv("HASHED_TEAMS", "{}"))

def get_team_from_hash(hash_value: str) -> str:
    return HASHED_TEAMS.get(hash_value, None)