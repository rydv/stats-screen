import re

class Field:
    def __init__(self, name, value):
        self.name = name
        self.value = value.strip() if value else None
        self.operations = self._parse_operations()

    def _parse_operations(self):
        if not self.value:
            return []

        operations = []
        parts = re.split(r'(\|EXACT\||\|EXP\||\|FRMT\||\|OP\||\|PerfRef\||\|FM\||\|IGNORE\||\|PARTNAME\||\|FIELD_VALUE\|)', self.value)[1:]

        for i in range(0, len(parts), 2):
            identifier = parts[i]
            content = parts[i + 1] if i + 1 < len(parts) else ''
            operations.append((identifier, content))

        return operations
