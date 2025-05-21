import streamlit as st
import ffmpeg
import os
from tempfile import NamedTemporaryFile

st.title("🎵🔄 ตัวแปลงไฟล์วิดีโอและเสียง")

uploaded_file = st.file_uploader("อัปโหลดไฟล์วิดีโอหรือเสียง", type=["mp4", "mp3", "mov", "avi", "wav", "mkv"])
output_format = st.selectbox("เลือกรูปแบบไฟล์ที่ต้องการแปลง", ["mp3", "mp4", "wav", "avi", "mov"])

if uploaded_file and output_format:
    # สร้างไฟล์ชั่วคราวจากไฟล์ที่อัปโหลด
    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_input:
        temp_input.write(uploaded_file.read())
        temp_input_path = temp_input.name

    base_filename = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"{base_filename}_converted.{output_format}"
    output_dir = "converted"
    output_path = os.path.join(output_dir, output_filename)

    os.makedirs(output_dir, exist_ok=True)

    try:
        # ตั้งค่าการแปลงไฟล์ตามรูปแบบที่เลือก
        stream = ffmpeg.input(temp_input_path)

        if output_format == "mp3":
            stream = ffmpeg.output(stream, output_path, format="mp3", acodec="libmp3lame")
        elif output_format == "mp4":
            stream = ffmpeg.output(stream, output_path, vcodec="libx264", acodec="aac", format="mp4")
        elif output_format == "wav":
            stream = ffmpeg.output(stream, output_path, format="wav")
        elif output_format == "avi":
            stream = ffmpeg.output(stream, output_path, vcodec="mpeg4", acodec="mp3", format="avi")
        elif output_format == "mov":
            stream = ffmpeg.output(stream, output_path, vcodec="libx264", acodec="aac", format="mov")
        else:
            st.error("ไม่รองรับรูปแบบไฟล์ที่เลือก")
            st.stop()

        stream.run()

        # แสดงปุ่มดาวน์โหลด
        with open(output_path, "rb") as f:
            st.success("✅ แปลงไฟล์สำเร็จ! ดาวน์โหลดได้ด้านล่าง 👇")
            st.download_button("⬇ ดาวน์โหลดไฟล์ที่แปลงแล้ว", data=f, file_name=output_filename)
    except ffmpeg.Error as e:
        st.error("❌ เกิดข้อผิดพลาดในการแปลงไฟล์")
        st.text(e.stderr.decode())
