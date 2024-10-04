import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from io import BytesIO

# Hàm để gửi ảnh tới API backend FastAPI và nhận kết quả OCR
def call_ocr_api(image):
    # Chuyển đổi ảnh sang chế độ RGB nếu ảnh đang ở chế độ RGBA
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    # Chuyển đổi ảnh PIL sang byte để gửi qua API
    buffered = BytesIO()
    image.save(buffered, format="JPEG")  # Lưu ảnh dưới dạng JPEG sau khi chuyển đổi sang RGB
    img_bytes = buffered.getvalue()

    # Gửi POST request tới API FastAPI với tệp ảnh
    files = {'file': ('image.jpg', img_bytes, 'image/jpeg')}
    response = requests.post("http://ocr-app:3000/preloaded_ocr", files=files)

    # Kiểm tra nếu response thành công
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to get response from OCR API")
        return None

# Hàm để vẽ bounding box và text lên ảnh
def visualize_ocr_results(image, ocr_results):
    draw = ImageDraw.Draw(image)
    
    # Load font nếu cần thiết
    fontpath = "./fonts/BeVietnam-Light.ttf"  # Đường dẫn tới font TTF của bạn
    font = ImageFont.truetype(fontpath, 15)

    # Lấy dữ liệu từ kết quả OCR (bounding boxes, texts, probabilities)
    bboxes = ocr_results["bboxes"]
    texts = ocr_results["texts"]
    probs = ocr_results["probs"]

    for bbox, text, prob in zip(bboxes, texts, probs):
        if prob >= 0.5:  # Chỉ vẽ nếu xác suất nhận dạng trên 0.5
            bbox = np.array(bbox).tolist()
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = (int(top_left[0]), int(top_left[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))

            # Vẽ text với màu xanh dương (blue) và box với màu đỏ (red)
            draw.text((top_left[0], top_left[1] - 20), text, font=font, fill=(0, 0, 255, 255))  # Màu xanh dương cho text
            draw.rectangle([top_left, bottom_right], outline="red", width=2)  # Màu đỏ cho bounding box với đường dày hơn
    
    return image

# Giao diện Streamlit
st.title("OCR System with FastAPI Backend")

# Tải lên ảnh từ người dùng
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Mở ảnh
    image = Image.open(uploaded_file)
    
    # Tạo hai cột cho việc hiển thị ảnh gốc và ảnh đã visualized
    col1, col2 = st.columns(2)

    # Hiển thị ảnh gốc ở cột 1
    with col1:
        st.image(image, caption="Original Image", use_column_width=True)
    
    # Nhấn nút để gọi API OCR
    if st.button("Run OCR"):
        with st.spinner("Processing..."):
            # Gọi API OCR trên FastAPI
            ocr_results = call_ocr_api(image)
            
            if ocr_results:
                # Visualize kết quả OCR với bounding boxes và text
                img_with_boxes = visualize_ocr_results(image.copy(), ocr_results)
                
                # Hiển thị ảnh đã vẽ bounding box ở cột 2
                with col2:
                    st.image(img_with_boxes, caption="Image with OCR Results", use_column_width=True)

                # Hiển thị kết quả OCR dưới dạng text
                st.write("Detected Texts:")
                for text, prob in zip(ocr_results["texts"], ocr_results["probs"]):
                    st.write(f"{text} (Probability: {prob:.2f})")
