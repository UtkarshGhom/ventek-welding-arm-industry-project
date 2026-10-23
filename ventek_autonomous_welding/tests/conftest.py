import os
import json
import pytest

PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMAS_DIR = os.path.join(PKG_ROOT, "integration", "schemas")
EXAMPLES_DIR = os.path.join(PKG_ROOT, "integration", "examples")

@pytest.fixture
def load_schema():
    def _loader(name):
        schema_path = os.path.join(SCHEMAS_DIR, f"{name}.schema.json")
        with open(schema_path, "r") as f:
            return json.load(f)
    return _loader

@pytest.fixture
def load_example():
    def _loader(name):
        example_path = os.path.join(EXAMPLES_DIR, f"{name}.json")
        with open(example_path, "r") as f:
            return json.load(f)
    return _loader
