import streamlit as st
import tempfile
import os
import ffmpeg

# UI
st.set_page_config(page_title="Media Converter", layout="centered")
st.title("🎬 Media Converter")
st.markdown("แปลงไฟล์สื่อเป็นประเภทต่างๆ ได้อย่างง่ายดาย")

# อัปโหลดไฟล์
uploaded_file = st.file_uploader("📁 เลือกไฟล์เสียงหรือวิดีโอที่ต้องการแปลง", type=["mp3", "wav", "mp4", "avi", "mov"])

# เลือกรูปแบบไฟล์ที่จะเปลี่ยน
output_format = st.selectbox("🎯 เลือกรูปแบบไฟล์ที่ต้องการแปลง", ["mp3", "wav", "mp4", "avi", "mov"])

if uploaded_file:
    file_name = uploaded_file.name
    input_ext = file_name.split('.')[-1].lower()
    input_name = file_name.rsplit('.', 1)[0]

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_ext}") as tmp_input:
        tmp_input.write(uploaded_file.read())
        temp_input_path = tmp_input.name

    output_ext = output_format
    temp_output_path = os.path.join(tempfile.gettempdir(), f"{input_name}_converted.{output_ext}")

    st.markdown("""
    <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                background-color: rgba(0, 0, 0, 0.8); color: white; padding: 20px;
                border-radius: 10px; z-index: 9999; font-size: 18px;">
        ⏳ กำลังแปลงไฟล์ โปรดรอสักครู่...
    </div>
    """, unsafe_allow_html=True)

    try:
        # ตรวจสอบว่ามี video stream หรือไม่
        probe = ffmpeg.probe(temp_input_path)
        streams = probe.get('streams', [])
        has_video = any(s.get('codec_type') == 'video' for s in streams)

        if has_video or output_format in ["mp3", "wav"]:
            # ไฟล์มีวิดีโออยู่แล้ว หรือแปลงเป็นเสียง
            stream = ffmpeg.input(temp_input_path)
            ffmpeg.output(stream, temp_output_path).run()
        else:
            # แปลงเสียง → วิดีโอ → ต้องใช้ภาพพื้นหลัง
            stream_audio = ffmpeg.input(temp_input_path)
            stream_image = ffmpeg.input("black.jpg", loop=1, framerate=1, t=10)
            ffmpeg.output(stream_image, stream_audio, temp_output_path,
                          vcodec="libx264", acodec="aac", shortest=None).run()

        st.success("✅ แปลงไฟล์สำเร็จ! ดาวน์โหลดได้ด้านล่าง 👇")
        with open(temp_output_path, "rb") as file:
            st.download_button(label=f"📥 ดาวน์โหลดไฟล์ {output_format.upper()}",
                               data=file,
                               file_name=f"{input_name}.{output_ext}",
                               mime="application/octet-stream")

    except ffmpeg.Error as e:
        st.error("❌ เกิดข้อผิดพลาดในการแปลงไฟล์")
        if e.stderr:
            try:
                st.text(e.stderr.decode())
            except Exception:
                st.text("ไม่สามารถแสดงรายละเอียดเพิ่มเติมได้")
        else:
            st.text("ไม่สามารถอ่านรายละเอียดข้อผิดพลาดจาก ffmpeg ได้")

    # ล้างข้อความ overlay โดยการ rerun
    st.rerun()
