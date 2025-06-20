# DENSO Neural Matrix - Enhanced SharePoint ↔ SQL Sync Tool

**Role:** Token-Optimized World-Class Programmer
**Project:** PyQt6-based data synchronization system with bidirectional sync capabilities

## 🎯 System Overview

Enterprise-grade application for synchronizing data between SharePoint Online and SQL databases, built with modern PyQt6 architecture and enhanced UX/UI design.

## 🏗️ Current Architecture

### Core Components

```python
# Main Structure
├── ui/
│   ├── main_window.py          # Enhanced 900x500 compact design
│   ├── components/
│   │   ├── dashboard.py        # Real-time sync dashboard
│   │   └── config_panel.py     # Tabbed configuration interface
│   └── widgets/               # Reusable UI components
├── controller/
│   ├── app_controller.py      # Business logic coordinator
│   └── sync_engine.py         # Bidirectional sync engine
├── connectors/
│   ├── sharepoint_connector.py # SPO API integration
│   └── database_connector.py   # SQL/SQLite abstraction
└── utils/
   ├── excel_import_handler.py # Excel processing pipeline
   ├── config_manager.py       # Configuration management
   └── error_handling.py       # Centralized error system
Key Features Implemented

Bidirectional Sync: SPO ↔ SQL, Excel → SPO/SQL
Compact UI: 900x500 optimized interface
Smart Config Management: Unified field mapping
Excel Import Pipeline: Data validation + type inference
Error Handling: Centralized exception management

🚀 Technical Capabilities
Sync Engine
python# Bidirectional sync support
sync_directions = {
    "spo_to_sql": SharePointConnector → DatabaseConnector,
    "sql_to_spo": DatabaseConnector → SharePointConnector,
    "excel_to_spo": ExcelHandler → SharePointConnector,
    "excel_to_sql": ExcelHandler → DatabaseConnector
}
Data Processing

Excel Validation: File size, format, encoding detection
Column Mapping: Auto-cleanup for SP/SQL compatibility
Type Inference: Smart data type detection
Batch Processing: Configurable batch sizes

UI Architecture

Compact Design: Fixed 900x500 window
Component Isolation: Modular widget system
Theme System: Ultra-modern glassmorphism design
Error Recovery: Graceful fallback mechanisms

🔧 Current Implementation Status
✅ Completed Features

Enhanced compact UI (900x500)
SharePoint → SQL sync (fully functional)
Excel import validation pipeline
Config management with field mapping
Error handling system
Progress tracking
Auto-sync capabilities

⚠️ Known Issues & Workarounds
pythoncritical_bugs = {
    "excel_to_sharepoint": "Placeholder implementation",
    "excel_to_database": "Placeholder implementation",
    "sql_to_sharepoint": "Reverse sync incomplete",
    "import_path_errors": "Relative import conflicts"
}

workarounds = {
    "excel_import": "Use Excel → SQL → SPO pipeline",
    "reverse_sync": "Manual data export/import",
    "imports": "Fallback absolute imports implemented"
}
🎯 Next Implementation Priorities

Complete Excel Import: Actual data insertion
SQL → SharePoint Sync: Reverse sync implementation
Import Path Resolution: Fix relative imports
Real-time Progress: Granular progress reporting

💡 Architecture Decisions
Design Patterns Used

MVC Pattern: Clear separation of concerns
Observer Pattern: Signal-slot communication
Factory Pattern: Component creation
Strategy Pattern: Sync direction handling

Technology Stack
yamlUI Framework: PyQt6
Database: SQLAlchemy (SQL Server/SQLite)
SharePoint: REST API + OAuth2
Excel Processing: pandas + openpyxl
Error Handling: Custom exception system
Configuration: JSON + environment variables
Performance Optimizations

Batch processing for large datasets
Connection pooling
Memory-efficient data streaming
Compact UI for resource constraints

🔍 Problem Areas Requiring Attention
Import System Issues
python# Current problematic imports
from ui.components.dashboard import ModernDashboard  # Fails
from ..widgets.status_card import ModernStatusCard   # Inconsistent

# Solution needed:
# Standardize import patterns across all modules
Component Loading Failures
python# Error pattern observed:
# "Config panel not available - skipping config signals"
# "Dashboard not available - skipping dashboard signals"

# Root cause: Import path resolution in PyQt6 modules
📋 Development Guidelines
Code Quality Standards

Type hints for all functions
Comprehensive error handling
Modular component design
Token-efficient documentation

UI/UX Principles

900x500 fixed window size
Compact but functional layouts
Modern glassmorphism theme
Accessibility considerations

Performance Requirements

Sub-1000ms UI response times
Efficient memory usage (< 200MB baseline)
Scalable to 10K+ records
Graceful error recovery

🎯 Integration Context
Copyright: © Thammaphon Chittasuwanna (SDM) | Innovation Department
Organization: DENSO
Purpose: Enterprise data synchronization solution
Deployment: Windows corporate environment

This system represents a modern approach to enterprise data integration with focus on user experience, reliability, and maintainability.
```
