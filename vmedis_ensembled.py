import pandas as pd
import numpy as np

def ensembled_function(df,y_est_tm,y_est_lstm, alpha):
    df=pd.DataFrame(df['Jumlah'])

    beta = 1-alpha

    y_est_ensmbld = alpha * np.array(y_est_tm) + beta * np.array(y_est_lstm)

    data = pd.DataFrame({
        'Prediksi TM': y_est_tm,
        'Prediksi LSTM': y_est_lstm,
        'Prediksi ensembled ':y_est_ensmbld
    })
    print(data)

    return y_est_ensmbld