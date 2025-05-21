import streamlit as st
import ffmpeg
import os
import uuid

st.set_page_config(page_title="Media Converter", layout="centered")
st.title("🎵🔁 Media Converter")

st.markdown("แปลงไฟล์เสียงหรือวิดีโอเป็นฟอร์แมตที่คุณต้องการ")

uploaded_file = st.file_uploader("📤 อัปโหลดไฟล์", type=["mp3", "wav", "ogg", "mp4", "avi", "mov"])

output_format = st.selectbox("🎯 เลือกรูปแบบไฟล์ที่ต้องการแปลง", ["mp3", "wav", "ogg", "mp4", "avi", "mov"])

if uploaded_file is not None:
    file_id = str(uuid.uuid4())
    input_path = f"input_{file_id}_{uploaded_file.name}"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.read())

    base_filename = os.path.splitext(uploaded_file.name)[0]
    output_path = f"output_{file_id}_{base_filename}.{output_format}"

    if st.button("🚀 เริ่มแปลงไฟล์"):
        # แสดงข้อความ overlay
        placeholder = st.empty()
        placeholder.markdown("""
        <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                    background-color: rgba(0, 0, 0, 0.8); color: white; padding: 20px;
                    border-radius: 10px; z-index: 9999; font-size: 18px;">
            ⏳ กำลังแปลงไฟล์ โปรดรอสักครู่...
        </div>
        """, unsafe_allow_html=True)

        try:
            input_stream = ffmpeg.input(input_path)

            # เลือก output โดยพิจารณาจากประเภทไฟล์
            if output_format in ["mp3", "wav", "ogg"]:
                stream = ffmpeg.output(input_stream.audio, output_path)
            elif output_format in ["mp4", "avi", "mov"]:
                # สร้างวิดีโอจากเสียง (ด้วย black video)
                audio = input_stream.audio
                video = ffmpeg.input("color=black:s=1280x720:d=5", f="lavfi")  # 5 วินาทีหรือปรับได้
                stream = ffmpeg.output(video, audio, output_path, vcodec="libx264", acodec="aac", shortest=None)
            else:
                raise ValueError("Unsupported format")

            stream.run()

            placeholder.empty()  # ซ่อน overlay

            st.success("✅ แปลงไฟล์สำเร็จ! ดาวน์โหลดได้ด้านล่าง 👇")
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์",
                    data=f,
                    file_name=os.path.basename(output_path),
                    mime="application/octet-stream"
                )

            # ลบไฟล์ที่ไม่จำเป็น
            os.remove(input_path)
            os.remove(output_path)

        except ffmpeg.Error as e:
            placeholder.empty()  # ซ่อน overlay เมื่อเกิด error
            st.error("❌ เกิดข้อผิดพลาดในการแปลงไฟล์")
            st.text(e.stderr.decode() if e.stderr else "ไม่พบรายละเอียดเพิ่มเติม")

        except Exception as e:
            placeholder.empty()
            st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
