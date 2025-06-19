# สร้างไฟล์ fix_css_compatibility.py
import re


def fix_css_file(file_path):
    """แก้ไข CSS properties ที่ไม่รองรับ"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # ลบ unsupported properties
    content = re.sub(r"\s*backdrop-filter:[^;]+;", "", content)
    content = re.sub(r"\s*text-shadow:[^;]+;", "", content)
    content = re.sub(r"\s*background-size:[^;]+;", "", content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


# รันคำสั่งนี้
fix_css_file("ui/styles/theme.py")
