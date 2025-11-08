import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Membaca data (pastikan Anda sudah memiliki file data yang sesuai)

customers_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\customers_dataset.csv")
geolocation_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\geolocation_dataset.csv")
order_items_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\order_items_dataset.csv")
order_payments_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\order_payments_dataset.csv")
order_reviews_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\order_reviews_dataset.csv")
orders_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\orders_dataset.csv")
category_df = pd.read_csv("dE-commerce-public-dataset\E-Commerce Public Dataset\product_category_name_translation.csv")
product_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\products_dataset.csv")
sellers_df = pd.read_csv("E-commerce-public-dataset\E-Commerce Public Dataset\sellers_dataset.csv")

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













