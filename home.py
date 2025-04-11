import streamlit as st

def home():
    st.image("images/home.png", width=1000)
    
    # Hiển thị tiêu đề đồ án
    st.title("Đồ án tốt nghiệp Data Science")
    
    # Hiển thị thông tin chi tiết
    st.subheader("Topic 1: Customer Segmentation")
    st.markdown("**DL07 – K302 – April 2025**")
    
    # Thêm thông tin người thực hiện
    st.markdown("**Người thực hiện:** Hàn Thảo Anh, Nguyễn Thị Thùy Trang")
    
    # Thêm thông tin về giáo viên hướng dẫn
    st.markdown("**Giáo viên hướng dẫn:** Cô Khuất Thùy Phương")
