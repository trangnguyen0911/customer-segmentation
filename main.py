import streamlit as st
import base64
from home import home
from general_content import general_content
from segmentation import segmentation
from suggestions import strategy_suggestions


def sidebar_bg(side_bg):
   side_bg_ext = 'png'

   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:images/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
    )

# Tạo trang chính cho Streamlit
def main():
    # CSS để đặt background image cho sidebar
    side_bg = 'images/bg.png'
    sidebar_bg(side_bg)

    # Tạo danh sách menu dạng dropdown
    menu_items = {
        "🏠 Home": "Home",
        "📊 Giới thiệu chung": "Giới thiệu chung",
        "📈 Phân cụm khách hàng": "Phân cụm khách hàng",
        "🎯 Gợi ý chiến lược": "Gợi ý chiến lược"
    }

    # Hiển thị dropdown trong sidebar
    st.sidebar.markdown("## 📌 Menu")
    selected_label = st.sidebar.selectbox("Chọn mục:", list(menu_items.keys()))

    # Lấy giá trị thực
    selected = menu_items[selected_label]

    # Điều hướng nội dung
    if selected == "Home":
        home()
    elif selected == "Giới thiệu chung":
        general_content()
    elif selected == "Phân cụm khách hàng":
        segmentation()
    elif selected == "Gợi ý chiến lược":
        strategy_suggestions()
    
    st.sidebar.markdown("""
    <style>
    .sidebar-footer {
        background-color: #e0f2f1;  /* Màu xanh nhạt */
        padding: 15px;
        border-radius: 8px;
        margin-top: 200px;
        color: #003f5c;
        font-size: 14px;
        line-height: 1.5;
    }
    </style>

    <div class="sidebar-footer">
        <strong>DL07 – K302 – April 2025</strong><br>
        Hàn Thảo Anh<br>
        Nguyễn Thị Thùy Trang<br>
        👩‍🏫 <strong>GVHD: Cô Khuất Thùy Phương</strong>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()