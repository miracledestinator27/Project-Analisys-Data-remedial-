import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import urllib.request
import matplotlib.image as mpimg

sns.set(style='dark')

# Membaca data (pastikan Anda sudah memiliki file data yang sesuai)

customers_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/customers_dataset.csv")
geolocation_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/geolocation_dataset.csv")
order_items_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/order_items_dataset.csv")
order_payments_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/order_payments_dataset.csv")
order_reviews_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/order_reviews_dataset.csv")
orders_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/orders_dataset.csv")
category_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/product_category_name_translation.csv")
product_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/products_dataset.csv")
sellers_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/sellers_dataset.csv")

# --- Data Processing ---
order_items_df['shipping_limit_date'] = pd.to_datetime(order_items_df['shipping_limit_date'])
order_items_df['month'] = order_items_df['shipping_limit_date'].dt.strftime('%B')
order_items_df['year'] = order_items_df['shipping_limit_date'].dt.year
order_items_df['month_num'] = order_items_df['shipping_limit_date'].dt.month

# Mengelompokkan data berdasarkan tahun, bulan, dan menghitung total penjualan per bulan
monthly_sales_df = order_items_df.groupby(['year', 'month_num', 'month']).agg({
    "price": "sum",
    "freight_value": "sum",
    "order_id": "nunique"  # Menghitung jumlah order unik
}).reset_index()

# Streamlit header
st.header('E-commerce Dashboard')



def default_plot(ax, spines):
    ax = plt.gca()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    ax.get_yaxis().set_tick_params(direction='out')
    ax.get_xaxis().set_tick_params(direction='out')

    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 10))  # outward by 10 points

    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    if 'right' in spines:
        ax.yaxis.set_ticks_position('right')
    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')

    return ax

# --- Contoh data (ganti ini dengan data aslimu) ---
# Pastikan struktur mirip dengan yang digunakan di kode kamu
data = {
    'customer_state': ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC'],
    'payment_value_mean': [250, 220, 190, 210, 260, 230],
    'ci_low': [230, 200, 170, 190, 240, 210],
    'ci_hi': [270, 240, 210, 230, 280, 250]
}
customer_regions = pd.DataFrame(data)
customer_regions = customer_regions.sort_values(by='payment_value_mean')

# --- Plot menggunakan matplotlib ---
fig, ax = plt.subplots(figsize=(12, 4))
ax = default_plot(ax, ['left', 'bottom'])
plt.xticks(rotation=30)
plt.xlabel('Kota')
plt.ylabel('Rata-rata Transaksi')
plt.xlim(-0.5, len(customer_regions) - 0.5)
plt.ylim(min(customer_regions['ci_low']) - 10, max(customer_regions['ci_hi']) + 10)

# Plot scatter dan error bars
plt.scatter(
    customer_regions['customer_state'],
    customer_regions['payment_value_mean'],
    s=100,
    c=customer_regions['payment_value_mean'],
    cmap='viridis'
)
plt.vlines(
    customer_regions['customer_state'],
    customer_regions['ci_low'],
    customer_regions['ci_hi'],
    lw=0.5,
    colors='gray'
)
plt.tight_layout()

# --- Tampilkan di Streamlit ---
st.title("Visualisasi Rata-rata Transaksi per Kota")
st.pyplot(fig)

# --- Judul Halaman ---
st.title("Top 10 Kategori Produk Terbanyak")

# --- Contoh Data (ganti dengan data aslimu) ---
data = {
    "product_category_name": [
        "eletronicos", "beleza_saude", "moveis_decoracao", "esporte_lazer",
        "informatica_acessorios", "brinquedos", "telefonia", "relogios_presentes",
        "perfumaria", "automotivo", "papelaria", "construcao_ferramentas"
    ],
    "total_orders": [5200, 4300, 3900, 3700, 3400, 3100, 3000, 2700, 2500, 2300, 2200, 2100]
}

category_counts = pd.DataFrame(data)

# --- Urutkan dan ambil 10 teratas ---
top_categories = category_counts.sort_values(by="total_orders", ascending=False).head(10)

# --- Tampilkan tabel di Streamlit ---
st.subheader("Top 10 Kategori Produk Terbanyak (Tabel)")
st.dataframe(top_categories.reset_index(drop=True))

# --- Visualisasi Bar Chart ---
st.subheader("Visualisasi Top 10 Kategori Produk Terbanyak")

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    x="product_category_name",
    y="total_orders",
    data=top_categories,
    palette="viridis",
    ax=ax
)
ax.set_title("Top 10 Kategori Produk Terbanyak (Jumlah Order)")
ax.set_xlabel("Kategori Produk")
ax.set_ylabel("Jumlah Order")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# --- Tampilkan di Streamlit ---
st.pyplot(fig)


st.title("🗺️ E-Commerce Geolocation & Purchase Analysis Dashboard")

st.markdown("""
Dashboard ini menampilkan hasil analisis gabungan antara **orders, customers, dan geolocation data**  
dengan visualisasi yang terintegrasi dalam format Streamlit.
""")


np.random.seed(42)
geolocation_df = pd.DataFrame({
    'geolocation_zip_code_prefix': np.random.randint(10000, 99999, 100),
    'geolocation_city': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'BA', 'SC'], 100),
    'geolocation_state': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'BA', 'SC'], 100),
    'geolocation_lat': np.random.uniform(-33.5, 5, 100),
    'geolocation_lng': np.random.uniform(-73.8, -34.5, 100)
})
customers_df = pd.DataFrame({
    'customer_id': [f"C{i}" for i in range(1, 51)],
    'customer_unique_id': [f"U{i}" for i in range(1, 51)],
    'customer_zip_code_prefix': np.random.choice(geolocation_df['geolocation_zip_code_prefix'], 50)
})
orders_df = pd.DataFrame({
    'order_id': [f"O{i}" for i in range(1, 100)],
    'customer_id': np.random.choice(customers_df['customer_id'], 99),
    'order_status': np.random.choice(['delivered', 'shipped', 'cancelled'], 99)
})

# ==============================
# 🏙️ GELOCATION ANALYSIS
# ==============================
st.header("🏙️ Analisis Kode Pos & State")

col1, col2 = st.columns(2)

with col1:
    other_state_geolocation = (
        geolocation_df
        .groupby(['geolocation_zip_code_prefix'])['geolocation_state']
        .nunique()
        .reset_index(name='count')
    )
    multi_state_zip = other_state_geolocation[other_state_geolocation['count'] >= 2]
    st.metric("Jumlah kode pos di lebih dari 1 state", multi_state_zip.shape[0])
    st.dataframe(multi_state_zip)

with col2:
    min_state = (
        geolocation_df
        .groupby(['geolocation_zip_code_prefix', 'geolocation_state'])
        .size()
        .reset_index(name='count')
        .drop_duplicates(subset='geolocation_zip_code_prefix')
        .drop('count', axis=1)
    )
    st.write("**State representatif per kode pos:**")
    st.dataframe(min_state.head(10))

# ==============================
# 🔗 MERGE DATA ORDERS + CUSTOMERS + GEOLOCATION
# ==============================
st.header("🔗 Penggabungan Data Orders, Customers, dan Geolocation")

orders_customers_geolocation_df = (
    orders_df
    .merge(customers_df, on='customer_id', how='left')
    .merge(
        geolocation_df,
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )
)

st.dataframe(orders_customers_geolocation_df.head())

# ==============================
# 📊 PURCHASES BY STATE
# ==============================
st.header("📊 Jumlah Pembelian per State")

purchases_by_state = (
    orders_customers_geolocation_df
    .groupby('geolocation_state')['order_id']
    .nunique()
    .reset_index()
    .rename(columns={'geolocation_state': 'State', 'order_id': 'Total Orders'})
)

locations_fewest_purchases = purchases_by_state.sort_values(by='Total Orders', ascending=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("📉 State dengan Pembelian Paling Sedikit")
    st.dataframe(locations_fewest_purchases.head(10))

with col4:
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x='State', y='Total Orders', data=purchases_by_state, palette='viridis', ax=ax)
    ax.set_title("Jumlah Pembelian per State")
    ax.set_xlabel("State")
    ax.set_ylabel("Total Orders")
    st.pyplot(fig)

# ==============================
# 🧭 CUSTOMERS SILVER & GEOLOCATION SILVER
# ==============================
st.header("🧭 Customers Silver Dataset")

customers_silver = customers_df.merge(
    geolocation_df,
    left_on='customer_zip_code_prefix',
    right_on='geolocation_zip_code_prefix',
    how='inner'
)

geolocation_silver = (
    geolocation_df
    .groupby(['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state'])[['geolocation_lat', 'geolocation_lng']]
    .median()
    .reset_index()
)
geolocation_silver = geolocation_silver.merge(
    min_state,
    on=['geolocation_zip_code_prefix', 'geolocation_state'],
    how='inner'
)

st.dataframe(customers_silver.head(10))

# ==============================
# 🗺️ MAP VISUALIZATION (CUSTOMERS)
# ==============================
st.header("🗺️ Peta Persebaran Pelanggan di Brasil")
def plot_brazil_map(data):
    # Ambil gambar peta Brasil
    url = 'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
    with urllib.request.urlopen(url) as u:
        brazil = mpimg.imread(u, 'jpg')

    # 🧭 Batas koordinat data pelanggan (scatter)
    data_lon_min, data_lon_max = data["geolocation_lng"].min(), data["geolocation_lng"].max()
    data_lat_min, data_lat_max = data["geolocation_lat"].min(), data["geolocation_lat"].max()

    # 🗺️ Batas peta dibuat lebih lebar dari data
    # Tambahkan margin kiri/kanan/atas/bawah agar peta tampak lebih luas
    lon_margin = 13
    lat_margin = 10

    map_lon_min = data_lon_min - lon_margin
    map_lon_max = data_lon_max + lon_margin
    map_lat_min = data_lat_min - lat_margin
    map_lat_max = data_lat_max + lat_margin

    # Buat plot
    fig, ax = plt.subplots(figsize=(14, 14))  
    ax.imshow(brazil, extent=[map_lon_min, map_lon_max, map_lat_min, map_lat_max], zorder=1)

    # Scatter pelanggan hanya di area data aslinya
    ax.scatter(
        data["geolocation_lng"],
        data["geolocation_lat"],
        s=20,
        alpha=0.8,
        color='yellow',
        edgecolor='black',
        linewidth=0.5,
        zorder=2
    )

    # Atur batas tampilan (fokus ke area data saja)
    ax.set_xlim(map_lon_min, map_lon_max)
    ax.set_ylim(map_lat_min, map_lat_max)

    # Rasio aspek disesuaikan agar proporsional (lebih lebar)
    ax.set_aspect('0.6', adjustable='box')

    # Label dan tampilan
    ax.set_xlabel("Longitude", fontsize=10)
    ax.set_ylabel("Latitude", fontsize=10)
    ax.set_title("🗺️ Peta Brasil (Latar Lebih Lebar dari Scatter)", fontsize=16)
    ax.grid(False)
    plt.tight_layout()
    return fig


# =====================================
# 🔹 Contoh Data Dummy
# =====================================
np.random.seed(36)
customers_silver = pd.DataFrame({
    'customer_unique_id': [f'U{i}' for i in range(50)],
    'geolocation_lat': np.random.uniform(-42, 38, 50),
    'geolocation_lng': np.random.uniform(-73, -33,50)
})

# =====================================
# 📊 Streamlit Layout
# =====================================
st.set_page_config(page_title="Peta Pelanggan Brasil", layout="wide")
st.title("🗺️ Visualisasi Peta Lebih Lebar dari Scatter")
st.markdown("""
Berikut visualisasi peta Brasil di mana **gambar peta dibuat lebih lebar dari area sebaran titik pelanggan**.  
Hal ini membantu menjaga konteks geografis dan memberikan ruang visual di sekitar data.
""")

fig_map = plot_brazil_map(customers_silver.drop_duplicates(subset='customer_unique_id'))
st.pyplot(fig_map)


































































































































































