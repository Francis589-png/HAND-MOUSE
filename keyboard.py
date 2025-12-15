from typing import List, Optional, Tuple


class OnScreenKeyboard:
    """Simple multi-page on-screen keyboard.

    Pages are defined as lists of rows (each row is a list of key labels).
    """
    def __init__(self):
        self.pages: List[List[List[str]]] = []
        self.current = 0
        self._build_pages()

    def _build_pages(self):
        # Page 0: letters
        self.pages.append([
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
            [("SPACE", 4), ("BACK", 1), ("SHIFT", 1), ("CAPS", 1), ("PREV", 1), ("NEXT", 1), ("ENTER", 2)]
        ])
        # Page 1: numbers & basic symbols
        self.pages.append([
            list("1234567890"),
            list("-=/.,;:'\""),
            list("()[]{}"),
            [("SPACE", 4), ("BACK", 1), ("SHIFT", 1), ("CAPS", 1), ("PREV", 1), ("NEXT", 1), ("ENTER", 2)]
        ])

    def toggle_shift(self):
        # toggle transient shift (if locked, unlock)
        if getattr(self, 'shift_locked', False):
            self.shift = False
            self.shift_locked = False
        else:
            self.shift = not getattr(self, 'shift', False)

    def set_shift_locked(self, lock: bool):
        self.shift = lock
        self.shift_locked = lock

    def toggle_caps(self):
        self.caps = not getattr(self, 'caps', False)

    def get_display_label(self, label: str) -> str:
        """Return label as displayed to the user (respect shift/caps for letters)."""
        if len(label) == 1 and label.isalpha():
            shift = getattr(self, 'shift', False)
            caps = getattr(self, 'caps', False)
            if shift ^ caps:
                return label.upper()
            else:
                return label.lower()
        return label

    def get_applied_char(self, label: str):
        """Return ('char', s) or ('action', label) depending on key.

        Letters respect shift/caps; special keys are returned as actions.
        """
        specials = {"SPACE", "BACK", "SHIFT", "CAPS", "NEXT", "PREV", "ENTER"}
        if label in specials:
            return 'action', label
        if len(label) == 1:
            # letter or symbol
            if label.isalpha():
                shift = getattr(self, 'shift', False)
                caps = getattr(self, 'caps', False)
                ch = label.upper() if (shift ^ caps) else label.lower()
                return 'char', ch
            return 'char', label
        return 'action', label

    def next_page(self):
        self.current = (self.current + 1) % len(self.pages)

    def prev_page(self):
        self.current = (self.current - 1) % len(self.pages)

    def get_page(self) -> List[List[str]]:
        return self.pages[self.current]

    def key_at(self, x_norm: float, y_norm: float, width: int, height: int) -> Optional[Tuple[str,int,int]]:
        """Return (key_label, row_idx, col_idx) for normalized coords, or None."""
        if x_norm is None or y_norm is None:
            return None
        page = self.get_page()
        row_h = height / len(page)
        row_idx = int(y_norm * len(page))
        row_idx = max(0, min(len(page) - 1, row_idx))
        row = page[row_idx]
        # support weighted keys in a row: keys can be string or (label, weight)
        weights = [ (k[1] if isinstance(k, tuple) else 1) for k in row ]
        total = sum(weights)
        x = x_norm * width
        acc = 0.0
        for col_idx, wgt in enumerate(weights):
            cell_w = (wgt / total) * width
            if acc <= x < acc + cell_w or col_idx == len(weights)-1:
                entry = row[col_idx]
                label = entry[0] if isinstance(entry, tuple) else entry
                return label, row_idx, col_idx
            acc += cell_w
        return None
