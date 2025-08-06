import pandas as pd

def read_data_vmedis(file_path):
    
    datafile = pd.read_excel(file_path)
    datapenjualan=datafile[['Tanggal','Jumlah']]
    datapenjualan['Tanggal']=pd.to_datetime(datapenjualan['Tanggal'], format="%d %b %Y %H:%M:%S")
    datapenjualan['Bulan_Tahun'] = datapenjualan['Tanggal'].dt.strftime('%B %Y')
    print(datapenjualan)
    
    datapenjualanperbulan = datapenjualan.groupby('Bulan_Tahun')['Jumlah'].sum()
    datapenjualanperbulan = datapenjualanperbulan.reset_index()

    datapenjualanperbulan['SortKey'] = pd.to_datetime(datapenjualanperbulan['Bulan_Tahun'], format='%B %Y')
    datapenjualanperbulan = datapenjualanperbulan.sort_values('SortKey').reset_index(drop=True)
    datapenjualanperbulan = datapenjualanperbulan.drop(columns='SortKey')
    print(datapenjualanperbulan)

    return datapenjualanperbulan

    