# ResearchFlow

<p align="center">
  <img src="icon.ico" alt="ResearchFlow Logo" width="80" height="80">
</p>

<p align="center">
  <strong>The Ultimate Academic Research Workflow Manager</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.9.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/PyQt6-6.0+-purple.svg" alt="PyQt6">
</p>

<p align="center">
  <a href="https://github.com/thefamer/ResearchFlow/releases"><strong>📥 Download v3.9.0 .exe from Releases</strong></a>
</p>

> **💡 Just want it to work?** v3.9.0 **portable standalone .exe** is available in [Releases](https://github.com/thefamer/ResearchFlow/releases) – download and run, no Python required!

---

ResearchFlow is a portable, aesthetically pleasing desktop application designed for academic researchers to manage workflows, literature, and ideas. Built with a focus on modern design and fluid user experience, it features a Notion-like interface, rich interactions, and powerful project management tools.

---

## ✨ What's New in V3.9.0

### 🔄 Comprehensive Undo/Redo (Ctrl+Z / Ctrl+Y)
- **Full Coverage**: Every action is now undoable! From canvas movements, node/group/edge creation and deletion, to sidebar changes (Description, TODOs, Tags).
- **Persistent History**: Your undo history is automatically saved per project and restored when you reopen it.
- **Deep States**: Supports 100 steps of history for worry-free experimentation.

### 📍 Waypoint Nodes (Connection Bending)
- **Path Control**: Drag the "Waypoint" item from the palette to create flexible bend points for your connections.
- **Adaptive Visuals**: Waypoints are larger when unconnected for easy selection and shrink to line-thickness when connected.
- **Signal Tracking**: Waypoints automatically adopt the color of the incoming connection (Pipeline vs. Reference).
- **Smart Alignment**: Supports Snap-to-Grid (`Shift`) and Group Binding (`Ctrl`).

### 🚩 Node Flagging & Locking
- **Flagging**: Mark important nodes with a red flag icon. Flagged nodes feature a subtle red gradient highlight.
- **Locking**: Prevent accidental movement by locking nodes. Locked nodes cannot be dragged unless unlocked.
- **Group Locking**: Locking a group effectively locks all nodes inside it for stable layout management.

### 🎨 Global Color Management & Synchronization
- **Fixed Palette Sync**: Changing module colors in the palette now correctly applies to *all future* nodes created, as well as existing ones.
- **Tag Sync**: Tag renaming, color changes, and deletions are now perfectly synchronized across all nodes in the scene.
- **Default Aesthetics**: New tags now default to a clean, professional gray, reducing overhead for custom styling.

### 🛠️ UX Improvements & Bugfixes
- **Group Drag Snap**: Fixed the "double-movement" bug where groups and child nodes would desync during Shift+Drag snapping.
- **Multi-Select Stability**: Refined `Ctrl+Click` selection logic for reliable multi-item manipulation.
- **Logical Connections**: Prevented invalid connections from Flowchart nodes specifically to Reference nodes.
- **Group Deletion**: Automatically unbinds child nodes when a group is deleted.

<details>
<summary><strong>📜 Previous Versions</strong></summary>

### V3.5.0
- **Node Grouping**: Visual containers with auto-containment (Ctrl+Drag).
- **TODO Enhancements**: Context menu for editing and reordering tasks.

### V3.1.0
- **Tag Customization**: Custom colors and reordering.
- **Module Palette**: Global color management for module types.

### V3.0.0
- **Portable .exe**: Standalone build with local data storage.

</details>

---

## 🚀 Key Features

### 📊 Flow & Design
- **Pipeline & Reference**: Distinguish between your research pipeline and supporting literature.
- **Smart Waypoints**: Use waypoints to manage complex flowchart layouts without overlapping lines.
- **Snap-to-Grid**: Hold `Shift` while moving nodes for precise 20px grid alignment.
- **Node Status**: Toggle "Locked" or "Flagged" states for better organization.

### 🔄 State Persistence
- **Auto-Save**: Project data is saved automatically on every interaction.
- **Undo History**: Full persistence of your operation history across sessions.

### 📄 Literature & Snippets
- **Markdown Support**: Drag `.md` files to import papers as reference nodes.
- **LaTeX Rendering**: Native rendering of formulas with automatic numbering.
- **Multimedia**: Paste images (`Ctrl+V`) or drag them directly onto nodes.

---

## 🛠️ Installation

```bash
git clone https://github.com/thefamer/ResearchFlow.git
cd ResearchFlow
pip install -r requirements.txt
python main.py
```

---

## ⌨️ Keyboard Shortcuts

| Action | Shortcut / Gesture |
|--------|-------------------|
| **Undo** | `Ctrl+Z` |
| **Redo** | `Ctrl+Y` / `Ctrl+Shift+Z` |
| **Delete** | `Delete` key |
| **Snap Move** | Hold `Shift` + Drag |
| **Group Bind** | Hold `Ctrl` + Drag into Group |
| **Multi-Select** | `Ctrl` + Click |
| **Zoom** | Mouse Wheel |
| **Pan** | Middle Mouse Button Drag |

---

## 📁 Project Structure

```
ResearchFlow/
├── main.py              # Application Entry & MainWindow
├── models.py            # Data Models (Dataclasses)
├── undo.py              # Undo/Redo Engine & Commands (V3.9.0)
├── graphics_items.py    # Custom QGraphicsItems (Nodes, Groups, Waypoints)
├── widgets.py           # Custom UI (Sidebar, Color Palette, Tags)
├── utils.py             # Theme & Project Logic
└── projects/            # Local Data Storage
```

---

## 📄 License
MIT License. Made with ❤️ for researchers everywhere.
