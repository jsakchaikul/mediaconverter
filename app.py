import streamlit as st
import ffmpeg
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
    output_dir = "converted"
    output_path = os.path.join(output_dir, output_filename)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # ตรวจสอบว่าไฟล์มีวิดีโอหรือไม่
        probe = ffmpeg.probe(temp_input_path)
        has_video = any(stream['codec_type'] == 'video' for stream in probe['streams'])

        # หากต้องการแปลงเป็นวิดีโอ แต่ไฟล์ไม่มีวิดีโอ
        if output_format in ["mp4", "avi", "mov"] and not has_video:
            # สร้างวิดีโอจากภาพ placeholder (ใช้ภาพสีดำ 1280x720)
            video = ffmpeg.input('color=c=black:s=1280x720:d=10', f='lavfi')
            audio = ffmpeg.input(temp_input_path)

            if output_format == "mp4":
                ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac', format='mp4').run()
            elif output_format == "avi":
                ffmpeg.output(video, audio, output_path, vcodec='mpeg4', acodec='mp3', format='avi').run()
            elif output_format == "mov":
                ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac', format='mov').run()
        else:
            # กรณีปกติ: แปลงแบบตรง
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
            stream.run()

        # แสดงผลลัพธ์
        with open(output_path, "rb") as f:
            st.success("✅ แปลงไฟล์สำเร็จ! ดาวน์โหลดได้ด้านล่าง 👇")
            st.download_button("⬇ ดาวน์โหลดไฟล์ที่แปลงแล้ว", data=f, file_name=output_filename)

    except ffmpeg.Error as e:
        st.error("❌ เกิดข้อผิดพลาดในการแปลงไฟล์")
        st.text(e.stderr.decode())
