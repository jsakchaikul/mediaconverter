import streamlit as st
import subprocess
import os
from tempfile import NamedTemporaryFile

st.title("🎵🔄 ตัวแปลงไฟล์วิดีโอและเสียง")

uploaded_file = st.file_uploader("อัปโหลดไฟล์วิดีโอหรือเสียง", type=["mp4", "mp3", "mov", "avi", "wav", "mkv"])

output_format = st.selectbox("เลือกรูปแบบไฟล์ที่ต้องการแปลง", ["mp3", "mp4", "wav", "avi", "mov"])

if uploaded_file and output_format:
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_input:
        temp_input.write(uploaded_file.read())
        temp_input_path = temp_input.name

    base_filename = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"{base_filename}_converted.{output_format}"
    output_path = os.path.join("converted", output_filename)

    os.makedirs("converted", exist_ok=True)

    # ใช้ FFmpeg แปลงไฟล์
    command = ["ffmpeg", "-i", temp_input_path, output_path]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode == 0:
        with open(output_path, "rb") as f:
            st.success("แปลงไฟล์สำเร็จ! ดาวน์โหลดได้ด้านล่าง 👇")
            st.download_button("⬇ ดาวน์โหลดไฟล์ที่แปลงแล้ว", data=f, file_name=output_filename)
    else:
        st.error("เกิดข้อผิดพลาดในการแปลงไฟล์ โปรดตรวจสอบรูปแบบไฟล์อีกครั้ง")
