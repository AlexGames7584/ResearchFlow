"""
ResearchFlow - Utility Functions and Project Manager
Handles file operations, project management, and asset copying.
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from models import ProjectData
from PyQt6.QtGui import QFont


def get_app_root() -> Path:
    """
    Get the application root directory (for data storage like projects/).
    Handles both normal Python execution and PyInstaller bundled .exe.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle (.exe)
        # sys.executable is the path to the .exe file
        return Path(sys.executable).parent.resolve()
    else:
        # Running as normal Python script
        return Path(__file__).parent.resolve()


def get_resource_path(relative_path: str) -> Path:
    """
    Get the path to a bundled resource file.
    Works both in normal Python and PyInstaller frozen environment.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS (onefile)
        # For onedir mode, resources are in the same folder as .exe
        base_path = getattr(sys, '_MEIPASS', Path(sys.executable).parent)
        return Path(base_path) / relative_path
    else:
        return Path(__file__).parent / relative_path


def get_projects_dir() -> Path:
    """Get the projects directory path."""
    return get_app_root() / "projects"


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def sanitize_project_name(name: str) -> str:
    """Convert project name to a valid directory name."""
    # Replace spaces with underscores and remove invalid characters
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    sanitized = name.replace(" ", "_")
    sanitized = "".join(c for c in sanitized if c in valid_chars)
    return sanitized or "Untitled_Project"


class ProjectManager:
    """
    Manages project lifecycle: creation, loading, saving.
    Ensures all data stays within the application folder.
    """
    
    def __init__(self):
        self.current_project_name: Optional[str] = None
        self.current_project_path: Optional[Path] = None
        self.project_data: Optional[ProjectData] = None
        
        # Ensure projects directory exists
        ensure_directory(get_projects_dir())
    
    @property
    def is_project_open(self) -> bool:
        return self.current_project_path is not None
    
    @property
    def assets_path(self) -> Optional[Path]:
        """Get the assets directory for the current project."""
        if self.current_project_path:
            return self.current_project_path / "assets"
        return None
    
    @property
    def papers_path(self) -> Optional[Path]:
        """Get the papers directory for the current project."""
        if self.assets_path:
            return self.assets_path / "papers"
        return None
    
    @property
    def images_path(self) -> Optional[Path]:
        """Get the images directory for the current project."""
        if self.assets_path:
            return self.assets_path / "images"
        return None
    
    def list_existing_projects(self) -> list[str]:
        """List all existing project names in the projects directory."""
        projects_dir = get_projects_dir()
        if not projects_dir.exists():
            return []
        
        projects = []
        for item in projects_dir.iterdir():
            if item.is_dir():
                # Check if it has a project_data.json file
                if (item / "project_data.json").exists():
                    projects.append(item.name)
        return sorted(projects)
    
    def create_project(self, name: str) -> bool:
        """
        Create a new project with the given name.
        Returns True if successful, False if project already exists.
        """
        sanitized_name = sanitize_project_name(name)
        project_path = get_projects_dir() / sanitized_name
        
        if project_path.exists():
            return False
        
        # Create project structure
        ensure_directory(project_path)
        ensure_directory(project_path / "assets" / "papers")
        ensure_directory(project_path / "assets" / "images")
        
        # Initialize empty project data
        self.current_project_name = sanitized_name
        self.current_project_path = project_path
        self.project_data = ProjectData()
        
        # Save initial project data
        self.save_project()
        
        return True
    
    def open_project(self, name: str) -> bool:
        """
        Open an existing project by name.
        Returns True if successful, False if project doesn't exist.
        """
        project_path = get_projects_dir() / name
        data_file = project_path / "project_data.json"
        
        if not data_file.exists():
            return False
        
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                json_content = f.read()
            
            self.project_data = ProjectData.from_json(json_content)
            self.current_project_name = name
            self.current_project_path = project_path
            
            # Ensure asset directories exist
            ensure_directory(self.papers_path)
            ensure_directory(self.images_path)
            
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading project: {e}")
            return False
    
    def save_project(self) -> bool:
        """
        Save the current project state to disk.
        Returns True if successful.
        """
        if not self.is_project_open or self.project_data is None:
            return False
        
        data_file = self.current_project_path / "project_data.json"
        
        try:
            json_content = self.project_data.to_json(indent=2)
            with open(data_file, "w", encoding="utf-8") as f:
                f.write(json_content)
            return True
        except IOError as e:
            print(f"Error saving project: {e}")
            return False
    
    def close_project(self) -> None:
        """Close the current project."""
        self.current_project_name = None
        self.current_project_path = None
        self.project_data = None
    
    def copy_markdown_to_assets(self, source_path: str) -> Optional[str]:
        """
        Copy a markdown file to the project's assets/papers directory.
        Returns the relative path to the copied file, or None if failed.
        """
        if not self.is_project_open or not self.papers_path:
            return None
        
        source = Path(source_path)
        if not source.exists() or not source.is_file():
            return None
        
        # Generate unique filename if needed
        dest_name = source.name
        dest_path = self.papers_path / dest_name
        
        # If file exists, add timestamp
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = source.stem
            suffix = source.suffix
            dest_name = f"{stem}_{timestamp}{suffix}"
            dest_path = self.papers_path / dest_name
        
        try:
            shutil.copy2(source, dest_path)
            # Return relative path from project root
            return f"assets/papers/{dest_name}"
        except IOError as e:
            print(f"Error copying file: {e}")
            return None
    
    def copy_image_to_assets(self, source_path: str) -> Optional[str]:
        """
        Copy an image file to the project's assets/images directory.
        Returns the relative path to the copied file, or None if failed.
        """
        if not self.is_project_open or not self.images_path:
            return None
        
        source = Path(source_path)
        if not source.exists() or not source.is_file():
            return None
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = source.stem
        suffix = source.suffix
        dest_name = f"{stem}_{timestamp}{suffix}"
        dest_path = self.images_path / dest_name
        
        try:
            shutil.copy2(source, dest_path)
            return f"assets/images/{dest_name}"
        except IOError as e:
            print(f"Error copying image: {e}")
            return None
    
    def save_clipboard_image(self, image_data: bytes, extension: str = ".png") -> Optional[str]:
        """
        Save clipboard image data to the project's assets/images directory.
        Returns the relative path to the saved file, or None if failed.
        """
        if not self.is_project_open or not self.images_path:
            return None
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"clipboard_{timestamp}{extension}"
        dest_path = self.images_path / filename
        
        try:
            with open(dest_path, "wb") as f:
                f.write(image_data)
            return f"assets/images/{filename}"
        except IOError as e:
            print(f"Error saving clipboard image: {e}")
            return None
    
    def get_absolute_asset_path(self, relative_path: str) -> Optional[Path]:
        """Convert a relative asset path to an absolute path."""
        if not self.is_project_open:
            return None
        return self.current_project_path / relative_path
    
    def delete_asset(self, relative_path: str) -> bool:
        """
        Delete an asset file (image or markdown).
        Returns True if successful or file doesn't exist.
        """
        if not self.is_project_open:
            return False
        
        abs_path = self.get_absolute_asset_path(relative_path)
        if abs_path and abs_path.exists():
            try:
                abs_path.unlink()
                return True
            except IOError as e:
                print(f"Error deleting asset: {e}")
                return False
        return True  # File doesn't exist, consider it success
    
    def get_referenced_assets(self) -> tuple[set[str], set[str]]:
        """
        Get all asset paths referenced by current project data.
        Returns (paper_paths, image_paths).
        """
        if not self.project_data:
            return set(), set()
        
        paper_paths = set()
        image_paths = set()
        
        for node in self.project_data.nodes:
            # Reference nodes have markdown files
            if node.type == "reference_paper" and node.metadata.relative_path_to_md:
                paper_paths.add(node.metadata.relative_path_to_md)
            
            # Snippets may have images
            for snippet in node.snippets:
                if snippet.type == "image" and snippet.content:
                    image_paths.add(snippet.content)
        
        return paper_paths, image_paths
    
    def cleanup_orphaned_assets(self) -> dict[str, int]:
        """
        Remove asset files that are no longer referenced by any node.
        Returns dict with counts: {'papers': n, 'images': m}
        """
        if not self.is_project_open:
            return {'papers': 0, 'images': 0}
        
        paper_refs, image_refs = self.get_referenced_assets()
        deleted = {'papers': 0, 'images': 0}
        
        # Clean orphaned papers
        if self.papers_path and self.papers_path.exists():
            for file in self.papers_path.iterdir():
                if file.is_file():
                    rel_path = f"assets/papers/{file.name}"
                    if rel_path not in paper_refs:
                        try:
                            file.unlink()
                            deleted['papers'] += 1
                        except IOError:
                            pass
        
        # Clean orphaned images
        if self.images_path and self.images_path.exists():
            for file in self.images_path.iterdir():
                if file.is_file():
                    rel_path = f"assets/images/{file.name}"
                    if rel_path not in image_refs:
                        try:
                            file.unlink()
                            deleted['images'] += 1
                        except IOError:
                            pass
        
        return deleted
    
    def validate_and_clean_data(self) -> dict[str, int]:
        """
        Validate project data and clean up any inconsistencies.
        Returns a dict with counts of removed items.
        
        1. Remove edges that reference non-existent nodes.
        2. Remove orphaned assets (files not referenced by any node).
        """
        if not self.is_project_open:
            return {}
            
        stats = {"edges_removed": 0, "assets_removed": 0}
        
        # 1. Validate Edges
        valid_node_ids = {n.id for n in self.project_data.nodes}
        valid_edges = []
        for edge in self.project_data.edges:
            if edge.source_id in valid_node_ids and edge.target_id in valid_node_ids:
                valid_edges.append(edge)
            else:
                stats["edges_removed"] += 1
        self.project_data.edges = valid_edges
        
        # 2. Cleanup Orphaned Assets
        removed_assets = self.cleanup_orphaned_assets()
        stats["assets_removed"] = sum(removed_assets.values())
        
        return stats
    
    def delete_project(self, name: str) -> bool:
        """
        Delete a project and all its contents.
        Returns True if successful.
        """
        project_path = get_projects_dir() / name
        
        if not project_path.exists():
            return False
        
        try:
            shutil.rmtree(project_path)
            return True
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False


class ModernTheme:
    """
    Apple/Notion-inspired design system.
    """
    
    # Color Palette
    BG_PRIMARY = "#FFFFFF"      # Pure white background
    BG_SECONDARY = "#F7F7F5"    # Unified secondary background (Sidebar/Canvas)
    BG_TERTIARY = "#EBEBEB"     # Hover states
    
    TEXT_PRIMARY = "#37352F"    # Notion Black
    TEXT_SECONDARY = "#787774"  # Notion Gray
    TEXT_INVERTED = "#FFFFFF"
    
    ACCENT_COLOR = "#2EAADC"    # Apple Blue
    ACCENT_HOVER = "#1B8FBf"
    
    BORDER_LIGHT = "#E0E0E0"
    BORDER_FOCUS = "rgba(46, 170, 220, 0.4)"
    
    SHADOW_LIGHT = "0px 1px 3px rgba(0, 0, 0, 0.05)"
    SHADOW_MEDIUM = "0px 4px 12px rgba(0, 0, 0, 0.08)"
    
    FONT_FAMILY = '"Segoe UI", "Microsoft YaHei", "Roboto", sans-serif'
    
    @staticmethod
    def get_ui_font(size: int = 10, bold: bool = False) -> QFont:
        """Get the standardized UI font with proper Chinese support."""
        # "Microsoft YaHei UI" is the safest bet for mixed English/Chinese on Windows
        font = QFont("Microsoft YaHei UI", size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return font

    @staticmethod
    def get_stylesheet() -> str:
        return f"""
        /* Global Reset */
        QWidget {{
            font-family: {ModernTheme.FONT_FAMILY};
            font-size: 14px;
            color: {ModernTheme.TEXT_PRIMARY};
            outline: none;
        }}
        
        /* Main Window & Dock */
        QMainWindow, QDockWidget {{
            background-color: {ModernTheme.BG_SECONDARY};
            border: none;
        }}
        
        QDockWidget::title {{
            background: {ModernTheme.BG_SECONDARY};
            padding: 12px;
            font-weight: bold;
            color: {ModernTheme.TEXT_PRIMARY};
        }}
        
        /* Graphics View (Canvas) */
        QGraphicsView {{
            border: none;
            background-color: {ModernTheme.BG_SECONDARY};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: white;
            border: 1px solid {ModernTheme.BORDER_LIGHT};
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {ModernTheme.BG_SECONDARY};
            border-color: #D0D0D0;
        }}
        QPushButton:pressed {{
            background-color: {ModernTheme.BG_TERTIARY};
            padding-top: 7px; /* Press effect */
            padding-bottom: 5px;
        }}
        
        /* Inputs */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: white;
            border: 1px solid {ModernTheme.BORDER_LIGHT};
            border-radius: 6px;
            padding: 8px;
            selection-background-color: {ModernTheme.ACCENT_COLOR};
            selection-color: white;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 1px solid {ModernTheme.ACCENT_COLOR};
        }}
        
        /* List Widget (TODOs) */
        QListWidget {{
            background-color: transparent;
            border: none;
            outline: none;
        }}
        QListWidget::item {{
            padding: 8px;
            border-radius: 4px;
            margin-bottom: 2px;
        }}
        QListWidget::item:hover {{
            background-color: rgba(0, 0, 0, 0.03);
        }}
        QListWidget::item:selected {{
            background-color: rgba(46, 170, 220, 0.1);
            color: {ModernTheme.TEXT_PRIMARY};
        }}
        
        /* Checkbox */
        QCheckBox {{
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #D0D0D0;
            background: white;
        }}
        QCheckBox::indicator:hover {{
            border-color: {ModernTheme.ACCENT_COLOR};
        }}
        QCheckBox::indicator:checked {{
            background-color: {ModernTheme.ACCENT_COLOR};
            border-color: {ModernTheme.ACCENT_COLOR};
        }}
        
        /* Context Menu */
        QMenu {{
            background-color: white;
            border: 1px solid {ModernTheme.BORDER_LIGHT};
            border-radius: 8px;
            padding: 6px;
        }}
        QMenu::item {{
            padding: 6px 24px 6px 12px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {ModernTheme.ACCENT_COLOR};
            color: white;
        }}
        
        /* Scrollbar */
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 10px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: #D0D0D0;
            min-height: 30px;
            border-radius: 5px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #A0A0A0;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 10px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: #D0D0D0;
            min-width: 30px;
            border-radius: 5px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: #A0A0A0;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* GroupBox */
        QGroupBox {{
            border: none;
            font-weight: bold;
            font-size: 12px;
            color: {ModernTheme.TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 20px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
        }}
        
        /* ToolTip */
        QToolTip {{
            border: 1px solid {ModernTheme.BORDER_LIGHT};
            background-color: white;
            color: {ModernTheme.TEXT_PRIMARY};
            padding: 4px;
            border-radius: 4px;
            opacity: 200;
        }}
        
        /* Sidebar Toggle Button */
        QPushButton#SidebarToggle {{
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid {ModernTheme.BORDER_LIGHT};
            border-left: none;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
            color: #555555;
            font-size: 24px;
            font-weight: bold;
            margin: 0px;
        }}
        QPushButton#SidebarToggle:hover {{
            background-color: {ModernTheme.BG_TERTIARY};
            color: {ModernTheme.ACCENT_COLOR};
        }}
        """


def extract_title_from_filename(filename: str) -> str:
    """Extract a readable title from a markdown filename."""
    # Remove extension
    name = Path(filename).stem
    # Replace underscores and hyphens with spaces
    name = name.replace("_", " ").replace("-", " ")
    # Title case
    return name.title()
