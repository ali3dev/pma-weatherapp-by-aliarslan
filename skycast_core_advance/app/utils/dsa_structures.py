class Stack:
    def __init__(self):
        self.items = []
    def push(self, item):
        self.items.append(item)
    def pop(self):
        return self.items.pop() if self.items else None
    def is_empty(self):
        return len(self.items) == 0


def sort_history_by_temp(records):
    """Return records sorted by temperature ascending."""
    try:
        return sorted(records, key=lambda r: getattr(r, 'temp', getattr(r, 'temperature', 0)))
    except Exception:
        return records
