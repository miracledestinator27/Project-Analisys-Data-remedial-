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


# Streamlit header
st.title('E-commerce Dashboard')

# --- Load and preprocess ---
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['order_year'] = orders_df['order_purchase_timestamp'].dt.year

# --- SIDEBAR UI ---
st.sidebar.header("Filter Orders")

# unique sorted years
years = sorted(orders_df['order_year'].unique())

# year selection in sidebar
selected_year = st.sidebar.selectbox(
    "Select Order Year",
    options=years,
    index=0
)

# filter dataframe
filtered_orders = orders_df[orders_df['order_year'] == selected_year]

# --- Display result ---
st.write(f"### Orders for Year: {selected_year}")
st.dataframe(filtered_orders)

st.write("### Menghitung Rata-rata Transaksi Produk per Tahun dan Kota")

st.header("Rata-rata Pembelanjaan Pelanggan & Confidence Interval per Wilayah")

# --- MERGE DATASET ---
pay_ord_cust = (
    orders_df
    .merge(order_payment_df, on='order_id', how='outer')
    .merge(customers_df, on='customer_id', how='outer')
)

# --- TOTAL PEMBELANJAAN PER CUSTOMER ---
customer_spent = (
    pay_ord_cust
    .groupby('customer_unique_id')
    .agg(total_spent=('payment_value', 'sum'))
    .sort_values(by='total_spent', ascending=False)
)

# Mean & Std Error
customer_mean = customer_spent['total_spent'].mean()
customer_std = stats.sem(customer_spent['total_spent'])

# Confidence interval (95%)
ci_customer = stats.t.interval(
    0.95,
    df=len(customer_spent) - 1,
    loc=customer_mean,
    scale=customer_std
)

# --- DISPLAY IN STREAMLIT ---
st.subheader("Rata-rata Belanja Pelanggan")
st.write(f"**Mean spending:** {customer_mean:,.2f}")
st.write(f"**95% Confidence Interval:** {ci_customer}")

# --- MEAN PER REGION (STATE) ---
customer_regions = (
    pay_ord_cust
    .groupby('customer_state')
    .agg(
        mean_payment=('payment_value', np.mean),
        std_payment=('payment_value', np.std),
        n_customers=('customer_unique_id', 'count')
    )
    .reset_index()
)

# Hitung CI per region
cis = stats.t.interval(
    0.95,
    df=customer_regions['n_customers'] - 1,
    loc=customer_regions['mean_payment'],
    scale=customer_regions['std_payment'] / np.sqrt(customer_regions['n_customers'])
)

customer_regions['ci_low'] = cis[0]
customer_regions['ci_hi'] = cis[1]

# --- DISPLAY TABLE ---
st.subheader("Confidence Interval Pembelanjaan per State")
st.dataframe(customer_regions)

# Pastikan timestamp menjadi datetime
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])

# Tambahkan kolom tahun
orders_df['order_year'] = orders_df['order_purchase_timestamp'].dt.year

# Merge orders + payments + customers
pay_ord_cust = (
    orders_df
    .merge(order_payment_df, on='order_id', how='outer')
    .merge(customers_df, on='customer_id', how='outer')
)

# Hitung rata-rata transaksi berdasarkan kota & tahun
avg_transaction_city_year = (
    pay_ord_cust.groupby(['order_year', 'customer_city'])
    .agg(
        avg_transaction_value=('payment_value', 'mean'),
        transaction_count=('payment_value', 'count')
    )
    .reset_index()
)

# Tampilkan dataframe di Streamlit
st.write("### Rata-rata Transaksi Produk per Tahun dan Kota")
st.dataframe(avg_transaction_city_year)

# --- DATA MERGE ---
pay_ord_cust = (
    orders_df
        .merge(order_payment_df, on='order_id', how='outer')
        .merge(customers_df, on='customer_id', how='outer')
)

st.write("### Merged Dataset: Orders + Payments + Customers")
st.dataframe(pay_ord_cust)


# --- Rata-rata transaksi per kota ---
avg_city = (
    pay_ord_cust.groupby('customer_city')
    .agg({'payment_value': 'mean'})
    .sort_values('payment_value', ascending=False)
)

# --- Ambil 10 kota teratas ---
top_10_cities = avg_city.head(10).index

st.write("### Rata-rata Transaksi per Kota")
st.dataframe(avg_city)

st.write("### 10 Kota dengan Rata-rata Transaksi Tertinggi")
st.write(top_10_cities.tolist())

avg_city = (
    pay_ord_cust.groupby('customer_city')
    .agg({'payment_value': 'mean'})
    .sort_values('payment_value', ascending=False)
)

# --- Ambil 10 kota teratas ---
top_10_cities = avg_city.head(10).index

st.write("### Rata-rata Transaksi per Kota")
st.dataframe(avg_city)

st.write("### 10 Kota dengan Rata-rata Transaksi Tertinggi")
st.write(top_10_cities.tolist())

# --- Merge order_items + products ---
items_prod = order_items_df.merge(
    products_df,
    on='product_id',
    how='left'
)

# --- Gabungkan dengan pay_ord_cust (tambahkan kategori produk) ---
full_df = pay_ord_cust.merge(
    items_prod[['order_id', 'product_id', 'product_category_name']],
    on='order_id',
    how='left'
)

st.write("### Full DataFrame (Orders + Payment + Customer + Product Category)")
st.dataframe(full_df)

# --- Filter hanya 10 kota teratas ---
filtered = full_df[full_df['customer_city'].isin(top_10_cities)]

st.write("### Filtered for Top 10 Cities")
st.dataframe(filtered.head())

# --- Grouping trend per Tahun, Kota, dan Kategori Produk ---
trend_city_cat_year = (
    filtered.groupby(['order_year', 'customer_city', 'product_category_name'])
    .agg(
        avg_transaction=('payment_value', 'mean'),
        total_transactions=('payment_value', 'count')
    )
    .reset_index()
)

st.write("### Trend per Tahun, Kota, dan Kategori Produk")
st.dataframe(trend_city_cat_year)

# --- Top 5 kategori per kota per tahun ---
top5_per_city_year = (
    trend_city_cat_year
    .sort_values(['order_year', 'customer_city', 'total_transactions'], ascending=False)
    .groupby(['order_year', 'customer_city'])
    .head(5)
)

st.write("### Top 5 Kategori Produk per Kota per Tahun")
st.dataframe(top5_per_city_year)


avg_city = (
    pay_ord_cust.groupby('customer_city')
    .agg({'payment_value': 'mean'})
    .sort_values('payment_value', ascending=False)
)

top_10_cities_df = avg_city.head(10)

st.write("### Top 10 Kota dengan Rata-rata Transaksi Tertinggi")
st.bar_chart(top_10_cities_df)

# Sort data
plot = customer_regions.sort_values(by=('payment_value', 'mean'))

st.write("### Rata-rata Transaksi per Kota")

# Create figure
fig, ax = plt.subplots(figsize=(12, 4))

# Bar chart (single blue color)
ax.bar(
    plot['customer_state'],
    plot['payment_value']['mean'],
    color="#1f77b4"
)

# Labels and formatting
plt.xticks(rotation=30)
plt.xlabel('Kota')
plt.ylabel('Rata-rata Transaksi')

plt.tight_layout()

# Display in Streamlit
st.pyplot(fig)



t.write("### Top 10 Kota: Tren Rata-rata Transaksi per Kategori Produk per Tahun")

# Create figure
fig = plt.figure(figsize=(18, 7))

# Loop each year
for year in sorted(top5_per_city_year['order_year'].unique()):
    subset = top5_per_city_year[top5_per_city_year['order_year'] == year]

    plt.bar(
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

# Display in Streamlit
st.pyplot(fig) 


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
















































































































































































































































