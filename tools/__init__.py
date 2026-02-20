"""Module tools pour GoldArmyArgent."""

__all__ = []

# Web searcher sera importé dynamiquement si disponible
try:
    from tools.web_searcher import web_searcher
    __all__.append("web_searcher")
except ImportError:
    web_searcher = None
