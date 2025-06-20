# utils/bug_tracker.py
"""
Bug Tracker - รายการ bugs ที่ยังคงมีในระบบ
"""

import logging
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class BugSeverity(Enum):
    CRITICAL = "critical"  # ระบบใช้งานไม่ได้
    HIGH = "high"  # ฟีเจอร์หลักเสีย
    MEDIUM = "medium"  # ฟีเจอร์รองเสีย
    LOW = "low"  # ปัญหาเล็กน้อย
    COSMETIC = "cosmetic"  # ปัญหา UI/UX


class BugStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    WONT_FIX = "wont_fix"
    DUPLICATE = "duplicate"


@dataclass
class Bug:
    id: str
    title: str
    description: str
    severity: BugSeverity
    status: BugStatus
    component: str
    discovered_date: str
    fixed_date: str = ""
    workaround: str = ""
    notes: str = ""


class BugTracker:
    """จัดการรายการ bugs ที่ทราบในระบบ"""

    def __init__(self):
        self.bugs = self._initialize_known_bugs()

    def _initialize_known_bugs(self) -> List[Bug]:
        """รายการ bugs ที่ทราบแล้ว"""
        return [
            Bug(
                id="BUG-001",
                title="Excel Import: SharePoint Upload ยังไม่ implement",
                description="ฟีเจอร์ import Excel ไป SharePoint ยังเป็นแค่ placeholder",
                severity=BugSeverity.HIGH,
                status=BugStatus.OPEN,
                component="excel_import_handler",
                discovered_date="2024-12-19",
                workaround="ใช้ Excel → SQL แล้วค่อย SQL → SPO",
                notes="ต้องใช้ SharePoint API สำหรับ bulk insert",
            ),
            Bug(
                id="BUG-002",
                title="Excel Import: Database Import ยังไม่ implement",
                description="ฟีเจอร์ import Excel ไป Database ยังเป็นแค่ placeholder",
                severity=BugSeverity.HIGH,
                status=BugStatus.OPEN,
                component="excel_import_handler",
                discovered_date="2024-12-19",
                workaround="ใช้ manual import ผ่าน SQL tools",
                notes="ต้องใช้ DatabaseConnector.insert_data()",
            ),
            Bug(
                id="BUG-003",
                title="SQL to SharePoint Sync ยังไม่ implement",
                description="Reverse sync จาก SQL ไป SharePoint ยังเป็น placeholder",
                severity=BugSeverity.HIGH,
                status=BugStatus.OPEN,
                component="sync_engine",
                discovered_date="2024-12-19",
                workaround="ใช้แค่ SPO → SQL sync",
                notes="ต้องทำ SharePointConnector.upload_data()",
            ),
            Bug(
                id="BUG-004",
                title="Config field mapping conflicts",
                description="มี config fields ซ้อนกัน (เก่า/ใหม่) ทำให้สับสน",
                severity=BugSeverity.MEDIUM,
                status=BugStatus.IN_PROGRESS,
                component="config_manager",
                discovered_date="2024-12-18",
                workaround="ใช้ __post_init__ เพื่อ sync fields",
                notes="แก้โดยทำ unified config structure",
            ),
            Bug(
                id="BUG-005",
                title="Log Console: Memory leak จากการเก็บ log มากเกินไป",
                description="Log console ไม่ได้จำกัดจำนวนบรรทัด ทำให้ใช้ RAM มาก",
                severity=BugSeverity.MEDIUM,
                status=BugStatus.FIXED,
                component="cyber_log_console",
                discovered_date="2024-12-19",
                fixed_date="2024-12-19",
                notes="แก้แล้วด้วย _limit_lines() method",
            ),
            Bug(
                id="BUG-006",
                title="Auto-sync timer ไม่ reset เมื่อเปลี่ยน interval",
                description="เปลี่ยน sync interval ใน config แต่ timer ยังใช้ค่าเก่า",
                severity=BugSeverity.LOW,
                status=BugStatus.OPEN,
                component="app_controller",
                discovered_date="2024-12-19",
                workaround="ปิด/เปิด auto-sync ใหม่",
                notes="ต้องแก้ toggle_auto_sync() method",
            ),
            Bug(
                id="BUG-007",
                title="Error handling: ไม่มี user-friendly error messages",
                description="Error messages ยังเป็นแบบ technical ไม่เหมาะกับ end users",
                severity=BugSeverity.LOW,
                status=BugStatus.OPEN,
                component="error_handling",
                discovered_date="2024-12-19",
                workaround="ดู log console สำหรับรายละเอียด",
                notes="ต้องทำ error message mapping",
            ),
            Bug(
                id="BUG-008",
                title="Database connection: SQL Server timeout issues",
                description="Connection timeout ไม่ได้ใช้ config value",
                severity=BugSeverity.MEDIUM,
                status=BugStatus.OPEN,
                component="database_connector",
                discovered_date="2024-12-19",
                workaround="เพิ่ม timeout ใน connection string",
                notes="แก้ใน _build_sqlserver_connection_string()",
            ),
            Bug(
                id="BUG-009",
                title="UI Scaling: หน้าจอ resolution สูงแสดงผลไม่ดี",
                description="UI elements เล็กเกินไปใน high DPI screens",
                severity=BugSeverity.COSMETIC,
                status=BugStatus.OPEN,
                component="main_window",
                discovered_date="2024-12-19",
                workaround="ปรับ Windows scaling ให้เหมาะสม",
                notes="ต้องเพิ่ม Qt High DPI support",
            ),
            Bug(
                id="BUG-010",
                title="Progress bar: ไม่แสดง real-time progress",
                description="Progress bar กระโดดจาก 0% ไป 100% โดยไม่แสดง progress ระหว่างทาง",
                severity=BugSeverity.LOW,
                status=BugStatus.OPEN,
                component="sync_engine",
                discovered_date="2024-12-19",
                workaround="ดู log console สำหรับ progress updates",
                notes="ต้องเพิ่ม progress reporting ใน sync phases",
            ),
            Bug(
                id="BUG-011",
                title="Cleanup: Double cleanup ทำให้เกิด errors",
                description="เรียก cleanup หลายครั้งทำให้เกิด exception",
                severity=BugSeverity.LOW,
                status=BugStatus.FIXED,
                component="main_window",
                discovered_date="2024-12-18",
                fixed_date="2024-12-19",
                notes="แก้แล้วด้วย cleanup_done flag",
            ),
            Bug(
                id="BUG-012",
                title="Config validation: ไม่ validate SharePoint URL format",
                description="สามารถใส่ URL ผิดรูปแบบได้ ทำให้ connection fail",
                severity=BugSeverity.MEDIUM,
                status=BugStatus.OPEN,
                component="config_validation",
                discovered_date="2024-12-19",
                workaround="ตรวจสอบ URL format ด้วยตัวเอง",
                notes="ใช้ config_validation.py ที่มีอยู่แล้ว",
            ),
            Bug(
                id="BUG-013",
                title="SharePoint API: Rate limiting ไม่ได้ handle",
                description="เมื่อดึงข้อมูลเยอะจาก SharePoint อาจโดน rate limit",
                severity=BugSeverity.MEDIUM,
                status=BugStatus.OPEN,
                component="sharepoint_connector",
                discovered_date="2024-12-19",
                workaround="ลด batch_size ใน config",
                notes="มี time.sleep(0.1) แล้ว แต่อาจไม่พอ",
            ),
            Bug(
                id="BUG-014",
                title="Excel Import: ไม่ validate ขนาดไฟล์ก่อนอ่าน",
                description="อ่านไฟล์ Excel ขนาดใหญ่อาจทำให้ memory overflow",
                severity=BugSeverity.MEDIUM,
                status=BugStatus.FIXED,
                component="excel_import_handler",
                discovered_date="2024-12-19",
                fixed_date="2024-12-19",
                notes="แก้แล้วด้วย file size validation (50MB limit)",
            ),
            Bug(
                id="BUG-015",
                title="Status Cards: Animation lag ใน slow systems",
                description="Status card animations ทำให้ระบบช้าใน low-end PCs",
                severity=BugSeverity.COSMETIC,
                status=BugStatus.OPEN,
                component="status_card",
                discovered_date="2024-12-19",
                workaround="ปิด animations ใน low-end systems",
                notes="ควรเพิ่ม performance detection",
            ),
        ]

    def get_open_bugs(self) -> List[Bug]:
        """ดึง bugs ที่ยังไม่ได้แก้"""
        return [bug for bug in self.bugs if bug.status == BugStatus.OPEN]

    def get_bugs_by_severity(self, severity: BugSeverity) -> List[Bug]:
        """ดึง bugs ตามระดับความร้ายแรง"""
        return [bug for bug in self.bugs if bug.severity == severity]

    def get_bugs_by_component(self, component: str) -> List[Bug]:
        """ดึง bugs ตาม component"""
        return [bug for bug in self.bugs if bug.component == component]

    def get_critical_bugs(self) -> List[Bug]:
        """ดึง critical bugs ที่ต้องแก้ด่วน"""
        return [
            bug
            for bug in self.bugs
            if bug.severity in [BugSeverity.CRITICAL, BugSeverity.HIGH]
            and bug.status == BugStatus.OPEN
        ]

    def get_bug_summary(self) -> Dict:
        """สรุปสถานะ bugs"""
        summary = {
            "total": len(self.bugs),
            "open": len([b for b in self.bugs if b.status == BugStatus.OPEN]),
            "fixed": len([b for b in self.bugs if b.status == BugStatus.FIXED]),
            "in_progress": len(
                [b for b in self.bugs if b.status == BugStatus.IN_PROGRESS]
            ),
            "by_severity": {
                "critical": len(
                    [b for b in self.bugs if b.severity == BugSeverity.CRITICAL]
                ),
                "high": len([b for b in self.bugs if b.severity == BugSeverity.HIGH]),
                "medium": len(
                    [b for b in self.bugs if b.severity == BugSeverity.MEDIUM]
                ),
                "low": len([b for b in self.bugs if b.severity == BugSeverity.LOW]),
                "cosmetic": len(
                    [b for b in self.bugs if b.severity == BugSeverity.COSMETIC]
                ),
            },
            "by_component": {},
        }

        # Count by component
        for bug in self.bugs:
            if bug.component not in summary["by_component"]:
                summary["by_component"][bug.component] = 0
            summary["by_component"][bug.component] += 1

        return summary

    def print_bug_report(self):
        """พิมพ์รายงาน bugs"""
        summary = self.get_bug_summary()

        print("=" * 60)
        print("🐛 BUG TRACKER REPORT")
        print("=" * 60)
        print(f"Total Bugs: {summary['total']}")
        print(
            f"Open: {summary['open']} | Fixed: {summary['fixed']} | In Progress: {summary['in_progress']}"
        )
        print()

        print("📊 BY SEVERITY:")
        for severity, count in summary["by_severity"].items():
            if count > 0:
                print(f"  {severity.upper()}: {count}")
        print()

        print("🔧 BY COMPONENT:")
        for component, count in summary["by_component"].items():
            print(f"  {component}: {count}")
        print()

        critical_bugs = self.get_critical_bugs()
        if critical_bugs:
            print("🚨 CRITICAL/HIGH PRIORITY BUGS:")
            for bug in critical_bugs:
                print(f"  {bug.id}: {bug.title} ({bug.severity.value})")
                if bug.workaround:
                    print(f"    Workaround: {bug.workaround}")
            print()

        print("=" * 60)

    def add_bug(self, bug: Bug):
        """เพิ่ม bug ใหม่"""
        self.bugs.append(bug)
        logger.info(f"Added new bug: {bug.id} - {bug.title}")

    def update_bug_status(self, bug_id: str, status: BugStatus, notes: str = ""):
        """อัปเดตสถานะ bug"""
        for bug in self.bugs:
            if bug.id == bug_id:
                bug.status = status
                if notes:
                    bug.notes = f"{bug.notes}\n{datetime.now().strftime('%Y-%m-%d')}: {notes}".strip()
                if status == BugStatus.FIXED:
                    bug.fixed_date = datetime.now().strftime("%Y-%m-%d")
                logger.info(f"Updated bug {bug_id} status to {status.value}")
                return True
        return False

    def find_bug(self, bug_id: str) -> Bug:
        """ค้นหา bug ด้วย ID"""
        for bug in self.bugs:
            if bug.id == bug_id:
                return bug
        return None


# สร้าง global bug tracker instance
bug_tracker = BugTracker()


def log_known_issue(component: str, issue: str, workaround: str = ""):
    """Log known issue เมื่อเจอใน runtime"""
    logger.warning(f"KNOWN ISSUE in {component}: {issue}")
    if workaround:
        logger.info(f"WORKAROUND: {workaround}")


def check_system_health():
    """ตรวจสอบสุขภาพระบบและแจ้ง known issues"""
    summary = bug_tracker.get_bug_summary()
    open_bugs = summary["open"]
    critical_bugs = len(bug_tracker.get_critical_bugs())

    logger.info(
        f"System Health Check: {open_bugs} open bugs ({critical_bugs} critical/high)"
    )

    if critical_bugs > 0:
        logger.warning("⚠️ System has critical bugs that may affect functionality")
        for bug in bug_tracker.get_critical_bugs():
            logger.warning(f"  - {bug.title} (Workaround: {bug.workaround or 'None'})")


# Quick access functions
def get_open_bugs():
    return bug_tracker.get_open_bugs()


def get_critical_bugs():
    return bug_tracker.get_critical_bugs()


def print_bugs():
    bug_tracker.print_bug_report()


if __name__ == "__main__":
    # สำหรับทดสอบ
    bug_tracker.print_bug_report()
    print()
    check_system_health()
