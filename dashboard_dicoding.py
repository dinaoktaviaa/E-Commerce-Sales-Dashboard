import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
# from datetime import datetime

sns.set(style='dark')

# A. DATA WRANGLING

# 1. Gathering Data

# Membaca data csv
df_orders = pd.read_csv("data_1_orders.csv")
df_payments = pd.read_csv("data_2_payments.csv")
df_items = pd.read_csv("data_3_items.csv")
df_products = pd.read_csv("data_4_products.csv")
df_customers = pd.read_csv("data_5_customers.csv")


# Penggabungan data "df_orders" dengan "df_payments". Untuk primary key: "order_id" dan foreign key dari data "df_payments"
orders_payments_df = pd.merge(
    left=df_orders,
    right=df_payments,
    how="inner",
    left_on="order_id",
    right_on="order_id"
)

# Penggabungan data "df_items" dengan "df_products". Untuk primary key: "product_id" dan foreign key dari data "df_products"
items_products_df = pd.merge(
    left=df_items,
    right=df_products,
    how="inner",
    left_on="product_id",
    right_on="product_id"
)


# 2. Assessing Data

# Assessing Data orders_payments_df
orders_payments_df.info()
orders_payments_df.isnull().sum() #missing value
orders_payments_df.duplicated().sum() #duplikat
orders_payments_df.describe()

# Assessing Data items_products_df
items_products_df.info()
items_products_df.isnull().sum() #missing value
items_products_df.duplicated().sum()
items_products_df.describe()

# Assessing Data df_customers
df_customers.info()
df_customers.duplicated().sum()

# 3. Cleaning Data

# 1. Pada penggabungan data "order_payments_df" terdapat missing value pada 3 kolom, namun kolom tersebut tidak akan digunakan pada proses Exploratory Data Analysis sehingga tidak ada data yang dibuang dan juga tidak ada duplikat. Jadi proses cleaning data hanya mengubah tipe data string ke datetime
# 2. Pada penggabungan data "items_products_df terdapat missing value pada 4 kolom, namun kolom tersebut tidak akan digunakan pada proses Exploratory Data Analysis sehingga tidak ada data yang dibuang dan juga tidak ada duplikat. Jadi hanya menyamaratakan tipe data float
# 3. Pada data "df_customers" tidak ada missing value dan duplikat sehingga tidak ada proses cleaning data


# Ubah tipe data beberapa kolom menjadi datetime pada penggabungan data "orders_payments_df"
convert_to_datetime = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
orders_payments_df[convert_to_datetime] = orders_payments_df[convert_to_datetime].apply(pd.to_datetime)

# Menyamaratakan tipe data float pada kolom "price" dan "freight_value" untuk penggabungan data: "items_products_df"
items_products_df[["price", "freight_value"]] = items_products_df[["price", "freight_value"]].astype(float)

# B. EXPLORATORY DATA ANALYSIS (EDA)

# Explore "orders_payments_df" (Analisis tren nilai pembayaran dari waktu ke waktu pada tahun 2016-2018)
def create_payment_by_timestamp(df):
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["month_year"] = df["order_purchase_timestamp"].dt.to_period('M')
    payment_by_timestamp = df.groupby("month_year")["payment_value"].sum().reset_index()
    return payment_by_timestamp
payment_by_timestamp = create_payment_by_timestamp(orders_payments_df)
payment_by_timestamp["month_year"] = payment_by_timestamp["month_year"].astype(str)

# Exploratory "items_products_df" (Analisis kategori produk berdasarkan pendapatan/revenue)
def create_product_category(df):
  product_category = df.groupby("product_category_name").agg(
      count_product=('product_category_name', 'count'),
      total_price=('price', 'sum')
  ).reset_index()
  product_category["revenue"] = product_category["total_price"] * product_category["count_product"]
  product_category = product_category.sort_values(by='count_product', ascending=False)
  return product_category
product_category = create_product_category(items_products_df)

# Exploratory "df_customers" (Analisis kota dengan total pelanggan terbanyak)
def create_customer_city(df):
  city = df['customer_city'].value_counts().reset_index()
  city.columns = ['customer_city', 'city_count']
  city = city.sort_values(by='city_count', ascending=False).reset_index(drop=True)
  return city
city = create_customer_city(df_customers)


# C. VISUALIZATION & EXPLORATORY ANALYSIS


st.title("E-Commerce Sales")

col1= st.columns(1)
 
with col1[0]:
    st.image("/Users/dinaoktv/Documents/PROYEKDA/Kursus-E-Commerce-Jogja.png", width=400)


st.subheader('Daily Orders')
col1, col2 = st.columns(2)

with col1:
   total_orders = df_orders.order_id.nunique()
   st.metric("Total orders", value=total_orders)

with col2:
   total_revenue = format_currency(product_category.revenue.sum(), "IDR", locale="id_ID")
   st.metric("Total Revenue", value=total_revenue)

# Pertanyaan 1: Apakah ada pola atau tren peningkatan atau penurunan dalam nilai pembayaran dari waktu ke waktu?
st.subheader("")
fig, ax = plt.subplots(figsize=(20, 12))
ax.plot(payment_by_timestamp["month_year"], payment_by_timestamp["payment_value"], marker="o", linewidth=4, color="#0c83ff")
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
ax.set_xlabel("Purchase Time", size=20, fontweight='bold')
ax.set_ylabel("Payment Value", size=20, fontweight='bold')
ax.set_title("Payment Value based on Purchase Time", size=30, fontweight='bold')
ax.set_xticklabels(payment_by_timestamp["month_year"], rotation=45, ha="right", fontsize=15)  # Menyesuaikan ukuran label sumbu x


for index, value in enumerate(payment_by_timestamp["payment_value"]):
    formatted_value = format_currency(value, 'IDR', locale='id_ID')
    ax.text(payment_by_timestamp["month_year"][index], value, formatted_value, ha='left', va='bottom', fontsize=15, rotation=10)
plt.tight_layout()
st.pyplot(fig)

with st.expander("Conclucion"):
    st.write(
        """ 
        Berdasarkan grafik di atas dapat disimpulkan bahwa nilai pembayaran (payment value) mengalami peningkatan pada bulan November tahun 2017 (2017-11) dan mengalami penurunan drastis pada bulan September tahun 2018 (2018-12)
        """
    )


# Pertanyaan 2: Apakah terdapat kategori produk tertentu yang memberikan kontribusi signifikan terhadap total pendapatan?
st.subheader("Best Performing Product")
top_products = product_category.sort_values(by="revenue", ascending=False).head(8)
fig, ax = plt.subplots(figsize=(35, 20))
colors = ["#7e171e", "#9f1424", "#c10a2a", "#d24949", "#d24949", "#e1706a", "#ed958d", "#f6b8b2"]
sns.barplot(x="product_category_name", y="revenue", data=top_products.head(8), palette=colors)
ax.set_ylabel("Revenue", fontsize=30, fontweight='bold')
ax.set_xlabel("Product Category", fontsize=30, fontweight='bold')
# ax.set_title("Best Performing Product", loc="center", fontsize=50, fontweight='bold')
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=15)
ax.set_xticklabels(top_products["product_category_name"], rotation=45, ha="right", fontsize=30) 

for index, value in enumerate(top_products["revenue"]):
    formatted_value = format_currency(value, 'IDR', locale='id_ID')
    ax.text(index, value, formatted_value, ha='center', va='bottom', fontsize=30, rotation=45)   
plt.tight_layout()
st.pyplot(fig)

with st.expander("Conclucion"):
    st.write(
        """
        Berdasarkan bar di atas dapat disimpulkan bahwa produk yang memberikan kontribusi signifikan terhadap total pendapatan (revenue) adalah "Baleze-Saude
        """
    )

# Pertanyaan 3: Kota apa dengan jumlah pelanggan terbanyak?
st.subheader("Top Customer Cities")
fig, ax = plt.subplots(figsize=(25,15))
top_cities = city.sort_values(by="city_count", ascending=False).head(8)
colors = ["#12320d", "#11420e", "#0e520c", "#056209", "#3e7b34", "#3e7b34", "#65955a", "#8baf81", "#d8e4d4"]
sns.barplot(y="city_count", x="customer_city", data=top_cities.head(8), palette=colors)
ax.set_xlabel("Customer City", fontsize=20, fontweight='bold')
ax.set_ylabel("Total City", fontsize=20, fontweight='bold')
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
for index, value in enumerate(top_cities["city_count"]):
    formatted_value = "{:,.0f}".format(value)
    ax.text(index, value, formatted_value, ha='center', va='bottom', fontsize=22, rotation=0)
plt.tight_layout()
st.pyplot(fig)

with st.expander("Conclucion"):
    st.write(
        """
        Berdasarkan bar di atas dapat disimpulkan bahwa kota dengan jumlah pelanggan terbanyak yaitu Sao Palo
        """
    )

# D. Conclucion

# Conclution pertanyaan 1: Nilai pembayaran mengalami peningkatan pada bulan November tahun 2017 (2017-11) dan mengalami penurunan drastis pada bulan September tahun 2018 (2018-12)
# Conclution pertanyaan 2: Produk yang memberikan kontribusi signifikan terhadap total pendapatan (revenue) adalah "Baleze-Saude"
# Conclution pertanyaan 3: Kota dengan jumlah pelanggan terbanyak yaitu Sao Palo
