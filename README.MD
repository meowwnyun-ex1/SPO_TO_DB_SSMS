DENSO Neural Matrix - SharePoint to SQL Sync System
🚀 ภาพรวมโครงการ
โปรเจกต์ DENSO Neural Matrix คือระบบซิงโครไนซ์ข้อมูลที่มีประสิทธิภาพสูง ออกแบบมาเพื่อเชื่อมต่อและถ่ายโอนข้อมูลระหว่าง SharePoint Online และฐานข้อมูล SQL Server ระบบนี้ช่วยให้มั่นใจได้ว่าข้อมูลของคุณจะทันสมัยและสอดคล้องกันทั้งสองแพลตฟอร์ม พร้อมด้วยอินเทอร์เฟซผู้ใช้แบบกราฟิก (GUI) ที่ทันสมัยและฟังก์ชันการทำงานอัตโนมัติ

✨ คุณสมบัติหลัก
การซิงค์ข้อมูลแบบสองทาง: รองรับการซิงค์ข้อมูลจาก SharePoint ไปยัง SQL Server และจาก SQL Server ไปยัง SharePoint

การเชื่อมต่อที่แข็งแกร่ง: จัดการการเชื่อมต่อกับ SharePoint Online (ผ่าน Microsoft 365) และฐานข้อมูล SQL Server/SQLite อย่างมั่นคง

การนำเข้าข้อมูล Excel: สามารถนำเข้าข้อมูลจากไฟล์ Excel ไปยังฐานข้อมูลได้โดยตรงพร้อมการแมปคอลัมน์

การซิงค์อัตโนมัติ: กำหนดค่าให้ระบบซิงค์ข้อมูลได้ตามช่วงเวลาที่กำหนด

การจัดการ Cache อัจฉริยะ: ทำความสะอาดไฟล์ชั่วคราวและ Cache ของระบบโดยอัตโนมัติ

ระบบบันทึกและการจัดการข้อผิดพลาด: มี Log Console แบบ Cyberpunk ที่แสดงสถานะและข้อผิดพลาดแบบเรียลไทม์ พร้อมระบบจัดการข้อผิดพลาดแบบรวมศูนย์

UI ที่ทันสมัยและตอบสนอง: อินเทอร์เฟซผู้ใช้ที่ออกแบบด้วย PyQt6 ด้วยธีม Ultra Modern Glassmorphism เพื่อประสบการณ์การใช้งานที่น่าประทับใจ

การจัดการการตั้งค่าแบบรวมศูนย์: กำหนดค่าการเชื่อมต่อ, การแมปฟิลด์ และการตั้งค่าอื่นๆ ได้อย่างง่ายดายผ่านไฟล์ config.json และตัวแปรสภาพแวดล้อม

การตรวจสอบสถานะ: แสดงสถานะการเชื่อมต่อ SharePoint, ฐานข้อมูล, สถานะการซิงค์ล่าสุด และสถานะการซิงค์อัตโนมัติแบบเรียลไทม์

💻 เทคโนโลยีที่ใช้
Python 3.12.10

PyQt6: สำหรับอินเทอร์เฟซผู้ใช้แบบกราฟิก (GUI)

pandas: สำหรับการจัดการและประมวลผลข้อมูล DataFrame

SQLAlchemy: สำหรับการโต้ตอบกับฐานข้อมูล SQL Server และ SQLite

pyodbc: ไดรเวอร์ ODBC สำหรับการเชื่อมต่อกับ SQL Server (จำเป็นต้องติดตั้ง ODBC Driver for SQL Server แยกต่างหาก)

requests: สำหรับการสื่อสารกับ SharePoint REST API

python-dotenv: สำหรับการจัดการตัวแปรสภาพแวดล้อม

openpyxl/xlrd: สำหรับการอ่านไฟล์ Excel

logging: สำหรับระบบบันทึก (Logging)

📁 โครงสร้างโปรเจกต์
spo_to_db_ssms/
├── .venv/ # Virtual Environment (Python 3.12.10)
├── assets/
│ ├── icons/ # ไอคอนแอปพลิเคชัน
│ └── images/ # รูปภาพประกอบ UI (เช่น พื้นหลัง)
│ └── bg_denso_matrix.jpg
├── config/
│ └── config.json # ไฟล์การตั้งค่าหลัก (ควรถูกสร้างขึ้นอัตโนมัติหากไม่มี)
├── connectors/
│ ├── **init**.py
│ ├── database_connector.py # เชื่อมต่อและจัดการการดำเนินงานกับฐานข้อมูล SQL/SQLite
│ └── sharepoint_connector.py # เชื่อมต่อและจัดการการดำเนินงานกับ SharePoint Online
├── controller/
│ ├── **init**.py
│ ├── app_controller.py # ควบคุมตรรกะหลักของแอปพลิเคชันและการสื่อสารระหว่าง UI/Logic
│ ├── connection_manager.py # จัดการการเชื่อมต่อและแคช
│ └── sync_engine.py # จัดการกระบวนการซิงโครไนซ์ข้อมูล
├── data/ # โฟลเดอร์สำหรับไฟล์ฐานข้อมูล SQLite (ถ้าใช้) หรือข้อมูลชั่วคราวอื่นๆ
├── logs/ # ไฟล์บันทึก (Log files)
├── reports/ # โฟลเดอร์สำหรับรายงานที่อาจเกิดขึ้น
├── resources/
│ ├── audio/ # ไฟล์เสียงประกอบ (เช่น เพลงพื้นหลัง)
│ │ └── bg_ambient.mp3
│ └── images/ # รูปภาพสำหรับ UI (เช่น ไอคอนในปุ่ม)
│ └── ...
├── ui/
│ ├── **init**.py
│ ├── components/
│ │ ├── **init**.py
│ │ ├── config_panel.py # แผงการตั้งค่า UI
│ │ └── dashboard.py # แดชบอร์ดหลักของ UI
│ ├── styles/
│ │ ├── **init**.py
│ │ └── theme.py # การกำหนดสไตล์ธีม Ultra Modern Glassmorphism
│ └── widgets/
│ ├── **init**.py
│ ├── cyber_log_console.py # Log Console แบบกำหนดเอง
│ ├── holographic_combobox.py# ComboBox สไตล์ Holographic
│ ├── holographic_progress_bar.py # Progress Bar สไตล์ Holographic
│ ├── modern_button.py # ปุ่ม UI ที่ทันสมัย
│ ├── modern_input.py # ช่องรับข้อมูล UI ที่ทันสมัย
│ ├── neon_groupbox.py # GroupBox สไตล์ Neon
│ ├── progress_card.py # การ์ดแสดงความคืบหน้า
│ └── status_card.py # การ์ดแสดงสถานะการเชื่อมต่อ/ซิงค์
├── utils/
│ ├── **init**.py
│ ├── auth_helper.py # ช่วยในการรับ Access Token สำหรับ SharePoint
│ ├── bug_tracker.py # ระบบติดตาม Bug ที่ทราบ
│ ├── cache_cleaner.py # ทำความสะอาด Cache และไฟล์ชั่วคราว
│ ├── config_manager.py # จัดการการโหลด/บันทึกการตั้งค่า
│ ├── config_validation.py # ตรวจสอบความถูกต้องของการตั้งค่า
│ ├── error_handling.py # ระบบจัดการข้อผิดพลาดแบบรวมศูนย์
│ ├── excel_import_handler.py # จัดการการนำเข้าไฟล์ Excel
│ └── logger.py # การตั้งค่าระบบ Logging
├── .env # ไฟล์สำหรับตัวแปรสภาพแวดล้อม (ควรถูกสร้างขึ้นหากไม่มี)
├── cleanup_project.py # สคริปต์สำหรับทำความสะอาดโปรเจกต์
├── config.json # ไฟล์การตั้งค่า (เป็น Symbolic Link ไปยัง config/config.json)
├── config.py # (เก่า) ควรจะถูกแทนที่ด้วย config_manager.py
├── data.db # ไฟล์ฐานข้อมูล SQLite (ถ้าใช้)
├── main.py # จุดเริ่มต้นของแอปพลิเคชัน
├── README.md # ไฟล์ README นี้
└── requirements.txt # รายการ Dependencies ของ Python

🛠 การตั้งค่าโครงการ
ข้อกำหนดเบื้องต้น (Prerequisites)
Python 3.12.10: แนะนำให้ใช้เวอร์ชันนี้เพื่อหลีกเลี่ยงปัญหาการคอมไพล์ pyodbc

ดาวน์โหลด Python

Microsoft Visual C++ Build Tools: จำเป็นสำหรับการคอมไพล์ pyodbc บน Windows

ดาวน์โหลด Visual Studio Build Tools

ในระหว่างการติดตั้ง ให้เลือก Workload: "Desktop development with C++"

ODBC Driver for SQL Server: จำเป็นสำหรับการเชื่อมต่อกับ SQL Server

ดาวน์โหลด ODBC Driver (เลือกเวอร์ชันที่เหมาะสมกับระบบปฏิบัติการของคุณ)

📦 การติดตั้ง
โคลน Repository:

git clone <https://github.com/your-repo/spo_to_db_ssms.git>
cd spo_to_db_ssms

สร้างและเปิดใช้งาน Virtual Environment:
สิ่งสำคัญคือต้องสร้าง Virtual Environment ด้วย Python 3.12.10 และจัดการ PATH ของระบบให้ถูกต้อง เพื่อหลีกเลี่ยงปัญหาการคอมไพล์ pyodbc

ก. ตรวจสอบเวอร์ชัน Python ของระบบหลัก (Global Python) และ PATH:
ตรวจสอบให้แน่ใจว่า Python 3.12.10 ถูกติดตั้งและอยู่ใน PATH ก่อน Python เวอร์ชันอื่นๆ (โดยเฉพาะ 3.13.x หากมี) หากไม่แน่ใจ แนะนำให้ถอนการติดตั้ง Python 3.13.x ออกจากระบบของคุณชั่วคราว

การจัดการ PATH (Windows):

ค้นหา "Edit the system environment variables" ใน Start Menu

คลิก "Environment Variables..."

ในส่วน "System variables" หา Path แล้วคลิก "Edit..."

ตรวจสอบให้แน่ใจว่าไม่มีพาธที่ชี้ไปที่ Python 3.13.x เหลืออยู่ หากมี ให้ลบออก หรือย้ายพาธของ Python 3.12.10 ขึ้นไปอยู่ต้นๆ ของรายการ

ข. ลบ Virtual Environment เก่า (หากมี):

deactivate # ถ้าอยู่ใน Virtual Environment อยู่แล้ว
rmdir /s /q .venv # สำหรับ Windows

# rm -rf .venv # สำหรับ macOS/Linux/Git Bash

ค. สร้าง Virtual Environment ใหม่ด้วย Python 3.12.10:
หาก Python 3.12.10 ของคุณอยู่ใน PATH แล้ว:

python -m venv .venv

หากคุณมี Python หลายเวอร์ชัน ให้ระบุพาธเต็มของ python.exe เวอร์ชัน 3.12.10 ของคุณ:

"C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe" -m venv .venv

# ตัวอย่าง: "C:\Python\Python312\python.exe" -m venv .venv

ง. เปิดใช้งาน Virtual Environment:

.venv\Scripts\activate # สำหรับ Windows

# source .venv/bin/activate # สำหรับ macOS/Linux/Git Bash

หลังจากเปิดใช้งานแล้ว ให้ยืนยันอีกครั้งว่าคุณกำลังใช้ Python 3.12.10:

python --version
where python # หรือ which python

ติดตั้ง Dependencies:
เมื่ออยู่ใน Virtual Environment ที่ถูกต้องแล้ว ให้ติดตั้งไลบรารีทั้งหมด:

pip install -r requirements.txt

ขั้นตอนนี้ควรจะติดตั้ง pyodbc, pandas, PyQt6 และอื่นๆ ได้สำเร็จ

⚙️ การตั้งค่าคอนฟิกูเรชัน
ไฟล์การตั้งค่าหลักคือ config/config.json และตัวแปรสภาพแวดล้อมในไฟล์ .env ระบบจะโหลดค่าจาก config.json ก่อน แล้วจึงทับด้วยค่าจาก .env

ไฟล์ config.json:

จะถูกสร้างขึ้นอัตโนมัติหากไม่มีอยู่ คุณสามารถแก้ไขไฟล์นี้เพื่อกำหนดค่าการเชื่อมต่อ SharePoint, ฐานข้อมูล SQL/SQLite, การแมปฟิลด์ และการตั้งค่าอื่นๆ

sharepoint_url, sharepoint_site, sharepoint_list: ข้อมูลการเชื่อมต่อ SharePoint ของคุณ

sharepoint_client_id, sharepoint_client_secret, tenant_id: ข้อมูลรับรองการยืนยันตัวตน SharePoint (หากใช้ App-Only Principal)

database_type: "sqlserver" หรือ "sqlite"

sql_server, sql_database, sql_username, sql_password, sql_table_name: ข้อมูลการเชื่อมต่อ SQL Server

sqlite_file, sqlite_table_name: ข้อมูลการเชื่อมต่อ SQLite

sharepoint_to_sql_mapping: การแมปชื่อคอลัมน์จาก SharePoint ไปยัง SQL (JSON object)

sql_to_sharepoint_mapping: การแมปชื่อคอลัมน์จาก SQL ไปยัง SharePoint (JSON object)

excel_import_mapping: การแมปชื่อคอลัมน์จาก Excel ไปยังฐานข้อมูล (JSON object)

auto_sync_enabled, sync_interval, sync_mode: การตั้งค่าการซิงค์อัตโนมัติ

ไฟล์ .env:

คุณสามารถสร้างไฟล์ .env ในโฟลเดอร์รูทของโปรเจกต์ และเพิ่มตัวแปรสภาพแวดล้อมที่สำคัญเพื่อปกป้องข้อมูลที่ละเอียดอ่อน (เช่น รหัสผ่าน) หรือเพื่อ override การตั้งค่าใน config.json

ตัวอย่าง .env:

SHAREPOINT_SITE="<https://yourcompany.sharepoint.com/sites/YourSite>"
SHAREPOINT_LIST="Your SharePoint List Name"
SHAREPOINT_CLIENT_ID="your-client-id"
SHAREPOINT_CLIENT_SECRET="your-client-secret"
TENANT_ID="your-tenant-id"
SQL_SERVER="your_sql_server_address"
SQL_DATABASE="your_database_name"
SQL_USERNAME="your_sql_username"
SQL_PASSWORD="your_sql_password"
SQL_TABLE_NAME="your_sql_table_name"
LOG_LEVEL="INFO"

🚀 การรันแอปพลิเคชัน
หลังจากตั้งค่าและติดตั้ง Dependencies ทั้งหมดแล้ว คุณสามารถรันแอปพลิเคชันได้:

(.venv) PS E:\GitHub\Project\spo_to_db_ssms> python main.py

แอปพลิเคชัน GUI ควรจะเปิดขึ้นมา และคุณจะเห็นแดชบอร์ด, แผงการตั้งค่า และ Log Console

💡 การใช้งาน
Dashboard:

ดูสถานะการเชื่อมต่อ SharePoint และฐานข้อมูล

ดูสถานะการซิงค์ล่าสุดและสถานะการซิงค์อัตโนมัติ

"Run Sync (SPO to SQL)": เริ่มต้นการซิงโครไนซ์ข้อมูลจาก SharePoint ไปยัง SQL Server

"Test Connections": ทดสอบการเชื่อมต่อทั้งหมด

"Clear System Cache": ล้าง Cache ของระบบ

"Clear Log Console": ล้างข้อความใน Log Console

"Import Excel to DB": นำเข้าข้อมูลจากไฟล์ Excel ไปยังฐานข้อมูล

Configuration Panel:

แก้ไขการตั้งค่าการเชื่อมต่อ SharePoint และฐานข้อมูล

กำหนดการแมปฟิลด์สำหรับ SharePoint to SQL และ SQL to SharePoint

เปิด/ปิดการซิงค์อัตโนมัติ และกำหนดช่วงเวลา

Log Console:

ดูบันทึกกิจกรรมของระบบแบบเรียลไทม์ ซึ่งจะแสดงสถานะความคืบหน้า, ข้อความแจ้งเตือน, ข้อผิดพลาด และข้อมูล Debugging

⚠️ การแก้ไขปัญหา (Troubleshooting)
NameError หรือ AttributeError:

ตรวจสอบให้แน่ใจว่าคุณได้นำเข้าโมดูลและคลาสที่จำเป็นทั้งหมดจาก PyQt6.QtCore, PyQt6.QtGui, typing และโมดูลภายในอื่นๆ ที่เกี่ยวข้อง

บางครั้งปัญหาเหล่านี้อาจเกิดจากไฟล์ .pyc ที่ล้าสมัยในโฟลเดอร์ **pycache** ลองรัน python cleanup_project.py เพื่อล้าง Cache

ปัญหาการติดตั้ง pyodbc:

สิ่งสำคัญที่สุดคือต้องแน่ใจว่าคุณใช้ Python 3.12.10 และ Virtual Environment ถูกตั้งค่าอย่างถูกต้อง (ตามขั้นตอนในส่วน "การติดตั้ง")

ตรวจสอบว่า Microsoft Visual C++ Build Tools และ ODBC Driver for SQL Server ถูกติดตั้งอย่างถูกต้อง

ลบ Virtual Environment (.venv) ทิ้ง แล้วสร้างใหม่และติดตั้ง dependencies อีกครั้ง

TypeError: handle_exceptions() got an unexpected keyword argument 'user_message':

ข้อผิดพลาดนี้แก้ไขแล้วในไฟล์ connectors/sharepoint_connector.py, connectors/database_connector.py, controller/connection_manager.py และ utils/excel_import_handler.py

ตรวจสอบว่าคุณได้แทนที่ไฟล์เหล่านี้ด้วยเวอร์ชันล่าสุดที่ผมได้ให้ไปแล้ว

UI ไม่ตอบสนอง / แฮงค์:

ระบบถูกออกแบบให้รันการซิงค์ใน Thread แยกต่างหากเพื่อป้องกัน UI แฮงค์ หาก UI ยังคงแฮงค์ อาจมีปัญหาในการทำงานของ Threading หรือการจัดการ Signal/Slot

ตรวจสอบ Log Console เพื่อดูข้อผิดพลาดที่อาจเกิดขึ้น

"Unknown configuration key '...'":

ข้อความเตือนนี้หมายถึงคุณมีคีย์ใน config.json ที่ไม่ได้ถูกกำหนดไว้ใน Config dataclass ใน utils/config_manager.py ผมได้เพิ่ม max_retries ไปแล้ว หากพบเพิ่มเติม คุณสามารถเพิ่มคีย์นั้นๆ ลงใน Config dataclass พร้อมค่าเริ่มต้นเพื่อให้ ConfigManager รู้จัก

🤝 การมีส่วนร่วม
หากคุณต้องการมีส่วนร่วมในการพัฒนาโปรเจกต์นี้:

Fork repository นี้

สร้าง branch ใหม่สำหรับฟีเจอร์ของคุณ (git checkout -b feature/AmazingFeature)

Commit การเปลี่ยนแปลงของคุณ (git commit -m 'Add AmazingFeature')

Push ไปยัง branch (git push origin feature/AmazingFeature)

เปิด Pull Request

📄 ใบอนุญาต (License)
โปรเจกต์นี้อยู่ภายใต้ใบอนุญาต MIT License ดูไฟล์ LICENSE สำหรับรายละเอียดเพิ่มเติม

© Thammaphon Chittasuwanna (SDM) | Innovation Department
