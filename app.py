import streamlit as st
import ffmpeg
import os
from tempfile import NamedTemporaryFile

st.set_page_config(page_title="Media Converter", layout="centered")
st.title("🎵🔄 ตัวแปลงไฟล์วิดีโอและเสียง")

uploaded_file = st.file_uploader("อัปโหลดไฟล์วิดีโอหรือเสียง", type=["mp4", "mp3", "mov", "avi", "wav", "mkv"])
output_format = st.selectbox("เลือกรูปแบบไฟล์ที่ต้องการแปลง", ["mp3", "mp4", "wav", "avi", "mov"])

# แสดง overlay loading หากกำลังประมวลผล
def show_loading_overlay():
    st.markdown("""
        <style>
        .overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0,0,0,0.6);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .overlay-text {
            color: white;
            font-size: 2em;
            font-weight: bold;
        }
        </style>
        <div class="overlay">
            <div class="overlay-text">⏳ กำลังแปลงไฟล์ โปรดรอสักครู่...</div>
        </div>
    """, unsafe_allow_html=True)

if uploaded_file and output_format:
    # แสดง overlay ก่อนประมวลผล
    show_loading_overlay()

    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_input:
        temp_input.write(uploaded_file.read())
        temp_input_path = temp_input.name

    base_filename = os.path.splitext(uploaded_file.name)[0]
    output_filename = f"{base_filename}_converted.{output_format}"
    output_dir = "converted"
    output_path = os.path.join(output_dir, output_filename)
    os.makedirs(output_dir, exist_ok=True)

    try:
        probe = ffmpeg.probe(temp_input_path)
        has_video = any(stream['codec_type'] == 'video' for stream in probe['streams'])

        if output_format in ["mp4", "avi", "mov"] and not has_video:
            video = ffmpeg.input('color=c=black:s=1280x720:d=10', f='lavfi')
            audio = ffmpeg.input(temp_input_path)

            if output_format == "mp4":
                ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac', format='mp4').run()
            elif output_format == "avi":
                ffmpeg.output(video, audio, output_path, vcodec='mpeg4', acodec='mp3', format='avi').run()
            elif output_format == "mov":
                ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac', format='mov').run()
        else:
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

        # ซ่อน overlay โดย refresh ส่วนนี้ (streamlit ทำเองอัตโนมัติ)
        st.success("✅ แปลงไฟล์สำเร็จ! ดาวน์โหลดได้ด้านล่าง 👇")
        with open(output_path, "rb") as f:
            st.download_button("⬇ ดาวน์โหลดไฟล์ที่แปลงแล้ว", data=f, file_name=output_filename)

    except ffmpeg.Error as e:
    st.error("❌ เกิดข้อผิดพลาดในการแปลงไฟล์")
    if e.stderr:
        st.text(e.stderr.decode())
    else:
        st.text("ไม่สามารถอ่านรายละเอียดข้อผิดพลาดจาก ffmpeg ได้")
