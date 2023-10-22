## Customer Segmentation with RFM

import pandas as pd
import datetime as dt
pd.set_option('display.max_column', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

df_ = pd.read_excel('/Users/betulyilmaz/Documents/Miuul/CRM Analytics/Bonus-Online Retail RFM Analizi Ile Musteri Segmentasyonu ve CLTV Prediction/online_retail_II.xlsx')
df = df_.copy()
df.head()

df.shape
df.describe().T
df.info()

# Eksi deger olan satirlari siliyoruz
df = df[df['Quantity'] > 0]
df = df[df['Price'] > 0]

# Missing valuelari siliyoruz
df.isnull().sum()
df.dropna(inplace=True)

# Faturalardaki ‘C’ iptal edilen islemleri gosteriyor.
# İptal edilen işlemleri veri setinden cikariyoruz.
c = df["Invoice"].astype(str).str.contains("C")
c.value_counts()
df = df[~df["Invoice"].astype(str).str.contains("C", na=False)]

# En fazla kazanc getiren ilk 10 musteriyi siralayalim.
df['TotalPrice'] = df['Quantity'] * df['Price']
df.sort_values('TotalPrice', ascending=False)[:10]

# RFM Metriklerinin hesaplanmasi
# Recency, Frequency, Monetary degerlerinin yer aldigi yeni bir RFM DataFrame'i olusturuyoruz.

df['InvoiceDate'].max() #2010-12-09 20:01:00
analysis_date = dt.datetime(2010, 12, 11)
type(analysis_date)


rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (analysis_date - InvoiceDate.max()).days,
                                    'Invoice': lambda Invoice: Invoice.nunique(),
                                    'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T

# RFM metriklerinin skorlarini belirleme
rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]) # method=first ilk gordugu degeri ilk gruba atar.
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm['RF_SCORE'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str)
rfm['RFM_SCORE'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str)

## RF segmentation

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
        }

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)

# Hedeflenen bir musteri kitlesinin id'lerinin kaydedilmesi.
target_segments_ids = pd.DataFrame()
target_segments_ids['customer_id'] = rfm[rfm['segment'].isin(["champions", "loyal_customers"])].index
target_segments_ids['customer_id'] = target_segments_ids['customer_id'].astype(int)

target_segments_ids = rfm[rfm['segment'].isin(["champions", "loyal_customers"])].index
target_segments_ids.astype(int)

target_customer_ids = pd.DataFrame()
target_customer_ids['customer_id'] = df[(df['Customer ID'].isin(target_segments_ids['customer_id'])) & (df['Country'].str.contains('United Kingdom'))]['Customer ID']
target_customer_ids['customer_id'].astype(int)
target_customer_ids.reset_index(inplace=True, drop=True) # eski indexi sifirladik, drop burda eski indexi kaldirmak icin.
target_customer_ids.to_csv('target_customer_ids.csv')










