COLORS = {
    "bg": "#F8F9FA",
    "surface": "#FFFFFF",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "text": "#111827",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "success": "#16A34A",
    "danger": "#DC2626",
    "warning": "#F59E0B",
}

APP_STYLESHEET = f"""
QMainWindow, QWidget#appRoot {{
    background: {COLORS['bg']};
}}
QWidget {{
    color: {COLORS['text']};
    font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
    font-size: 14px;
}}
QLabel {{
    background: transparent;
}}
QFrame#surfaceCard {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}
QPushButton#primaryButton {{
    background: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 600;
}}
QPushButton#primaryButton:hover {{ background: {COLORS['primary_hover']}; }}
QPushButton#secondaryButton {{
    background: #F3F4F6;
    color: {COLORS['text']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 8px 14px;
}}
QPushButton {{
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
}}
QLineEdit, QComboBox {{
    background: white;
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 8px 10px;
}}
QListWidget {{
    background: white;
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
"""
