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


st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_year'] = orders_df['order_purchase_timestamp'].dt.year

with st.sidebar:
    st.image(
        "https://spiralcute.com/characters/mofusand/en/img/main.jpg",
        width=120
    )
    st.title("E-Commerce Dashboard")

    st.markdown("---")
    st.subheader(" Filter Waktu")

    # Pastikan kolom tanggal ada di orders_df
    if 'order_purchase_timestamp' in orders_df.columns:
        orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'], errors='coerce')
        min_date = orders_df['order_purchase_timestamp'].min()
        max_date = orders_df['order_purchase_timestamp'].max()

        start_date, end_date = st.date_input(
            label="Pilih Rentang Waktu",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

        # Filter data berdasarkan tanggal
        filtered_orders = orders_df[
            (orders_df['order_purchase_timestamp'] >= pd.to_datetime(start_date)) &
            (orders_df['order_purchase_timestamp'] <= pd.to_datetime(end_date))
        ]
    else:
        st.warning("⚠️ Kolom tanggal tidak ditemukan di dataset orders.")
        filtered_orders = orders_df.copy()

    st.markdown("---")
    st.subheader(" Filter Lokasi")

    # Filter state pelanggan
    unique_states = sorted(customers_df['customer_state'].unique())
    selected_states = st.multiselect(
        "Pilih State Pelanggan:",
        options=unique_states,
        default=unique_states[:5]  # tampilkan 5 state awal sebagai default
    )

    filtered_customers = customers_df[customers_df['customer_state'].isin(selected_states)]

    st.markdown("---")
    st.subheader("Pilih Tampilan Dashboard")

    dashboard_options = [
        "Rata-rata Transaksi per Kota",
        "Top 10 Kategori Produk",
        "Analisis Geolokasi & Pembelian",
        "Peta Sebaran Pelanggan"
    ]
    selected_dashboard = st.radio(
        "Tampilkan Bagian:",
        dashboard_options,
        index=0
    )

    st.markdown("---")
    st.info("Gunakan filter di atas untuk mempersempit analisis dan memperbarui visualisasi dashboard.")


# Streamlit header
st.title('E-commerce Dashboard')



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
st.header("1. Visualisasi Rata-rata Transaksi per Kota")
st.markdown("""
Dashboard ini menampilkan hasil Visualisasi Rata-rata transaksi pembelian per kota di Brazil
""")
st.pyplot(fig)

# --- Judul Halaman ---
st.header("2. Visualisasi Top 10 Kategori Produk Terbanyak")
st.markdown("""
Dashboard ini menampilkan hasil Visualisasi dari Kategori Produk yang paling banyak dibeli.
""")

# --- Contoh Data (ganti dengan data aslimu) ---
data = {
    "product_category_name": [
        "cama_mesa_banho", "beleza_saude", "moveis_decoracao", "esporte_lazer",
        "informatica_acessorios", "brinquedos", "telefonia", "relogios_presentes",
        "perfumaria", "automotivo", "papelaria", "construcao_ferramentas"
    ],
    "total_orders": [5200, 4300, 3900, 3700, 3400, 3100, 3000, 2700, 2500, 2300, 2200, 2100]
}

category_counts = pd.DataFrame(data)

# --- Urutkan dan ambil 10 teratas ---
top_categories = category_counts.sort_values(by="total_orders", ascending=False).head(10)

# --- Tampilkan tabel di Streamlit ---
st.subheader("Tabel")
st.dataframe(top_categories.reset_index(drop=True))

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






st.caption('Copyright (C) Mira Destiyanti 2025')














































































































































































































































