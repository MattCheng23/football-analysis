from pathlib import Path
def test_package_exists():
    root = Path(__file__).resolve().parent.parent
    assert (root/'00_MANIFEST.json').exists()
