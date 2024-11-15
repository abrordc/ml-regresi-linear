# Import library yang diperlukan
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pickle  # Import modul pickle untuk menyimpan model

# Contoh data: Luas rumah (dalam m2) dan harga rumah (dalam juta)
data = {
    'Luas_Rumah': [50, 60, 70, 80, 100, 120, 150, 200],
    'Harga_Rumah': [500, 550, 600, 650, 700, 800, 1000, 1200]
}

# Mengubah data menjadi DataFrame
df = pd.DataFrame(data)

# Memisahkan fitur (Luas_Rumah) dan label (Harga_Rumah)
X = df[['Luas_Rumah']]  # Fitur (input)
y = df['Harga_Rumah']  # Label (output)

# Membagi data menjadi data latih dan data uji
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#cetak data train dan test 
print("data training:\n",X_train)
print("data testing:\n",X_test)

# Membuat model regresi linear
model = LinearRegression()

# Melatih model dengan data latih
model.fit(X_train, y_train)

# Melakukan prediksi terhadap data uji
y_pred = model.predict(X_test)

# Menampilkan hasil prediksi
print("Prediksi harga rumah:", y_pred)

# Menampilkan error (Mean Squared Error)
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

# Menghitung R-squared (koefisien determinasi)
r_squared = model.score(X_test, y_test)
print("R-squared:", r_squared)

# Menyimpan model ke dalam file pickle, setelah model dilatih
with open('modelRegresiku.pkl', 'wb') as file:
    pickle.dump(model, file)
print("Model telah disimpan ke dalam file 'modelRegresiku.pkl'.")

# Visualisasi hasil regresi linear
plt.scatter(X, y, color='blue')  # Plot data asli
plt.plot(X, model.predict(X), color='red')  # Plot garis regresi
plt.title("Regresi Linear: Luas Rumah vs Harga Rumah")
plt.xlabel("Luas Rumah (m2)")
plt.ylabel("Harga Rumah (juta)")
plt.show()
