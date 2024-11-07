from flask import Flask, request, jsonify, render_template
import uiautomator2 as u2
import time
import subprocess
from threading import Thread
from bin.lib.lib_adb import LibAdb

app = Flask(__name__)

# สถานะสำหรับหยุด Thread
stop_thread = False
data_adb = []

# ฟังก์ชันสำหรับเช็คอุปกรณ์ ADB อย่างต่อเนื่อง
def loop_check_adb():
    global data_adb
    while True:
        try:
            main_adb = LibAdb()
            data_adb = main_adb.list_adb()
            time.sleep(1)
        except:
            pass

Thread(target=loop_check_adb).start()

# ฟังก์ชันสำหรับคลิกปุ่ม "อนุญาต"
def click_allow(device_id):
    global stop_thread
    d = u2.connect(device_id)  # เชื่อมต่อกับอุปกรณ์ Android ด้วย device_id
    while not stop_thread:
        time.sleep(2)
        d.click(115, 1312)
        print("เริ่ม click")
        d.click(195, 1402)
        break

# Endpoint สำหรับแสดงอุปกรณ์ทั้งหมด
@app.route("/devices", methods=["GET"])
def get_devices_all():
    main_adb = LibAdb()
    data_adb = main_adb.list_adb()
    return jsonify(data_adb)

# Endpoint สำหรับตรวจสอบการติดตั้ง Termux
@app.route('/checkinstall', methods=['GET'])
def check_termux():
    device_id = request.args.get("device_id")  # รับ device_id จาก query parameter
    d = u2.connect(device_id)

    element = d(resourceId="com.termux:id/terminal_view")

    if element.exists(timeout=5.0):
        content_description = element.info.get("contentDescription", "")
        if "~ $" in content_description and "pyproject.toml" in content_description:
            return jsonify({"status": "success", "message": "ติดตั้งสำเร็จแล้ว"})
        else:
            return jsonify({"status": "error", "message": "ยังไม่ได้ติดตั้ง"})
    else:
        return jsonify({"status": "error", "message": "ยังไม่ได้ติดตั้ง"})

# Endpoint สำหรับติดตั้งคำสั่งใน Termux
@app.route('/install', methods=['POST', 'GET'])
def run_commands():
    global stop_thread
    device_id = request.args.get("device_id")  # รับ device_id จาก query parameter
    d = u2.connect(device_id)
    d.set_orientation("n")  # ตั้งค่าหน้าจอให้อยู่ในแนวตั้ง

    if d.info['currentPackageName'] == "com.termux":
        return jsonify({"status": "success", "message": "Termux กำลังทำงานอยู่"})

    d.app_start("com.termux")
    time.sleep(3)

    try:
        if d(text="อนุญาต").exists(timeout=0.1):
            d(text="อนุญาต").click()
            print("คลิกปุ่ม 'อนุญาต'")
    except Exception as e:
        print(f"Error: {e}")


    try:
        if d(text="อนุญาต").exists(timeout=0.1):
            d(text="อนุญาต").click()
            print("คลิกปุ่ม 'อนุญาต'")
    except Exception as e:
        print(f"Error: {e}")


    command_to_paste = (
        "pkg upgrade -y && "
        "pkg install git -y && "
        "pkg install python -y && "
        "yes | pip install cython && "
        "pkg install libxml2 libxslt -y && "
        "pkg install -y python ndk-sysroot clang make libjpeg-turbo -y && "
        "pkg install clang -y && "
        "yes | pip install lxml && "
        "yes | pip install --pre uiautomator2 && "
        "yes | pip install pure-python-adb && "
        "pkg install android-tools -y && "
        "yes | pip install websockets && "
        "yes | pip install flask && "
        "yes | pip install xmltodict && "
        "pkg update -y"
    )

    subprocess.run(
        f'adb -s {device_id} shell "echo \'{command_to_paste}\' | tr -d \'\\n\' | am broadcast -a clipper.set -e text \\"{command_to_paste}\\""',
        shell=True
    )
    print("ข้อความถูกคัดลอกไปยังคลิปบอร์ดแล้วผ่าน ADB")

    thread = Thread(target=click_allow, args=(device_id,))
    thread.start()

    d.send_keys(command_to_paste)
    d.send_keys("\n")
    print("คำสั่งถูกวางและรันใน Termux แล้ว")

    stop_thread = True
    thread.join()

    return jsonify({"status": "success", "message": "คำสั่งถูกวางและรันใน Termux แล้ว"})
# Endpoint สำหรับตั้งค่า ADB ให้เชื่อมต่อผ่าน TCP/IP
@app.route('/adb/tcpip', methods=['POST','GET'])
def set_adb_tcpip():
    # global stop_thread
    # device_id = request.args.get("device_id")  # รับ device_id จาก query parameter
    # d = u2.connect(device_id)
    # d.set_orientation("n")  # ตั้งค่าหน้าจอให้อยู่ในแนวตั้ง

    # if d.info['currentPackageName'] == "com.termux":
    #     return jsonify({"status": "success", "message": "Termux กำลังทำงานอยู่"})

    # d.app_start("com.termux")
    # time.sleep(3)

    global stop_thread
    device_id = request.args.get("device_id")  # รับ device_id จาก query parameter
    try:

        subprocess.run(f"adb devices", shell=True)
        print(f"ตั้งค่า ADB devices {device_id} สำเร็จ")

        subprocess.run(f"adb -s {device_id} tcpip 5555", shell=True)
        print(f"ตั้งค่า ADB ให้เชื่อมต่อผ่าน TCP/IP บนอุปกรณ์ {device_id} สำเร็จ")

        time.sleep(3)
        d = u2.connect(device_id)
        # รันคำสั่ง ADB เพื่อเปลี่ยนเป็นโหมด TCP/IP บนพอร์ต 5555
        # ตรวจสอบว่าแอป Termux กำลังทำงานอยู่หรือไม่
        if d.info['currentPackageName'] == "com.termux":
            return jsonify({"status": "success", "message": "Termux กำลังทำงานอยู่"})

        # เปิดแอป Termux
        d.app_start("com.termux")

        time.sleep(3)

        command_to_paste = "adb connect localhost:5555"
        # ใช้คำสั่ง ADB เพื่อคัดลอกข้อความไปยังคลิปบอร์ดของอุปกรณ์
        subprocess.run(
            f"adb -s {device_id} shell 'echo \"{command_to_paste}\" | tr -d \"\\n\" | clipper set'",
            shell=True
        )
        print("ข้อความถูกคัดลอกไปยังคลิปบอร์ดแล้วผ่าน ADB")


        thread = Thread(target=click_allow, args=(device_id))
        thread.start()

        d.send_keys(command_to_paste)
        d.send_keys("\n")
        print("คำสั่งถูกวางและรันใน Termux แล้ว")

        stop_thread = True
        thread.join()


        try:
            #อนุญาตจากคอมพิวเตอร์เครื่องนี้เสมอ
            element = d(text="อนุญาตจากคอมพิวเตอร์เครื่องนี้เสมอ")
            # ตรวจสอบว่าองค์ประกอบมีอยู่หรือไม่
            if element.exists(timeout=5.0):  # เพิ่มเวลาในการรอเป็น 5 วินาที
                content_description = element.info.get("checked", None)
                if content_description:
                    print("องค์ประกอบถูกเลือกแล้ว:", content_description)
                else:
                    print("ยังไม่ได้กดอนุญาต ตกลง")
                    element.click()  # คลิกที่ช่องทำเครื่องหมาย

                if d(text="ตกลง").exists:
                    d(text="ตกลง").click()
                elif d(text="อนุญาต").exists:
                    d(text="อนุญาต").click()
            else:
                print("ไม่พบองค์ประกอบที่ระบุ")
        except:
            pass
        # command_to_paste = (
        #         "git clone https://github.com/kboapi/adb.git &&"
        #         "cd adb && "
        #         "python mobile.py "
        # )


        # command_to_paste = (
        #         "cd adb && "
        #         "git pull https://github.com/kboapi/adb.git &&"
        #         "python mobile.py --username=kbiz1234"
        # )
        # # ใช้คำสั่ง ADB เพื่อคัดลอกข้อความไปยังคลิปบอร์ดของอุปกรณ์
        # subprocess.run(
        #     f"adb -s {device_id} shell 'echo \"{command_to_paste}\" | tr -d \"\\n\" | clipper set'",
        #     shell=True
        # )
        # print("ข้อความถูกคัดลอกไปยังคลิปบอร์ดแล้วผ่าน ADB")

        # d.send_keys(command_to_paste)
        # d.send_keys("\n")

        return jsonify({"status": "success", "message": f"ตั้งค่า ADB ให้เชื่อมต่อผ่าน TCP/IP สำเร็จสำหรับอุปกรณ์ {device_id}"})
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": f"ไม่สามารถตั้งค่า ADB ให้เชื่อมต่อผ่าน TCP/IP สำหรับอุปกรณ์ {device_id}"})

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html", result=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
