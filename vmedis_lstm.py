import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM


def lstm_function(df, N_predict):
    df=pd.DataFrame(df['Jumlah'])
    print(df)

    # Normalisasi (Min-Max)
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df)
    print(type(data_scaled))

    # Buat data latih: X (n bulan sebelumnya) -> Y (bulan ke-n+1)
    def create_dataset(data, time_step=3):
        X, Y = [], []
        for i in range(len(data) - time_step):
            X.append(data[i:i+time_step, 0])
            Y.append(data[i+time_step, 0])
        return np.array(X), np.array(Y)

    X, y = create_dataset(data_scaled, time_step=3)
    X = X.reshape(X.shape[0], X.shape[1], 1)  # LSTM butuh 3D input

    # Bangun model LSTM
    model = Sequential()
    model.add(LSTM(50, activation='relu', return_sequences=False, input_shape=(3, 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=300, verbose=0)

    y_est=[]
    for i in range(0,N_predict):
        last_3 = data_scaled[-3:].reshape(1, 3, 1)
        pred_scaled = model.predict(last_3)
        pred = scaler.inverse_transform(pred_scaled)
            
        y_est.append(round(pred[0][0]))
        print("Prediksi penjualan : ",y_est[i])
        df.loc[len(df)] = y_est[i]
        data_scaled = scaler.fit_transform(df)


    return y_est