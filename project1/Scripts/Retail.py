import streamlit as st
import pandas as pd
import mysql.connector

#  Database Connection
try:
    connection = mysql.connector.connect(
        host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
        port=4000,
        user="w9wfNMYH97sGJCu.root",
        password="PG2s6UNgeviOPk69",
        database="miniproject",
    )
    mycursor = connection.cursor()
    db_status = "✅ Connected"
except mysql.connector.Error as err:
    db_status = f"❌ Database Error: {err}"

# Streamlit App Title
st.title("📊 Retail Order Data Analysis")

#  Sidebar Navigation
st.sidebar.header("🔍 Navigation")
r = st.sidebar.radio("Go to:", ["🏠 Home", "📈 First 10 Queries", "📉 Last 10 Queries","Write Your Own Query"])

# Read CSV File (Ensure path is correct)
df = pd.read_csv(r"C:\Users\ABIRAINA\OneDrive\Desktop\guvi notes\guvi\orders.csv")

# Data Cleaning & Processing
df = df.rename(columns={
    "Order Id": "order_id", 
    "Order Date": "order_date",
    "Ship Mode": "ship_mode",
    "Postal Code": "postal_code", 
    "Sub Category": "sub_category",
    "Product Id": "product_id",
    "cost price": "cost_price",
    "List Price": "list_price", 
    "Discount Percent": "discount_percent"
})
df.fillna(0, inplace=True)
df["Discount_value"] = df["list_price"] * (df["discount_percent"] / 100)
df["selling_price"] = df["list_price"] - df["Discount_value"]
df["profit"] = df["selling_price"] - df["cost_price"]

#  Split into Two DataFrames
df1 = df[['order_id', 'order_date', 'ship_mode', 'Segment', 'Country', 'City', 'State', 'postal_code', 'Region']]
df2 = df[['order_id', 'Category', 'sub_category', 'product_id', 'cost_price', 'list_price', 'Quantity', 'discount_percent', 'Discount_value', 'selling_price', 'profit']]

#  Home Page
if r == "🏠 Home":
    st.header("🗂 Data Overview")
    st.write("📌 **Database Status:**", db_status)
    st.subheader("📄 Complete Data")
    st.write(df)
    st.subheader("📜 Order Info (file1)")
    st.write(df1)
    st.subheader("🛍️ Product Info (file2)")
    st.write(df2)

#  First 10 Queries
queries_1 = {
    'Find top 10 highest revenue generating products':"SELECT sub_category,(selling_price * Quantity) as revenue from miniproject.file2 ORDER BY revenue DESC LIMIT 10; ",
    'Find the top 5 cities with the highest profit margins':"""SELECT o1.City, SUM(o2.profit) AS Total_Profit, SUM(o2.selling_price * o2.Quantity) AS Total_Revenue, (SUM(o2.profit) / SUM(o2.selling_price * o2.Quantity)) * 100 AS Profit_Margin 
     FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
     GROUP BY o1.City 
     ORDER BY Profit_Margin DESC LIMIT 5;""",
    'Calculate the total discount given for each category':"SELECT Category,Sum(Discount_value) as total_discount from file2 GROUP BY Category ",
    'Find the average sale price per product category':"SELECT sub_category, avg(selling_price) as average from miniproject.file2 GROUP BY sub_category  ORDER BY average DESC",
    'Find the region with the highest average sale price':"""SELECT o1.Region, avg(o2.selling_price) AS average_sale 
                 FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
                 group by o1.Region 
                 ORDER BY average_sale DESC limit 1;""",
    'Find the total profit per category':"SELECT Category, SUM(profit) as Total_profit from file2 GROUP BY Category  ORDER BY Total_profit DESC",
    ' Identify the top 3 segments with the highest quantity of orders':"""SELECT o1.Segment, sum(o2.Quantity) AS total_quantity 
                 FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
                 group by o1.Segment 
                 ORDER BY total_quantity  DESC LIMIT 3;""",
    ' Determine the average discount percentage given per region':"""SELECT o1.Region, avg(o2.discount_percent) AS discount
                 FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
                 group by o1.Region 
                 ORDER BY discount DESC ;""",
    ' Find the product category with the highest total profit':"""SELECT sub_category, SUM(profit) as total_profit
                 from miniproject.file2
                 group by sub_category 
                 ORDER BY total_profit DESC ;""",
    'Calculate the total revenue generated per year':""" select YEAR(o1.order_date) as Year ,sum(o2.selling_price * o2.Quantity) as total_revenue
                 FROM file2 o2 JOIN file1 o1 ON o1.order_id = o2.order_id
                 group by YEAR(o1.order_date)
                 ORDER BY YEAR DESC;"""
    
}

if r == "📈 First 10 Queries":
    st.header("🚀 First 10 Queries")
    selected_query = st.selectbox("🔎 Select a Query", list(queries_1.keys()))
    
    if selected_query:
        query = queries_1[selected_query]

        #  Show Query Button
        if st.button("🔍 Show Query"):
            st.code(query, language="sql")

        #  Run Query Button
        if st.button("▶ Run Query"):
            mycursor.execute(query)
            result = mycursor.fetchall()
            df_query_result = pd.DataFrame(result, columns=[desc[0] for desc in mycursor.description])
            st.write(df_query_result)


# Last 10 Queries
queries_2 = {
    "Most Popular Ship Mode by Total Sales": """
        SELECT o1.ship_mode, SUM(o2.selling_price * o2.Quantity) AS total_sale 
        FROM file1 o1 
        JOIN file2 o2 ON o1.order_id = o2.order_id 
        GROUP BY o1.ship_mode
        ORDER BY total_sale DESC;
    """,
    "Find the total revenue generated by each segment":"""SELECT o1.Segment, sum(o2.selling_price * o2.Quantity) AS total_revenue 
                 FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
                 group by o1.Segment 
                 ORDER BY total_revenue  DESC LIMIT 3;""",
    " City with Highest Total Discount": """
        SELECT o1.City, SUM(o2.Discount_value) AS Total_discount
        FROM file1 o1 
        JOIN file2 o2 ON o1.order_id = o2.order_id 
        GROUP BY o1.City
        ORDER BY Total_discount DESC 
        LIMIT 1;
    """,
    "Find the city with the highest total discount given":"""SELECT o1.City, sum(o2.Discount_value) AS Total_discount
                 FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
                 group by o1.City
                 ORDER BY Total_discount DESC limit 1;""",
    "Find the most frequently ordered product in each region.":"""SELECT o1.Region,o2.product_id , count(o2.product_id ) AS product_count
                 FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
                 group by o1.Region ,o2.product_id 
                 ORDER BY o1.Region,product_count DESC ;""",
    "Calculate the total number of orders per state":"SELECT  state, count(order_id) as total_order from miniproject.file1 GROUP BY state order by total_order desc",

    " Top-Selling Products by Quantity": """
        SELECT o2.product_id, o2.Category, SUM(o2.Quantity) AS total_sold_quantity
        FROM file2 o2
        GROUP BY o2.product_id, o2.Category
        ORDER BY total_sold_quantity DESC;
    """,
    "Find the average profit margin per region":"""SELECT o1.Region, avg(o2.profit/o2.selling_price)*100 AS average_profit
                 FROM file1 o1 JOIN file2 o2 ON o1.order_id = o2.order_id 
                 group by o1.Region 
                 ORDER BY average_profit DESC ;""",
    "Find the top 5 most discounted products":"""SELECT o2.product_id,o2.Category,o2.sub_category, avg(o2.discount_percent) as average_discount
                 FROM file2 o2
                 group by o2.product_id,o2.Category,o2.sub_category
                 ORDER BY average_discount DESC limit 5;""",

    " Find the Total Revenue for Each City": """
        SELECT o1.City, SUM(o2.selling_price * o2.Quantity) AS total_revenue 
        FROM file2 o2 
        JOIN file1 o1 ON o2.order_id = o1.order_id
        GROUP BY o1.City 
        ORDER BY total_revenue DESC;
    """
}

if r == "📉 Last 10 Queries":
    st.header("🚀Last 10 Queries")
    selected_query = st.selectbox("🔎 Select a Query", list(queries_2.keys()))
    
    if selected_query:
        query = queries_2[selected_query]

        # Show Query Button
        if st.button("🔍 Show Query"):
            st.code(query, language="sql")

        #  Run Query Button
        if st.button("▶ Run Query"):
            mycursor.execute(query)
            result = mycursor.fetchall()
            df_query_result = pd.DataFrame(result, columns=[desc[0] for desc in mycursor.description])
            st.write(df_query_result)

if r == 'Write Your Own Query':
    st.subheader("📝 Write and Execute Your Own SQL Query")

    # Text area for query input
    user_query = st.text_area("🔹 Enter your SQL query below:", height=150)

    if st.button("🚀 Run Query"):
        if user_query.strip():
            try:
                mycursor.execute(user_query)
                result = mycursor.fetchall()
                if result:
                    df_query_result = pd.DataFrame(result, columns=[desc[0] for desc in mycursor.description])
                    st.write(df_query_result)
                else:
                    st.write("✅ Query executed successfully, but no results found.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Please enter a valid SQL query.")

