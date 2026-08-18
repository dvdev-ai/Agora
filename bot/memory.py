from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict, List


class ConversationMemory:
    """Память диалога в оперативке: хватает для одного процесса бота."""

    def __init__(self, limit: int = 20) -> None:
        self.limit = max(2, limit)
        self._store: Dict[int, Deque[dict]] = defaultdict(deque)
        self._lock = Lock()

    def get(self, user_id: int) -> List[dict]:
        with self._lock:
            return list(self._store[user_id])

    def add(self, user_id: int, role: str, content: str) -> None:
        with self._lock:
            history = self._store[user_id]
            history.append({"role": role, "content": content})
            while len(history) > self.limit:
                history.popleft()

    def clear(self, user_id: int) -> None:
        with self._lock:
            self._store.pop(user_id, None)
