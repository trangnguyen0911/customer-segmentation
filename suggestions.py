import streamlit as st
import pandas as pd
from segmentation import *

# Tính toán Segment dựa trên RFM hoặc mã khách hàng
def calculate_segment(df_RFM, customer_id=None, recency=None, frequency=None, monetary=None):
    if customer_id is not None:
        # Trường hợp chọn theo mã khách hàng
        customer_data = df_RFM[df_RFM.index == customer_id]
        if not customer_data.empty:
            return customer_data["Segment"].values[0]
        else:
            return "Không tìm thấy khách hàng này"
    else:
        # Trường hợp chọn theo RFM từ slider
        # Định nghĩa nhãn cho Recency, Frequency, Monetary
        r_labels = [3, 2, 1]  # Giảm dần vì Recency thấp hơn là tốt hơn
        f_labels = [1, 2, 3]  # Tăng dần vì Frequency cao hơn là tốt hơn
        m_labels = [1, 2, 3]  # Tăng dần vì Monetary cao hơn là tốt hơn

        # Tính toán biên phân vị thực tế từ dữ liệu
        r_bins = pd.qcut(df_RFM['Recency'], q=3, duplicates='drop', retbins=True)[1]
        f_bins = pd.qcut(df_RFM['Frequency'], q=3, duplicates='drop', retbins=True)[1]
        m_bins = pd.qcut(df_RFM['Monetary'], q=3, duplicates='drop', retbins=True)[1]

        # Gán nhãn cho Recency
        if recency <= r_bins[1]:
            r_label = 3
        elif recency <= r_bins[2]:
            r_label = 2
        else:
            r_label = 1

        # Gán nhãn cho Frequency
        if frequency <= f_bins[1]:
            f_label = 1
        elif frequency <= f_bins[2]:
            f_label = 2
        else:
            f_label = 3

        # Gán nhãn cho Monetary
        if monetary <= m_bins[1]:
            m_label = 1
        elif monetary <= m_bins[2]:
            m_label = 2
        else:
            m_label = 3

        # Hiển thị nhãn
        # st.write(f"R label for {recency}: {r_label}")
        # st.write(f"F label for {frequency}: {f_label}")
        # st.write(f"M label for {monetary}: {m_label}")

        # Tạo RFM segment
        RFM_segment = f"{r_label}{f_label}{m_label}"

        # Kiểm tra xem có khách hàng nào khớp chính xác không
        customer_data = df_RFM[
            (df_RFM['Recency'] == recency) & 
            (df_RFM['Frequency'] == frequency) & 
            (abs(df_RFM['Monetary'] - monetary) < 1)
        ]
        
        if customer_data.empty:
            return None, segment_customers(RFM_segment)
        else:
            return customer_data.index[0], segment_customers(RFM_segment)

# Hiển thị chiến lược kinh doanh cho nhóm khách hàng
def display_strategy(segment):
    if segment == "Champions":
        st.markdown("""
        ### 🎁 Chiến lược ưu đãi dành cho khách hàng Champions

        - 🎯 **Chương trình tích điểm** đổi quà hoặc voucher  
        - 💌 **Ưu đãi đặc biệt** (giảm **5% - 10%**) gửi qua **SMS / Email / Mạng xã hội**
        - 🎉 **Voucher tri ân** dành cho khách hàng thường xuyên
        """)
    elif segment == "Loyal":
        st.markdown("""
        ### 🎉 Chiến lược ưu đãi dành cho khách hàng Loyal

        - 🛍️ **Ưu đãi theo mốc mua hàng** dành riêng cho khách hàng thân thiết  
        - 🎂 **Khuyến mãi dịp lễ và sinh nhật** – gửi trực tiếp qua SMS hoặc Email  
        - 🎁 **Tặng voucher tri ân** khi khách hàng tham gia góp ý cải thiện dịch vụ
        """)
    elif segment == "Needs Attention":
        st.markdown("""
        ### 🎁 Gợi ý ưu đãi tăng tương tác với khách hàng Needs Attention

        - 💌 **Ưu đãi nhỏ (5% - 10%)** gửi qua SMS / Email  
        - 🎫 **Phiếu giảm giá** cho lần mua hàng tiếp theo  
        - 🎁 **Tặng quà** cho khách hàng tham gia khảo sát hoặc phản hồi
        """)
    elif segment == "Inactive":
        st.markdown("""
        ### ⏳ Gợi ý ưu đãi tăng tương tác với khách hàng Inactive

        - 🎁 **Ưu đãi giới hạn thời gian** hoặc **quà tặng đặc biệt**
        - 🎫 **Voucher giảm giá** cho khách hàng tiềm năng / trung thành
        """)
# Gợi ý chiến lược
def strategy_suggestions():
    st.image("images/suggestion.png", width=1200) 
    st.title("Gợi ý chiến lược")
    
    # Dữ liệu phân khúc khách hàng
    data = {
        "Tên Phân Khúc": ["👑 Champions", "💖 Loyal", "🕵️ Needs Attention", "💤 Inactive"],
        "Mô Tả": [
            "Khách hàng tốt nhất - mua thường xuyên và chi tiêu cao",
            "Khách hàng trung thành - mua hàng thường xuyên, bao gồm cả khách mới",
            "Khách hàng chưa mua gần đây nhưng vẫn có giá trị",
            "Khách hàng không còn tương tác - có mức độ tham gia rất thấp"
        ]
    }

    # Tạo DataFrame
    df = pd.DataFrame(data)

    # Hiển thị bảng trên Streamlit
    st.title("📝 Phân Khúc Khách Hàng")
    st.table(df)
    
    st.write("""
    Dựa trên dữ liệu phân cụm, chúng tôi sẽ gợi ý các chiến lược marketing phù hợp cho từng nhóm khách hàng.
    """)
        # Tạo chức năng lựa chọn dữ liệu
    data_option = st.radio("Chọn dữ liệu", ("Dữ liệu hiện có", "Tải dữ liệu mới"))
    data = None

    # Nếu người dùng chọn dữ liệu hiện có
    if data_option == "Dữ liệu hiện có":
        data = pd.read_csv("data/processed_data.csv")
    # Nếu người dùng chọn tải dữ liệu mới
    elif data_option == "Tải dữ liệu mới":
        upload_file = st.file_uploader("Tải lên dữ liệu kinh doanh (CSV)", type=["csv"], key="upload_4")

        if upload_file is not None:
            # Đọc và làm sạch dữ liệu
            data = pd.read_csv(upload_file)
    
    if data is not None:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce", dayfirst=True)

        # Tao RFM dataframe
        df_RFM_slider = rfm_transform_data(data)
        rfm_agg, df_RFM = rfm_segmentation(df_RFM_slider)
        st.write("Dữ liệu khách hàng:")
        st.write(df_RFM)
        st.write("Dữ liệu phân nhóm khách hàng:")
        st.write(rfm_agg)
        # st.write("Dữ liệu phân nhóm RFM:")
        # st.write(df_RFM_slider)
        
        # Tạo radio button để chọn phương án
        selection_method = st.radio("Chọn phương thức phân khúc", ("Theo mã khách hàng", "Theo RFM"))

        # Xử lý theo phương án đã chọn
        if selection_method == "Theo mã khách hàng":
            st.header("Chọn Mã Khách Hàng")
            customer_choices = df_RFM.index.tolist()
            selected_customer = st.selectbox("Chọn mã khách hàng", customer_choices)
            
            if selected_customer:
                segment = calculate_segment(df_RFM, customer_id=selected_customer)
                st.write(f"Khách hàng số {selected_customer} thuộc nhóm: {segment}")
                st.markdown(f"📊 Khách hàng số {selected_customer} thuộc nhóm: **🟢 {segment}**")
                display_strategy(segment)

        elif selection_method == "Theo RFM":
            st.header("Chọn theo RFM")
            recency = st.slider("Recency", min_value=df_RFM['Recency'].min(), max_value=df_RFM['Recency'].max(), value=int(df_RFM['Recency'].mean()))
            frequency = st.slider("Frequency", min_value=df_RFM['Frequency'].min(), max_value=df_RFM['Frequency'].max(), value=int(df_RFM['Frequency'].mean()))
            monetary = st.slider("Monetary", min_value=int(df_RFM['Monetary'].min()), max_value=int(df_RFM['Monetary'].max()), value=int(df_RFM['Monetary'].mean()))

            if recency is not None and frequency is not None and monetary is not None:
                cus_number, segment_rfm = calculate_segment(df_RFM_slider, recency=recency, frequency=frequency, monetary=monetary)
                if cus_number is not None:
                    st.write(f"Khách hàng số {cus_number} thuộc nhóm: {segment_rfm}")
                else:
                    st.write("Dữ liệu không có khách hàng nào với thông số này.")
                    st.markdown(f"📊 Dựa trên các giá trị RFM, nhóm khách hàng này là: **🟢 {segment_rfm}**")
                display_strategy(segment_rfm)