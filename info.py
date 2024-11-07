# import uiautomator2 as u2

# # เชื่อมต่อกับอุปกรณ์ Android
# d = u2.connect()

# # ค้นหาองค์ประกอบที่มี resourceId "com.termux:id/terminal_view"
# element = d(resourceId="com.termux:id/terminal_view")

# # ตรวจสอบว่าองค์ประกอบมีอยู่หรือไม่ และดึง content-description
# if element.exists(timeout=0.1):
#     content_description = element.info.get("contentDescription", None)
#     if "~ $" in content_description and "pyproject.toml" in content_description:
#         print("พบสัญลักษณ์ '~ $' ในข้อความ")
#     else:
#         print("ไม่พบสัญลักษณ์ '~ $' ในข้อความ")
# else:
#     print("ไม่พบองค์ประกอบที่ระบุ")


# import uiautomator2 as u2
# import argparse

# parser = argparse.ArgumentParser(description="โปรแกรมรับค่าพารามิเตอร์มือถือจากบรรทัดคำสั่ง")
# parser.add_argument('--username', type=str, help='Username Kbiz')
# args = parser.parse_args()
# print(f"kbiz user: {args.username}")


# # เชื่อมต่อกับอุปกรณ์ Android ด้วย device_id ของคุณ
# d = u2.connect("ZPMFORA6SWWWGY6T")


# print(d.device_info['serial'])

# # ค้นหาองค์ประกอบที่มีข้อความ "อนุญาตจากคอมพิวเตอร์เครื่องนี้เสมอ"
# element = d(text="อนุญาตจากคอมพิวเตอร์เครื่องนี้เสมอ")

# # ตรวจสอบว่าองค์ประกอบมีอยู่หรือไม่
# if element.exists(timeout=5.0):  # เพิ่มเวลาในการรอเป็น 5 วินาที
#     content_description = element.info.get("checked", None)
#     if content_description:
#         print("องค์ประกอบถูกเลือกแล้ว:", content_description)
#         d(text="ตกลง").click()
#     else:
#         print("ยังไม่ได้กดอนุญาต ตกลง")
#         element.click()  # คลิกที่ช่องทำเครื่องหมาย
#         d(text="ตกลง").click()  # คลิกปุ่มตกลง
# else:
#     print("ไม่พบองค์ประกอบที่ระบุ")
