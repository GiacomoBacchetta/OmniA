# Shared Utilities

Common utilities and models used across multiple services.

## Usage

Services can import shared utilities by copying this directory or mounting as a volume.

For Docker deployments:
```dockerfile
COPY ../shared /app/shared
```

Or use as a Python package:
```python
from shared.models import ArchiveItem
from shared.utils import generate_id, format_timestamp
```

## Contents

- `models/` - Common Pydantic models
- `utils/` - Utility functions
- `constants.py` - Shared constants
