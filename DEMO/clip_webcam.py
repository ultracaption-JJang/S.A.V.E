import streamlit as st
import cv2
import os
import time

# 프레임 저장 폴더
save_dir = "./frames"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Streamlit 페이지 구성
st.title("카메라 캡처 및 이미지 저장")

# 상태 변수
start_capture = st.button("카메라 시작")
stop_capture = st.button("카메라 종료")

# 옵션 선택: 1초 간격 또는 5프레임 간격
capture_interval = st.selectbox("이미지 저장 주기 선택", ["1초 간격", "5프레임 간격"])

# 카메라 캡처 시작
if start_capture:
    cap = cv2.VideoCapture(0)
    frame_count = 0  # 프레임 번호 카운팅
    last_saved_time = time.time()  # 마지막 저장 시간 기록
    
    st.write("카메라가 실행 중입니다. 이미지를 저장합니다...")

    # 스트리밍 및 저장 루프
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("프레임을 가져올 수 없습니다.")
            break

        # 프레임을 보여주기 (Streamlit에서 OpenCV 사용 불가하므로 HTML로 전환)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, channels="RGB", caption="Camera Stream")

        # 이미지 저장 조건 체크
        if capture_interval == "1초 간격":
            if time.time() - last_saved_time >= 1:  # 1초 간격으로 저장
                filename = os.path.join(save_dir, f"frame_{frame_count}.jpg")
                cv2.imwrite(filename, frame)
                st.write(f"{filename} 저장 완료")
                frame_count += 1
                last_saved_time = time.time()
        else:  # 5프레임 간격으로 저장
            if frame_count % 5 == 0:
                filename = os.path.join(save_dir, f"frame_{frame_count}.jpg")
                cv2.imwrite(filename, frame)
                st.write(f"{filename} 저장 완료")
            frame_count += 1

        # '카메라 종료' 버튼이 눌리면 루프 종료
        if stop_capture:
            st.write("카메라 프로세스가 종료되었습니다.")
            break

    cap.release()  # 카메라 해제
    cv2.destroyAllWindows()

elif stop_capture:
    st.write("카메라가 종료되었습니다.")
