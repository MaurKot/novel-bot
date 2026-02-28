"""
Инициализация всех сценариев
"""
from . import prologue
from . import chapter1
from . import chapter2
from . import endings

def load_all_scenarios():
    """Загрузить все сценарии в систему"""
    prologue.register_scenes()
    chapter1.register_scenes()
    chapter2.register_scenes()
    endings.register_scenes()