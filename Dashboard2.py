import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import streamlit as st

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
