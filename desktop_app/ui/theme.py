"""Centralized UI theme values and shared stylesheets."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    bg_app: str = "#f4f6fb"
    bg_surface: str = "#ffffff"
    bg_surface_alt: str = "#f8fafc"
    border: str = "#e2e8f0"
    text_primary: str = "#0f172a"
    text_secondary: str = "#64748b"
    text_muted: str = "#94a3b8"
    brand: str = "#2563eb"
    brand_hover: str = "#1d4ed8"
    nav_bg: str = "#eef2f7"
    nav_active_bg: str = "#dbeafe"
    nav_active_text: str = "#1e3a8a"
    success: str = "#15803d"
    warning: str = "#b45309"


PALETTE = Palette()


def login_stylesheet() -> str:
    p = PALETTE
    return f"""
        QWidget:focus {{ outline: none; }}
        QAbstractItemView:focus {{ outline: none; }}
        QWidget {{ background: {p.bg_app}; font-size: 14px; color: {p.text_primary}; }}
        QLabel#title {{ font-size: 30px; font-weight: 700; color: {p.text_primary}; }}
        QLabel#subtitle {{ font-size: 14px; color: {p.text_secondary}; margin-bottom: 8px; }}
        QFrame#card {{ background: {p.bg_surface}; border-radius: 16px; border: 1px solid {p.border}; }}
        QLabel#cardTitle {{ font-size: 20px; font-weight: 600; color: {p.text_primary}; margin-bottom: 4px; }}
        QLabel#hint {{ color: {p.text_secondary}; font-size: 12px; }}
        QPushButton {{ border-radius: 10px; padding: 10px 14px; font-weight: 600; }}
        QPushButton#primary {{ background: {p.brand}; color: white; border: none; }}
        QPushButton#primary:hover {{ background: {p.brand_hover}; }}
        QPushButton#switch {{ color: {p.brand}; background: transparent; border: none; padding: 4px; }}
        QLineEdit {{ border: 1px solid {p.border}; border-radius: 10px; padding: 9px 11px; background: #fff; min-height: 18px; }}
        QLineEdit:focus {{ border: 1px solid {p.brand}; }}
    """


def main_window_stylesheet() -> str:
    p = PALETTE
    return f"""
        QWidget:focus {{ outline: none; }}
        QAbstractItemView:focus {{ outline: none; }}
        QMainWindow {{ background: {p.bg_app}; }}

        QFrame#topbar {{ background: {p.bg_surface}; border-bottom: 1px solid {p.border}; }}
        QLabel#appTitle {{ font-size: 24px; font-weight: 700; color: {p.text_primary}; }}
        QLabel#appSubtitle {{ font-size: 13px; color: {p.text_secondary}; }}
        QPushButton#topIconBtn {{
            background: transparent;
            border: 1px solid transparent;
            border-radius: 10px;
            min-width: 36px;
            min-height: 36px;
            font-size: 20px;
            color: #64748b;
            padding: 2px;
        }}
        QPushButton#topIconBtn:hover {{ background: {p.bg_surface_alt}; }}

        QFrame#sidebar {{
            background: {p.nav_bg};
            border-right: 1px solid {p.border};
            min-width: 240px;
            max-width: 240px;
        }}
        QListWidget#navList {{
            border: none;
            background: transparent;
            font-size: 15px;
            color: {p.text_secondary};
            outline: 0;
        }}
        QListWidget#navList::item {{
            height: 44px;
            padding: 0 12px;
            border-radius: 10px;
            margin: 4px 0;
        }}
        QListWidget#navList::item:selected {{
            background: {p.nav_active_bg};
            color: {p.nav_active_text};
            font-weight: 600;
        }}

        QFrame#contentCard {{
            background: {p.bg_surface};
            border: 1px solid {p.border};
            border-radius: 14px;
        }}
        QLabel#pageTitle {{ font-size: 20px; font-weight: 700; color: {p.text_primary}; }}
        QLabel#statusText {{ color: {p.warning}; font-size: 13px; }}
        QFrame#profileCard {{
            background: {p.bg_surface_alt};
            border: 1px solid {p.border};
            border-radius: 14px;
            padding: 10px;
        }}
        QLabel#profileCardTitle {{ font-size: 26px; font-weight: 700; color: #1f2937; }}
        QLabel#profileValue {{ font-size: 20px; color: #1f2937; }}

        QLineEdit {{
            border: 1px solid {p.border};
            border-radius: 10px;
            padding: 8px 10px;
            background: #fff;
            min-height: 16px;
            font-size: 14px;
        }}
        QLineEdit:focus {{ border: 1px solid {p.brand}; }}

        QPushButton {{
            background: {p.brand};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background: {p.brand_hover}; }}

        QListWidget#contentList {{
            border: 1px solid {p.border};
            border-radius: 10px;
            background: #fff;
            font-size: 14px;
            padding: 4px;
        }}
        QListWidget#contentList::item {{
            padding: 10px 12px;
            margin: 3px 0;
            border-radius: 8px;
            color: {p.text_primary};
        }}
        QListWidget#contentList::item:selected {{
            background: {p.bg_surface_alt};
            color: {p.text_primary};
        }}
    """
