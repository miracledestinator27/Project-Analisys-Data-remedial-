import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import streamlit as st
from scipy import stats as sps   


sns.set(style='dark')
st.title("E-commerce Dashboard")

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

with st.sidebar:
    st.image(
        "https://spiralcute.com/characters/mofusand/en/img/main.jpg",
        width=120
    )
    st.title("E-Commerce Dashboard")

    st.markdown("---")
    st.subheader(" Filter Waktu")

st.header("1. Analisis Perilaku Konsumen & Transaksi")
st.write("Dashboard ini menampilkan analisis spending customer, confidence interval, "
         "serta pola transaksi berdasarkan waktu, kota, dan kategori produk.")


customers_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/customers_dataset.csv")
geolocation_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/geolocation_dataset.csv")
order_items_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/order_items_dataset.csv")
order_payments_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/order_payments_dataset.csv")
order_reviews_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/order_reviews_dataset.csv")
orders_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/orders_dataset.csv")
category_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/product_category_name_translation.csv")
product_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/products_dataset.csv")
sellers_df = pd.read_csv("E-commerce-public-dataset/E-Commerce Public Dataset/sellers_dataset.csv")


# Timestamp → datetime
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_year'] = orders_df['order_purchase_timestamp'].dt.year

st.sidebar.header("Tabel Nilai Transaksi")

min_year, max_year = int(orders_df['order_year'].min()), int(orders_df['order_year'].max())

year_range = st.sidebar.slider(
    "Pilih Rentang Tahun:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter berdasarkan tahun
filtered_orders = orders_df[
    (orders_df['order_year'] >= year_range[0]) &
    (orders_df['order_year'] <= year_range[1])
]

st.sidebar.write(f"Rentang Tahun Aktif: **{year_range[0]} - {year_range[1]}**")

pay_ord_cust = (
    filtered_orders
    .merge(order_payments_df, on="order_id", how="outer")
    .merge(customers_df, on="customer_id", how="outer")
)

# =======================
# A. Customer Spending Analysis
# =======================

customer_spent = (
    pay_ord_cust.groupby('customer_unique_id')
    .agg({'payment_value': 'sum'})
    .sort_values('payment_value', ascending=False)
)

customer_mean = customer_spent['payment_value'].mean()
customer_sem = sps.sem(customer_spent['payment_value'])

ci_low, ci_high = sps.t.interval(
    0.95,
    loc=customer_mean,
    scale=customer_sem,
    df=len(customer_spent) - 1
)

# =======================
# B. Customer Spending per Kota wilayah
# =======================
st.header("Analisis Pengeluaran berdasarkan Kota")

customer_regions = (
    pay_ord_cust.groupby("customer_state")
    .agg({
        'payment_value': ['mean', 'std'],
        'customer_unique_id': 'count'
    })
)

customer_regions.reset_index(inplace=True)

# Hitung CI per state
cis = sps.t.interval(
    0.95,
    loc=customer_regions['payment_value']['mean'],
    scale=customer_regions['payment_value']['std'] /
          np.sqrt(customer_regions['customer_unique_id']['count']),
    df=customer_regions['customer_unique_id']['count'] - 1
)

customer_regions["ci_low"] = cis[0]
customer_regions["ci_high"] = cis[1]

# ---------- Plot ----------
st.subheader("Rata-rata Transaksi per Kota")

fig, ax = plt.subplots(figsize=(12, 4))
plot = customer_regions.sort_values(('payment_value', 'mean'))

ax.bar(
    plot['customer_state'],
    plot['payment_value']['mean']
)

plt.xticks(rotation=30)
plt.xlabel("State")
plt.ylabel("Rata-rata Transaksi")
plt.tight_layout()

st.pyplot(fig)

# =======================
# C. Rata-rata Transaksi per Kota per Tahun
# =======================
st.header("Tabel Rata-rata Nilai Transaksi per Kota per Tahun")

avg_transaction_city_year = (
    pay_ord_cust.groupby(['order_year', 'customer_city'])
    .agg(
        avg_transaction_value=('payment_value', 'mean'),
        transaction_count=('payment_value', 'count')
    )
    .reset_index()
)

st.dataframe(avg_transaction_city_year.head(20))

# =======================
# Top 10 Kota dengan Rata-rata Transaksi Tertinggi
# =======================
st.header(" Top 10 Kota dengan Rata-rata Transaksi Tertinggi")

avg_city = (
    pay_ord_cust.groupby('customer_city')
    .agg({'payment_value': 'mean'})
    .sort_values('payment_value', ascending=False)
)

top_10_cities = avg_city.head(10).index

st.write("Berikut adalah top 10 kota dengan transaksi rata-rata tertinggi:")

st.dataframe(avg_city.head(10))

# =======================
#  E. Tren Per Tahun per Kategori Produk untuk Top 10 Kota
# =======================
st.header(" Tren Kategori Produk di Top 10 Kota")

# merge items + product category
items_prod = order_items_df.merge(product_df, on='product_id', how='left')

full_df = (
    pay_ord_cust.merge(
        items_prod[['order_id', 'product_id', 'product_category_name']],
        on='order_id', how='left'
    )
)

filtered_df = full_df[full_df['customer_city'].isin(top_10_cities)]

trend_city_cat_year = (
    filtered_df.groupby(['order_year', 'customer_city', 'product_category_name'])
    .agg(
        avg_transaction=('payment_value', 'mean'),
        total_transactions=('payment_value', 'count')
    )
    .reset_index()
)

# ---------- Plot Tren ----------
st.subheader("Tren Rata-rata Transaksi per Kategori per Tahun (Top 10 Kota)")

fig2, ax2 = plt.subplots(figsize=(18, 7))

for year in sorted(trend_city_cat_year['order_year'].unique()):
    subset = trend_city_cat_year[trend_city_cat_year['order_year'] == year]

    ax2.bar(
        subset['product_category_name'] + " (" + subset['customer_city'] + ")",
        subset['avg_transaction'],
        alpha=0.7,
        label=f"Tahun {year}"
    )

plt.xticks(rotation=90)
plt.xlabel("Kategori Produk (per Kota)")
plt.ylabel("Rata-rata Nilai Transaksi")
plt.title("Top 10 Kota: Tren Rata-rata Transaksi per Kategori Produk per Tahun")
plt.legend()
plt.tight_layout()

st.pyplot(fig2)
st.subheader("Ringkasan")
st.write(f"""
- **Rata-rata pengeluaran pelanggan**: ${customer_mean:,.2f}  
- **95% Confidence Interval**: (${ci_low:,.2f}  —  ${ci_high:,.2f})  
- **Jumlah pelanggan**: {customer_spent.shape[0]}
""")

st.markdown("---")
st.markdown("## KESIMPULAN")

st.markdown("""
Bagaimana tren rata-rata pembelanjaan pelanggan menurut dari pesebaran kota-kota di Brazil? 
jika dirunutkan atau dibreakdown terdapat banyak jenis-jenis produk yang telah dijual di wilayah brazil, perkembangannya bisa berbeda akan menarik lagi dari setiap kota memiliki tren produk yang berbeda-beda juga dan beragam, tidak ada hanya 1 jenis produk yang menonjol. Pada kota-kota besar cendrung memiliki lebih banyak jenis transaksi sebaliknya kebutuhan di Kota kecil tidak terlalu banyak sehingga trennya juga tidak terlihan beragam.
analisi ini menghasilkan fakta bahwa rata-rata pengeluaran pelanggan sebesar $166.59 atau sekitar 95% dari skala Confidence Interval,
menghasilkan total jumlah pelanggan sebanyak 96096 yang tersebar di kota-kota Brazil.
""")


# ============================================
# TITLE
# ============================================
st.header("2. Analisis Kategori Produk & Pola Order E-Commerce")

st.write("""
Dashboard ini menampilkan analisis persebaran kategori produk, tren pembelian berdasarkan waktu, serta
kategori produk paling populer dari waktu ke waktu.
""")


# ============================================
# PREPROCESSING WAKTU
# ============================================
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['year']  = orders_df['order_purchase_timestamp'].dt.year
orders_df['month'] = orders_df['order_purchase_timestamp'].dt.month
orders_df['day']   = orders_df['order_purchase_timestamp'].dt.day
orders_df['date']  = orders_df['order_purchase_timestamp'].dt.date

st.subheader(" Informasi Jumlah Order per Tahun")
year_counts = orders_df['year'].value_counts().sort_index()
st.bar_chart(year_counts)

# ============================================
#  MERGE PRODUCT & ITEM DATA
# ============================================
st.header(" Analisis Kategori Produk")

totals_product_df = order_items_df.merge(product_df, on="product_id", how="left")

# Hitung total order per kategori
category_counts = (
    totals_product_df.groupby("product_category_name")["order_id"]
    .count()
    .reset_index()
    .rename(columns={"order_id": "total_orders"})
)

top_categories = category_counts.sort_values(by="total_orders", ascending=False)

st.subheader("Top 10 Kategori Produk Terbanyak di Order")
st.dataframe(top_categories.head(10))

# ============================================
# VISUALISASI TOP 10 KATEGORI PRODUK
# ============================================
fig, ax = plt.subplots(figsize=(10, 6))

sns.barplot(
    x=top_categories.head(10)["product_category_name"],
    y=top_categories.head(10)["total_orders"],
    color="#1f77b4"
)

plt.title("Top 10 Kategori Produk Terbanyak (Jumlah Order)")
plt.xlabel("Kategori Produk")
plt.ylabel("Jumlah Order")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

st.pyplot(fig)

# ============================================
# TREND KATEGORI PRODUK PER TAHUN
# ============================================
st.header("📈 Tren Kategori Produk Berdasarkan Tahun")

# Merge items + product + tahun order
items_products = order_items_df.merge(product_df, on="product_id", how="left")
items_products_year = items_products.merge(
    orders_df[['order_id', 'year']],
    on="order_id",
    how="left"
)

category_year_counts = (
    items_products_year
    .groupby(['year', 'product_category_name'])['order_id']
    .count()
    .reset_index()
    .rename(columns={'order_id': 'total_orders'})
)

# Tampilkan data
st.write("Berikut distribusi jumlah order kategori produk per tahun:")
st.dataframe(category_year_counts.head(20))

# --- SIDEBAR FILTER TAHUN ---
st.sidebar.header("Filter Tahun Kategori Produk")

years_available = sorted(category_year_counts['year'].unique())

selected_year = st.sidebar.selectbox(
    "Pilih Tahun:",
    years_available,
    index=len(years_available) - 1  # default ke tahun terbaru
)

# --- FILTER DATA BERDASARKAN TAHUN ---
data_year = (
    category_year_counts[category_year_counts['year'] == selected_year]
    .sort_values(by='total_orders', ascending=False)
    .head(10)
)

st.subheader(f"Top 10 Kategori Produk Tahun {selected_year}")

# --- BAR CHART ---
fig, ax = plt.subplots(figsize=(12, 5))

sns.barplot(
    data=data_year,
    x='product_category_name',
    y='total_orders',
    color='#1f77b4'
)

plt.title(f'Top 10 Kategori Produk — Tahun {selected_year}')
plt.xlabel('Kategori Produk')
plt.ylabel('Total Order')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

st.pyplot(fig)
st.markdown("---")
st.markdown("## KESIMPULAN")

st.markdown("""
Dinamika trasaksi E-commerce sangat beragam pada tahun 2016-2018 di Brazil, setiap tahun grafiknya pun menunjukan perbedaan tren yang berbeda berdasarkan kategori. Namun, setelah dikumpulkan informasinya dalam 3 tahun kategory produk cama_mesa_banho tetap paling diminati di beberapa kota di Brazil
""")
st.caption('Copyright (C) Mira Destiyanti 2025')






















































































































































































































































































