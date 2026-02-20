
import sys
try:
    import duckduckgo_search
    print(f"Version: {duckduckgo_search.__version__}")
    print(f"Dir: {dir(duckduckgo_search)}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
