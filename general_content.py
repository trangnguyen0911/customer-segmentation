import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def general_content():
    st.image("images/shop.png", width=1200) 
    st.title("Chào mừng đến với dự án phân tích dữ liệu bán hàng")
    
    # Nội dung Business Objective
    st.subheader("Mục tiêu kinh doanh")
    st.write("""
    Cửa hàng X là một cửa hàng tiện lợi ở Mỹ, chủ yếu bán các sản phẩm thiết yếu cho khách hàng như rau, củ, quả, thịt, cá, trứng, sữa, nước giải khát... 
    Khách hàng của cửa hàng là khách hàng mua lẻ.
    
    Chủ cửa hàng X mong muốn có thể bán được nhiều hàng hóa hơn cũng như giới thiệu sản phẩm đến đúng đối tượng khách hàng, chăm sóc và làm hài lòng khách hàng.
    """)
    
    # Nội dung về cách giải quyết mục tiêu kinh doanh
    st.subheader("Giải pháp")
    st.write("""
    Để đạt được mục tiêu trên, chúng tôi đã thực hiện các bước sau:
    1. Phân tích dữ liệu bán hàng để tìm hiểu về hành vi mua sắm của khách hàng.
    2. Phân khúc khách hàng thành các nhóm khác nhau dựa trên hành vi mua sắm của họ.
    3. Đưa ra các chiến lược tiếp thị và bán hàng dựa trên phân khúc khách hàng.
    
    Để phân khúc khách hàng, chúng tôi đã sử dụng phương pháp manual RFM, 
    RFM kết hợp với Kmeans và RFM kết hợp với GMM. Sau đó, chúng tôi đã lựa chọn
    phương pháp manual RFM để phân khúc khách hàng vì phương pháp này phản ánh rõ rệt 
    về hành vi mua sắm của khách hàng nhất. Dưới đây là phần tìm hiểu về dữ liệu bán hàng của cửa hàng X. 
    Bạn có thể tải lên dữ liệu bán hàng mới nhất theo đúng định dạng để tìm hiểu về hành vi mua sắm của khách hàng 
    hoặc sử dụng dữ liệu hiện có.""")

    # Nội dung về dữ liệu
    st.subheader("Tìm hiểu về dữ liệu")
    # Tạo chức năng lựa chọn dữ liệu
    data_option = st.radio("Chọn dữ liệu", ("Dữ liệu hiện có", "Tải dữ liệu mới"))
    data = None
    
    # Nếu người dùng chọn dữ liệu hiện có
    if data_option == "Dữ liệu hiện có":
        transactions = "data/Transactions.csv"
        products = "data/Products_with_Categories.csv"
        data = clean_data(products, transactions)
    elif data_option == "Tải dữ liệu mới":
        # Chức năng tải lên tệp dữ liệu
        uploaded_file_product = st.file_uploader("Tải lên dữ liệu sản phẩm (CSV)", type=["csv"], key="upload_1")
        uploaded_file_transaction = st.file_uploader("Tải lên dữ liệu giao dịch (CSV)", type=["csv"], key="upload_2")
    
        if uploaded_file_product is None or uploaded_file_transaction is None:
            st.warning("Vui lòng tải lên cả hai tệp dữ liệu sản phẩm và giao dịch để tiếp tục.")
            return       
        elif uploaded_file_product is not None and uploaded_file_transaction is not None:
            # Đọc dữ liệu từ tệp CSV
            data = clean_data(uploaded_file_product, uploaded_file_transaction)
            
    if data is not None:
        st.write("Dữ liệu đã tải lên:")
        st.write(data)

        st.subheader("Một số thông tin cơ bản của dữ liệu")
        st.write("Số lượng sản phẩm:", data['productId'].nunique())
        st.write("Số lượng khách hàng:", data['Member_number'].nunique())
        st.write("Số lượng nhóm sản phẩm:", data['Category'].nunique())
        st.write("Số lượng ngày giao dịch:", data['Date'].nunique())
        st.write("Số lượng sản phẩm bán ra:", data['items'].sum())
        st.write("Tổng doanh thu:", data['TotalPrice'].sum())
        st.write("Giá trị đơn hàng trung bình:", data['TotalPrice'].mean())
        st.write("Giá trị đơn hàng lớn nhất:", data['TotalPrice'].max())
        st.write("Giá trị đơn hàng nhỏ nhất:", data['TotalPrice'].min())
        st.write("Số lượng sản phẩm bán ra lớn nhất:", data['items'].max())
        st.write("Số lượng sản phẩm bán ra nhỏ nhất:", data['items'].min())
        
        # Vẽ biểu đồ
        plot_data(data)
        
        # Tải xuống dữ liệu đã xử lý
        st.subheader("Tải xuống dữ liệu đã xử lý")
        csv = data.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "processed_data.csv", "text/csv", key='download-csv')
        st.write("Dữ liệu đã được xử lý và có thể tải xuống dưới dạng tệp CSV.")

        
# Hàm clean dữ liệu
def clean_data(product_data, transaction_data):
    transactions = pd.read_csv(transaction_data)
    products = pd.read_csv(product_data)
    data = pd.merge(transactions, products, on='productId', how='left')
    # Loại bỏ hàng có giá trị thiếu
    data = data.dropna()  
    # Loại bỏ dòng trùng lặp
    data = data.drop_duplicates()  
    # Convert datetime format for column 'Date'
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce", dayfirst=True)
    data = data[data['price'] >= 0]  # Loại bỏ price âm
    # Tạo cột mới bằng cách nhân giá và số lượng
    data['TotalPrice'] = data['price'] * data['items']
    data['Month'] = data['Date'].dt.month # Tháng của giao dịch
    data['Weekday'] = data['Date'].dt.day_name() # Tên ngày trong tuần
    
    return data

def plot_data(data):
    # Vẽ biểu đồ 1: Biểu đồ top 10 sản phẩm có doanh thu cao nhất
    st.subheader("Biểu đồ phân phối doanh thu theo sản phẩm")
    top_products = data.groupby('productName')['TotalPrice'].sum().reset_index()
    top_products = top_products.sort_values(by='TotalPrice', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='TotalPrice', y='productName', data=top_products, ax=ax, palette="mako", hue='productName', legend=False)
    ax.set_title("Top 10 sản phẩm có doanh thu cao nhất")
    ax.set_xlabel("Doanh thu")
    ax.set_ylabel("Tên sản phẩm")
    st.pyplot(fig)

    # Vẽ biểu đồ 2: Biểu đồ phân phối doanh thu theo ngày trong tuần (Weekday)
    st.subheader("Biểu đồ doanh thu theo ngày trong tuần")
    weekday_sales = data.groupby('Weekday')['TotalPrice'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='Weekday', y='TotalPrice', data=weekday_sales, ax=ax, palette="viridis", hue='Weekday', legend=False)
    ax.set_title("Doanh thu theo ngày trong tuần")
    st.pyplot(fig)

    # Vẽ biểu đồ 3: Biểu đồ doanh thu theo tháng (Month)
    st.subheader("Biểu đồ doanh thu theo tháng")
    monthly_sales = data.groupby('Month')['TotalPrice'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='Month', y='TotalPrice', data=monthly_sales, ax=ax, marker='o')
    ax.set_title("Doanh thu theo tháng")
    st.pyplot(fig)

    # Vẽ biểu đồ 4: Biểu đồ phân phối số lượng sản phẩm bán ra theo tháng
    st.subheader("Biểu đồ phân phối số lượng sản phẩm bán ra theo tháng")
    monthly_items = data.groupby('Month')['items'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='Month', y='items', data=monthly_items, ax=ax, marker='o')
    ax.set_title("Số lượng sản phẩm bán ra theo tháng")
    st.pyplot(fig)
    
    # Vẽ biểu đồ 5: Biểu đồ top 10 sản phẩm bán chạy nhất trong tháng có doanh thu cao nhất
    st.subheader("Top 10 sản phẩm bán chạy nhất trong tháng có doanh thu cao nhất")
    top_month = data.groupby('Month')['TotalPrice'].sum().idxmax()
    top_month_data = data[data['Month'] == top_month]
    top_products = top_month_data.groupby('productName')['items'].sum().reset_index()
    top_products = top_products.sort_values(by='items', ascending=False).head(10)   
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='items', y='productName', data=top_products, ax=ax, palette="mako", hue='productName', legend=False)
    ax.set_title(f"Top 10 sản phẩm bán chạy nhất trong tháng {top_month}")
    st.pyplot(fig)
    
    # Vẽ biểu đồ 6: Biểu đồ top 10 sản phẩm bán chạy nhất
    st.subheader("Top 10 sản phẩm bán chạy nhất")
    top_products_all = data.groupby('productName')['items'].sum().reset_index()
    top_products_all = top_products_all.sort_values(by='items', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='items', y='productName', data=top_products_all, ax=ax, palette="mako", hue='productName', legend=False)
    ax.set_title("Top 10 sản phẩm bán chạy nhất")
    st.pyplot(fig)
    
    # Vẽ biểu đồ 7: Biểu đồ doanh thu theo danh mục sản phẩm
    st.subheader("Doanh thu theo danh mục sản phẩm")
    # sắp xếp theo thứ tự doanh thu giảm dần
    category_sales = data.groupby('Category')['TotalPrice'].sum().reset_index()
    category_sales = category_sales.sort_values(by='TotalPrice', ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='TotalPrice', y='Category', data=category_sales, ax=ax, palette="Blues_d", hue='Category', legend=False)
    ax.set_title("Doanh thu theo danh mục sản phẩm")
    st.pyplot(fig)