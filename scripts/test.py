# scripts/diagnose_langchain.py
import langchain
import pkgutil
import importlib

print(f"LangChain version: {langchain.__version__}")
print(f"LangChain location: {langchain.__file__}")
print("\n" + "="*60)

# List all available modules in langchain
print("Available modules in langchain:")
for importer, modname, ispkg in pkgutil.iter_modules(langchain.__path__):
    print(f"  - {modname}")

print("\n" + "="*60)

# Try different import paths
print("Testing different import paths:")

import_paths = [
    "langchain.prompts",
    "langchain_core.prompts", 
    "langchain_community.prompts",
    "langchain.prompt_templates",
    "langchain.schema.prompts"
]

for path in import_paths:
    try:
        module = importlib.import_module(path)
        print(f"✅ {path} - SUCCESS")
    except ImportError as e:
        print(f"❌ {path} - FAILED: {e}")