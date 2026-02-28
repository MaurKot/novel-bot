from .commands import router as commands_router
from .callbacks import router as callbacks_router
from .game import router as game_router

__all__ = ["commands_router", "callbacks_router", "game_router"]