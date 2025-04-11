import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import plotly.express as px
from sklearn.preprocessing import RobustScaler
from sklearn.cluster import KMeans
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import squarify

random_state=42
cols_for_clustering = ['Recency', 'Frequency', 'Monetary']

def process_data(df_RFM):
    rfm_log = df_RFM.copy()
    # Apply log transformation to the columns for clustering
    rfm_log[cols_for_clustering] = df_RFM[cols_for_clustering].apply(np.log1p)
    
    # Scale the data using RobustScaler
    scaler = RobustScaler()
    rfm_scaled = rfm_log.copy()
    rfm_scaled[cols_for_clustering] = scaler.fit_transform(rfm_log[cols_for_clustering])
    return rfm_scaled

# Hàm tiện ích: vẽ evaluating clusters bar chart 
def plot_evaluating_clusters(dataframe, cluster_col, palette='Set2', title=''):
    plt.figure(figsize=(8, 6))
    ax = sns.countplot(data=dataframe, x=cluster_col, palette=palette)
    total = len(dataframe[cluster_col])
    for patch in ax.patches:
        count_value = patch.get_height()
        percentage = 100 * count_value / total
        x = patch.get_x() + patch.get_width() / 2 - 0.17
        y = patch.get_y() + count_value * 1.01
        # ax.annotate(f'{count_value:.0f}\n({percentage:.1f}%)', (x, y), size=12)
        ax.annotate(f'{percentage:.1f}%', (x, y))
    plt.title(title)
    plt.xlabel(cluster_col)
    plt.ylabel('Số lượng khách hàng')
    st.pyplot(plt)

def tree_map_plot(data, title):
    plt.clf() # Xóa figure cũ trước khi vẽ TreeMap
    fig = plt.gcf()
    ax = fig.add_subplot()
    fig.set_size_inches(14, 10)
    colors_dict = {'Cluster0':'yellow','Cluster1':'royalblue', 'Cluster2':'cyan',
               'Cluster3':'red', 'Cluster4':'purple'}

    if title == 'RFM Segments':
        colors_dict = {'Champions':'yellow','Inactive':'blue', 
                    'Loyal':'purple', 'Needs Attention':'red'}

    squarify.plot(sizes=data['Count'],
                text_kwargs={'fontsize':12,'weight':'bold', 'fontname':"sans serif"},
                color=colors_dict.values(),
                label=['{} \n{:.0f} days \n{:.0f} orders \n{:.0f} $ \n{:.0f} customers ({}%)'.format(*data.iloc[i])
                        for i in range(0, len(data))], alpha=0.5 )


    plt.title(title, fontsize=26,fontweight="bold")
    plt.axis('off')
    st.pyplot(fig)

def scatter_plot(data, color, hover):
    fig = px.scatter(data, x="RecencyMean", y="MonetaryMean", size="FrequencyMean", color=color,
    hover_name=hover, size_max=100, color_continuous_scale="Viridis")
    st.plotly_chart(fig)
    
def create_rfm_agg(df_RFM, groupby_col):
    rfm_agg = df_RFM.groupby(groupby_col).agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': ['mean', 'count']}).round(0)

    rfm_agg.columns = rfm_agg.columns.droplevel()
    rfm_agg.columns = ['RecencyMean','FrequencyMean','MonetaryMean', 'Count']
    rfm_agg['Percent'] = round((rfm_agg['Count']/rfm_agg.Count.sum())*100, 2)

    # Reset the index
    rfm_agg = rfm_agg.reset_index()
    return rfm_agg

def segment_customers(rfm_score):
    if rfm_score in ['333', '332', '323']:
        return 'Champions' 
    elif rfm_score in ['321', '322', '331', '232', '233', '312', '313', '311', '222', '223']:
        return 'Loyal' 
    elif rfm_score in ['213', '221', '123', '132', '133', '231', '212', '122', '131', '211']:
        return 'Needs Attention' 
    elif rfm_score in ['111', '112', '113', '121']:
        return 'Inactive' 

# Hàm phân cụm bằng Manual RFM
def rfm_segmentation(df_RFM):
    # Create labels for Recency, Frequency, Monetary
    r_labels = range(3, 0, -1) # số ngày tính từ lần cuối mua hàng lớn thì gán nhãn nhỏ, ngược lại thì nhãn lớn
    f_labels = range(1, 4)
    m_labels = range(1, 4)

    # Assign these labels to 3 equal percentile groups
    r_groups = pd.qcut(df_RFM['Recency'].rank(method='first'), q=3, labels=r_labels)
    f_groups = pd.qcut(df_RFM['Frequency'].rank(method='first'), q=3, labels=f_labels)
    m_groups = pd.qcut(df_RFM['Monetary'].rank(method='first'), q=3, labels=m_labels)
    
    # Create new columns R, F, M
    df_RFM = df_RFM.assign(R = r_groups.values, F = f_groups.values,  M = m_groups.values)
    def join_rfm(x): return str(int(x['R'])) + str(int(x['F'])) + str(int(x['M']))
    df_RFM['RFM_Segment'] = df_RFM.apply(join_rfm, axis=1)
    # Calculate RFM_Score
    df_RFM['RFM_Score'] = df_RFM[['R','F','M']].sum(axis=1)
    df_RFM['Segment'] = df_RFM['RFM_Segment'].apply(segment_customers)
    # Calculate average values for each RFM_Level, and return a size of each segment
    rfm_agg = create_rfm_agg(df_RFM, 'Segment')

    # Phân cụm
    return rfm_agg, df_RFM

# Hàm phân cụm bằng KMeans
def kmeans_segmentation(df_RFM, rfm_scaled, n_clusters=4):
    kmeans_4 = KMeans(n_clusters=n_clusters, random_state=random_state)
    labels_4 = kmeans_4.fit_predict(rfm_scaled[cols_for_clustering])
    df_RFM['Cluster_KM_4'] = labels_4  # Gán nhãn cụm vào dữ liệu gốc
    rfm_agg = create_rfm_agg(df_RFM, 'Cluster_KM_4')
    return rfm_agg, df_RFM

# Hàm phân cụm bằng GMM
def gmm_segmentation(df_RFM, rfm_scaled, n_components=5):
    gmm_5 = GaussianMixture(n_components = n_components, random_state = random_state)
    labels_5 = gmm_5.fit_predict(rfm_scaled[cols_for_clustering])
    df_RFM['Cluster_GMM_5'] = labels_5  # Gán nhãn cụm vào dữ liệu gốc
    rfm_agg = create_rfm_agg(df_RFM, 'Cluster_GMM_5')
    return rfm_agg, df_RFM

def rfm_transform_data(data):
    # Convert string to date, get max date of dataframe
    max_date = data['Date'].max().date()
    data['date_string'] = data['Date'].dt.strftime('%Y-%m-%d')

    Recency = lambda x : (max_date - x.max().date()).days
    Frequency  = lambda x: len(x.unique())
    Monetary = lambda x : round(sum(x), 2)

    df_RFM = data.groupby('Member_number').agg({'Date': Recency,
                                            'date_string': Frequency,
                                            'TotalPrice': Monetary })
    df_RFM.columns = ['Recency', 'Frequency', 'Monetary']
    # Descending Sorting
    df_RFM = df_RFM.sort_values('Monetary', ascending=False)
    return df_RFM

# Trang phân cụm khách hàng
def segmentation():
    st.image("images/customer.png", width=1000)
    st.title("Phân Cụm Khách Hàng")
    st.write("""Dữ liệu sau khi đã được làm sạch và xử lý sẽ được sử dụng để phân cụm khách hàng.
    Chúng tôi đã sử dụng các phương pháp phân cụm khác nhau như manual RFM, RFM kết hợp với KMeans và RFM kết hợp với GMM để phân 
    cụm khách hàng. Đối với RFM kết hợp với KMeans và GMM, chúng tôi đã sử dụng phương pháp log transformation 
    và RobustScaler để chuẩn hóa dữ liệu. Ngoài ra, chúng tôi còn sử dụng Elbow Method và Silhouette Score để đánh giá 
    số cụm tối ưu. Dưới đây là kết quả sau khi phân cụm khách hàng. 
    Bạn có thể tải lên dữ liệu bán hàng mới nhất đã được làm sạch theo đúng định dạng hoặc sử dụng dữ liệu hiện có để phân cụm khách hàng.""")
    
    # Tạo chức năng lựa chọn dữ liệu
    data_option = st.radio("Chọn dữ liệu", ("Dữ liệu hiện có", "Tải dữ liệu mới"))
    data = None

    # Nếu người dùng chọn dữ liệu hiện có
    if data_option == "Dữ liệu hiện có":
        data = pd.read_csv("data/processed_data.csv")
    # Nếu người dùng chọn tải dữ liệu mới
    elif data_option == "Tải dữ liệu mới":
        uploaded_file = st.file_uploader("Tải lên dữ liệu kinh doanh (CSV)", type=["csv"], key="upload_3")

        if uploaded_file is not None:
            # Đọc và làm sạch dữ liệu
            data = pd.read_csv(uploaded_file)
    
    if data is not None:
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce", dayfirst=True)
    
        # Hiển thị dữ liệu đã tải lên
        st.write(data)

        # Tao RFM dataframe
        df_RFM = rfm_transform_data(data)

        
        # Chọn phương pháp phân cụm
        st.markdown("<h4 style='font-size:22px; font-weight:bold;'>🔍 Chọn phương pháp phân cụm</h4>", unsafe_allow_html=True)
        clustering_method = st.selectbox("Chọn phương pháp phân cụm", ["Manual RFM", "KMeans", "GMM"], label_visibility="collapsed")

        # Thực hiện phân cụm theo phương pháp đã chọn
        if clustering_method == "Manual RFM":
            rfm_agg, df_RFM = rfm_segmentation(df_RFM)
            st.write("Phân cụm bằng RFM:")
            st.write(df_RFM)
            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Biểu đồ phân cụm:</h4>", unsafe_allow_html=True)
            plot_evaluating_clusters(df_RFM, 'Segment', palette='Set2',
                    title=f'Phân bố khách hàng theo cụm')
            
            # Thêm một khoảng cách giữa các biểu đồ để chúng không bị chồng lên nhau
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Tree map:</h4>", unsafe_allow_html=True)
            tree_map_plot(rfm_agg, "RFM Segments")
            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Biểu đồ phân tán:</h4>", unsafe_allow_html=True)
            scatter_plot(rfm_agg, "Segment", "Segment")
        elif clustering_method == "KMeans":
            rfm_scaled = process_data(df_RFM)
            rfm_agg, df_RFM = kmeans_segmentation(df_RFM, rfm_scaled)
            st.write("Phân cụm bằng Kmeans:")
            st.write(df_RFM)
            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Biểu đồ phân cụm:</h4>", unsafe_allow_html=True)
            plot_evaluating_clusters(df_RFM, 'Cluster_KM_4', palette='Set2',
                    title=f'Phân bố khách hàng theo cụm')
            
            # Thêm một khoảng cách giữa các biểu đồ để chúng không bị chồng lên nhau
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Tree map:</h4>", unsafe_allow_html=True)
            tree_map_plot(rfm_agg, "Cluster_KM_4")
            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Biểu đồ phân tán:</h4>", unsafe_allow_html=True)
            scatter_plot(rfm_agg, "Cluster_KM_4", "Cluster_KM_4")
        elif clustering_method == "GMM":
            rfm_scaled = process_data(df_RFM)
            rfm_agg, df_RFM = gmm_segmentation(df_RFM, rfm_scaled)
            st.write("Phân cụm bằng GMM:")
            st.write(df_RFM)
            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Biểu đồ phân cụm:</h4>", unsafe_allow_html=True)
            plot_evaluating_clusters(df_RFM, 'Cluster_GMM_5', palette='Set2',
                    title=f'Phân bố khách hàng theo cụm')
            
            # Thêm một khoảng cách giữa các biểu đồ để chúng không bị chồng lên nhau
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Tree map:</h4>", unsafe_allow_html=True)
            tree_map_plot(rfm_agg, "Cluster_GMM_5")
            st.markdown("<h4 style='font-size:22px; font-weight:bold;'>📊 Biểu đồ phân tán:</h4>", unsafe_allow_html=True)
            scatter_plot(rfm_agg, "Cluster_GMM_5", "Cluster_GMM_5")