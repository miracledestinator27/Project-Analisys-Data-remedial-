import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st
import urllib.request
import matplotlib.image as mpimg

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

monthly_sales_df['month_year'] = monthly_sales_df['month'] + ' ' + monthly_sales_df['year'].astype(str)
monthly_sales_df.sort_values(by=['year', 'month_num'], inplace=True)

# --- Streamlit Dashboard ---

# Streamlit header
st.header('E-commerce Dashboard')

st.subheader('Monthly Sales Data')

st.dataframe(monthly_sales_df)

# Fungsi untuk memformat plot (dari kode asli)
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

# --- Judul Halaman ---
st.title("Sebaran Pelanggan di Brasil")

st.markdown("""
Aplikasi ini melakukan analisis **geolokasi pelanggan** dan **aktivitas pembelian** berdasarkan data:
- `orders_df`
- `customers_df`
- `geolocation_df`
""")

# ==============================
# 🗂️ UPLOAD DATAFRAME
# ==============================
st.subheader("📤 Upload Dataset")

orders_file = st.file_uploader("Upload file orders.csv", type=["csv"])
customers_file = st.file_uploader("Upload file customers.csv", type=["csv"])
geolocation_file = st.file_uploader("Upload file geolocation.csv", type=["csv"])

if orders_file and customers_file and geolocation_file:
    # Membaca data
    orders_df = pd.read_csv(orders_file)
    customers_df = pd.read_csv(customers_file)
    geolocation_df = pd.read_csv(geolocation_file)

    st.success("✅ Semua file berhasil dimuat!")

    # ==============================
    # 🔍 1. Analisis kode pos yang muncul di lebih dari satu state
    # ==============================
    st.subheader("🏙️ Analisis State Unik per Kode Pos")

    other_state_geolocation = (
        geolocation_df
        .groupby(['geolocation_zip_code_prefix'])['geolocation_state']
        .nunique()
        .reset_index(name='count')
    )

    multi_state_zip = other_state_geolocation[other_state_geolocation['count'] >= 2]

    st.write(f"Jumlah kode pos yang muncul di lebih dari satu state: **{multi_state_zip.shape[0]}**")
    st.dataframe(multi_state_zip)

    # ==============================
    # 🗺️ 2. Ambil state representatif per kode pos
    # ==============================
    st.subheader("🗺️ State Representatif per Kode Pos")

    min_state = (
        geolocation_df
        .groupby(['geolocation_zip_code_prefix', 'geolocation_state'])
        .size()
        .reset_index(name='count')
        .drop_duplicates(subset='geolocation_zip_code_prefix')
        .drop('count', axis=1)
    )
    st.dataframe(min_state.head(10))

    # ==============================
    # 🔗 3. Merge orders, customers, dan geolocation
    # ==============================
    st.subheader("🔗 Menggabungkan Data Orders, Customers, dan Geolocation")

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
    st.write("✅ Dataframe hasil merge:")
    st.dataframe(orders_customers_geolocation_df.head())

    # ==============================
    # 📊 4. Hitung pembelian per state
    # ==============================
    st.subheader("📊 Jumlah Pembelian per State")

    purchases_by_state = (
        orders_customers_geolocation_df
        .groupby('customer_state')['order_id']
        .nunique()
        .reset_index()
    )

    locations_fewest_purchases = purchases_by_state.sort_values(by='order_id', ascending=True)

    st.write("📉 State dengan jumlah pembelian paling sedikit:")
    st.dataframe(locations_fewest_purchases.head(10))

    # ==============================
    # 🧭 5. Membuat Data Customers Silver
    # ==============================
    st.subheader("🧭 Membuat Dataset Customers Silver")

    customers_silver = customers_df.merge(
        geolocation_df,
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='inner'
    )

    # ==============================
    # 🪙 6. Membuat Dataset Geolocation Silver
    # ==============================
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

    # Hitung state dominan untuk setiap prefix
    min_state = (
        geolocation_df
        .groupby(['geolocation_zip_code_prefix', 'geolocation_state'])
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
        .drop_duplicates('geolocation_zip_code_prefix')
        .drop('count', axis=1)
    )

    st.write("📍 State dominan per kode pos:")
    st.dataframe(min_state.head())

    # ==============================
    # 💾 7. Simpan hasil akhir
    # ==============================
    st.subheader("💾 Simpan Dataset Hasil (Customers Silver)")

    csv_data = customers_silver.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Customers Silver CSV",
        data=csv_data,
        file_name="customers_silver.csv",
        mime="text/csv"
    )

    st.success("Proses selesai ✅ — Semua data berhasil diproses!")

else:
    st.info("Silakan upload ketiga file dataset (orders, customers, dan geolocation) untuk memulai analisis.")
    st.pyplot(fig)















