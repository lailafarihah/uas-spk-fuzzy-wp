import streamlit as st
import pandas as pd

st.title('Fuzzy Weight Product')
st.write('                    ')

# Membuat input jumlah kriteria dan alternatif
col1, col2 = st.columns(2)
with col1:
    kriteria = st.number_input("Jumlah Kriteria", 0)
with col2:
    alternatif = st.number_input("Jumlah Alternatif", 0)
kriteria_alternatif = st.button("Next")

# Menyimpan jumlah kriteria dan alternatif dalam session_state
if kriteria_alternatif:
    st.session_state.kriteria = kriteria
    st.session_state.alternatif = alternatif

# Setelah input jumlah kriteria dan alternatif
if 'kriteria' in st.session_state and 'alternatif' in st.session_state:
    kriteria = st.session_state.kriteria
    alternatif = st.session_state.alternatif

    col1, col2, col3, col4 = st.columns(4)
    # Input nama kriteria
    with col1:
        st.write("##### Nama Kriteria")
        if 'kriteria_nama' not in st.session_state:
            st.session_state.kriteria_nama = [''] * int(kriteria)
        for i in range(int(kriteria)):
            st.session_state.kriteria_nama[i] = st.text_input(f"C {i + 1}", value=st.session_state.kriteria_nama[i], key=f"kriteria_{i}")

    # Input jenis kriteria
    with col2:
        st.write("##### Jenis Kriteria")
        if 'kriteria_jenis' not in st.session_state:
            st.session_state.kriteria_jenis = [''] * int(kriteria)
        for i in range(int(kriteria)):
            st.session_state.kriteria_jenis[i] = st.selectbox(
                f"Jenis C {i + 1}",
                options=["maks", "min"],
                index=0 if st.session_state.kriteria_jenis[i] == "" else ["maks", "min"].index(st.session_state.kriteria_jenis[i]),
                key=f"jenis_kriteria_{i}"
            )

    # Input jenis kriteria
    with col3:
        st.write("##### Fuzzy")
        if 'jenis_fuzzy' not in st.session_state:
            st.session_state.jenis_fuzzy = [''] * int(kriteria)
        for i in range(int(kriteria)):
            st.session_state.jenis_fuzzy[i] = st.selectbox(
                f"Fuzzy C{i + 1}",
                options=["linear naik", "linear turun"],
                index=0 if st.session_state.jenis_fuzzy[i] == "" else ["linear naik", "linear turun"].index(st.session_state.jenis_fuzzy[i]),
                key=f"fuzzy_{i}"
            )

    # Input nama alternatif
    with col4:
        st.write("##### Nama Alternatif")
        if 'alternatif_nama' not in st.session_state:
            st.session_state.alternatif_nama = [''] * int(alternatif)
        for i in range(int(alternatif)):
            st.session_state.alternatif_nama[i] = st.text_input(f"A {i + 1}", value=st.session_state.alternatif_nama[i], key=f"alternatif_{i}")

     # Input bobot untuk setiap kriteria
    st.subheader("Input Bobot untuk Setiap Kriteria")
    if 'bobot' not in st.session_state:
        st.session_state.bobot = [0] * kriteria
    col_bobot = st.columns(kriteria)  # Tetap menggunakan col_bobot
    for i in range(kriteria):
        st.session_state.bobot[i] = col_bobot[i].number_input(
            f"W {i + 1}", value=st.session_state.bobot[i], step=1, key=f"bobot_{i}"
        )
    
    # Input data alternatif terhadap kriteria
    st.subheader("Input Data Alternatif Terhadap Kriteria (Data Asli)")
    if 'data_alternatif' not in st.session_state:
        st.session_state.data_alternatif = [[0 for _ in range(kriteria)] for _ in range(alternatif)]
    for i in range(alternatif):
        col_data = st.columns(kriteria)  
        for j in range(kriteria):
            st.session_state.data_alternatif[i][j] = col_data[j].number_input(
                f"A{i+1}, C{j+1}",
                value=st.session_state.data_alternatif[i][j],
                step=1,
                key=f"data_a{i}_c{j}"
            )

    # Membuat DataFrame untuk menampilkan data alternatif
    columns = [f"C{j+1}" for j in range(kriteria)]
    index = [f"A{i+1}" for i in range(alternatif)]
    df_alternatif = pd.DataFrame(st.session_state.data_alternatif, columns=columns, index=index)


if 'kriteria_nama' in st.session_state and 'kriteria_jenis' in st.session_state and 'alternatif_nama' in st.session_state and 'bobot' in st.session_state and 'data_alternatif' in st.session_state:
    # Tombol hitung 
    Hitung= st.button("Hitung")

    # Setelah Klik Tombol Hitung
    if Hitung:
        # Tampilkan bobot yang telah diinput
        st.write("### Bobot")
        for i, bobot in enumerate(st.session_state.bobot):
            st.write(f"W{i + 1} = {bobot}")
            
        # Tampilkan tabel dengan judul kolom dan baris
        st.write("### Data Asli")
        st.table(df_alternatif)

        # Fungsi untuk menghitung keanggotaan fuzzy
        def linear_rise_membership(x, a, b): #linear naik
            if x <= a:
                return 0
            elif a < x < b:
                return (x - a) / (b - a)
            else:
                return 1

        def linear_fall_membership(x, a, b):  # linear turun
            if x <= a:
                return 1
            elif a < x <= b:  # Gunakan nilai b yang dikirim ke fungsi
                return (b - x) / (b - a)
            else:  # x > b
                return 0

        # Tentukan nilai a dan b 
        a = [1] * kriteria  # Titik awal untuk semua kriteria adalah 1
        b = [max([st.session_state.data_alternatif[i][j] for i in range(alternatif)]) for j in range(kriteria)]  # Nilai terbesar di setiap kriteria
        b_turun = [val + 1 for val in b]

        # Hitung keanggotaan fuzzy berdasarkan jenis fuzzy
        fuzzy_data = []
        for i in range(alternatif):
            fuzzy_row = []
            for j in range(kriteria):
                x = st.session_state.data_alternatif[i][j]
                if st.session_state.jenis_fuzzy[j] == "linear naik":
                    fuzzy_value = linear_rise_membership(x, a[j], b[j])
                else:  # "linear turun"
                    fuzzy_value = linear_fall_membership(x, a[j], b_turun[j])  # Gunakan b_turun[j]
                fuzzy_row.append(fuzzy_value)
            fuzzy_data.append(fuzzy_row)

        # Membuat DataFrame untuk menampilkan hasil keanggotaan fuzzy
        df_fuzzy = pd.DataFrame(fuzzy_data, columns=columns, index=index)

        st.write("### Data Setelah Fuzzy")
        st.table(df_fuzzy)

        # Perbaikan total bobot
        total_bobot = sum(st.session_state.bobot)
        if total_bobot > 0:
            bobot_normalisasi = [b / total_bobot for b in st.session_state.bobot]  # Normalisasi bobot
            st.write("### Perbaikan Bobot")
            for i, b in enumerate(bobot_normalisasi):
                st.write(f"W{i + 1} = {b:.4f}")
        else:
            st.error("Total bobot tidak boleh nol.")
        
        # Fungsi untuk menghitung nilai S 
        def hitung_S(fuzzy_value, bobot_normalisasi, kriteria_jenis):
            if kriteria_jenis == "maks":
                # Jika kriteria adalah 'maks', gunakan bobot normalisasi positif
                return fuzzy_value ** bobot_normalisasi
            else:
                # Jika kriteria adalah 'min', gunakan bobot normalisasi negatif
                return fuzzy_value ** -bobot_normalisasi

        # Menghitung nilai S untuk setiap alternatif dan kriteria
        S_values = []
        for i in range(alternatif):
            S_value = 1  # Inisialisasi S dengan 1 untuk perkalian
            for j in range(kriteria):
                # Hitung S dengan memperhatikan jenis kriteria (maks/min)
                fuzzy_value = fuzzy_data[i][j]  # Nilai fuzzy untuk alternatif i dan kriteria j
                bobot_normalisasi_value = bobot_normalisasi[j]  # Bobot normalisasi untuk kriteria j
                S_value *= hitung_S(fuzzy_value, bobot_normalisasi_value, st.session_state.kriteria_jenis[j])
            S_values.append(S_value)

        # Menampilkan hasil perhitungan S
        st.write("### Preferensi Alternatif")
        for i, S in enumerate(S_values):
            st.write(f"S{i+1} = {S:.4f}")

        # Menambahkan total dari semua nilai S
        total_S = sum(S_values)
        st.write(f"Total dari Semua Nilai S = {total_S:.4f}")

        # Menghitung preferensi relatif (V) untuk setiap alternatif
        V_values = [S / total_S for S in S_values]

        # Menampilkan hasil preferensi relatif
        st.write("### Preferensi Relatif")
        for i, V in enumerate(V_values):
            st.write(f"V{i+1} = {V:.4f}")

        # Menampilkan alternatif terbaik berdasarkan preferensi relatif
        alternatif_terbaik = V_values.index(max(V_values)) + 1
        alternatif_terbaik_nama = st.session_state.alternatif_nama[alternatif_terbaik - 1]
        st.write(f"### Alternatif terbaik adalah A{alternatif_terbaik} ({alternatif_terbaik_nama}) dengan nilai V = {max(V_values):.4f}")
