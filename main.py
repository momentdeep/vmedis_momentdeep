from flask import Flask, request, render_template, send_file, session
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pickle

import vmedis_read_data as rd
import vmedis_trendmoment as tm
import vmedis_lstm as lstm
import vmedis_ensembled as ensembled

app = Flask(__name__)
app.secret_key = 'rahasia_anda'  # Untuk session

@app.route('/', methods=['GET', 'POST'])
def index():
    tables = {}

    # Jika halaman diakses lewat GET (refresh / buka tab baru), hapus file & session
    if request.method == 'GET':
        session.pop('uploaded', None)
        session.pop('file_path', None)

        # Hapus file yang tersimpan jika ada
        if os.path.exists("temp_data.pkl"):
            os.remove("temp_data.pkl")
        if os.path.exists("temp_data.xls"):
            os.remove("temp_data.xls")

        return render_template("index.html", tables={})

    # ===== BAGIAN POST =====
    n_predict = int(request.form['n_predict'])
    sediaan = int(request.form['sediaan'])
    alpha = float(request.form['alpha'])
    mode = request.form['mode']

    file = request.files.get('file')

    if file:
        # Simpan file ke server
        file_path = "temp_data.xls"
        file.save(file_path)
        session['uploaded'] = True
        session['file_path'] = file_path

        data = rd.read_data_vmedis(file_path)
        with open("temp_data.pkl", "wb") as f:
            pickle.dump(data, f)
    elif session.get('uploaded'):
        file_path = session['file_path']
        with open("temp_data.pkl", "rb") as f:
            data = pickle.load(f)
    else:
        return render_template("index.html", tables={}, error="Silakan upload file terlebih dahulu.")

    # Prediksi dan visualisasi seperti sebelumnya
    y_tm = tm.tm_fuction(data, n_predict)
    y_lstm = lstm.lstm_function(data, n_predict)
    y_ens = ensembled.ensembled_function(data, y_tm, y_lstm, alpha)

    def make_table(pred, mode, sediaan_awal, n_predict):
        bulan = []
        sediaan = sediaan_awal

        if mode == "produk":
            produk_jadi_tetap = round(pred[0])
            for i in range(n_predict):
                jualan = round(pred[i])
                sediaan_akhir = produk_jadi_tetap + sediaan - jualan
                produk_siap = jualan + sediaan_akhir
                bulan.append([jualan, sediaan_akhir, produk_siap, sediaan, produk_jadi_tetap])
                sediaan = sediaan_akhir
        else:
            sediaan_akhir_tetap = 10
            for i in range(n_predict):
                jualan = round(pred[i])
                produk_jadi = jualan + sediaan_akhir_tetap - sediaan
                produk_siap = jualan + sediaan_akhir_tetap
                bulan.append([jualan, sediaan_akhir_tetap, produk_siap, sediaan, produk_jadi])
                sediaan = sediaan_akhir_tetap

        kolom = {
            'Keterangan': ['Jualan', 'Sediaan akhir +', 'Produk siap dijual', 'Sediaan awal-', 'Produk jadi']
        }

        for i in range(n_predict):
            kolom[f"Bulan {i+1}"] = bulan[i]

        return pd.DataFrame(kolom)

    df_tm = make_table(y_tm, mode, sediaan, n_predict)
    df_lstm = make_table(y_lstm, mode, sediaan, n_predict)
    df_ens = make_table(y_ens, mode, sediaan, n_predict)

    tables["Trend Moment"] = df_tm.to_html(index=False)
    tables["LSTM"] = df_lstm.to_html(index=False)
    tables["Ensembled TM-LSTM"] = df_ens.to_html(index=False)

    with pd.ExcelWriter("static/data_output.xlsx") as writer:
        df_tm.to_excel(writer, sheet_name='Trend Moment', index=False)
        df_lstm.to_excel(writer, sheet_name='LSTM', index=False)
        df_ens.to_excel(writer, sheet_name='Ensembled TM-LSTM', index=False)

    # Plot
    N = data.shape[0]
    fig, axs = plt.subplots(3, 1, figsize=(6, 8), sharex=True)

    def plot_pred(ax, y_pred, title):
        full = pd.DataFrame(data['Jumlah'].copy())
        full = pd.concat([full, pd.DataFrame(y_pred, columns=['Jumlah'])], ignore_index=True)
        ax.plot(full.index[:N], data['Jumlah'], label='Aktual')
        ax.plot(full.index[N-1:], full['Jumlah'][N-1:], 'r-', label='Prediksi')
        ax.set_title(title)
        ax.legend()
        ax.grid()

    plot_pred(axs[0], y_tm, "Trend Moment")
    plot_pred(axs[1], y_lstm, "LSTM")
    plot_pred(axs[2], y_ens, "Ensembled")

    plt.tight_layout()
    plt.savefig("static/plot.png")
    plt.close()

    return render_template("index.html", tables=tables)

@app.route("/download")
def download_excel():
    return send_file("static/data_output.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
