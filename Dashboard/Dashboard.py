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

# fungsi untuk membuat metric harian
def create_daily_metrics_df(orders_df):
    datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
    for column in datetime_columns: 
        orders_df[column] = pd.to_datetime(orders_df[column])
    daily_df = orders_df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id': 'nunique',  # Unique orders
        'order_status': 'count'  # Total orders
    }).reset_index()
    daily_df.rename(columns={'order_id': 'order_count', 'order_status': 'total_orders'}, inplace=True)
    return daily_df

# membuat dataframe metric harian
print ("ORDERS TABLE")
orders_df = pd.read_csv("orders_dataset.csv")
orders_df.head()
daily_metrics_df = create_daily_metrics_df(orders_df)


# sidebar untuk input tanggal
with st.sidebar:
    start_date, end_date = st.date_input()
        label='Date Range',
        value=(daily_metrics_df['order_purchase_timestamp'].min().date(), 
            daily_metrics_df['order_purchase_timestamp'].max().date())

# menggonversi input tanggal ke datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data berdasarkan data input
main_df = daily_metrics_df[(daily_metrics_df['order_purchase_timestamp'] >= start_date) & 
                            (daily_metrics_df['order_purchase_timestamp'] <= end_date)]

# --- Streamlit Dashboard ---

# Streamlit header
st.header('E-commerce Dashboard')













