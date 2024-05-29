import scipy
from PyEMD import EMD
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, kurtosis
import os
import glob
from extract_name import extract_tokens


def Vc(buffer_original_voltage):
    emd = EMD()
    IMFs = emd(buffer_original_voltage)
    array_dinamico = np.array([])

    signal_sum = np.zeros(shape=buffer_original_voltage.shape)

    for i, mode in enumerate(IMFs):
        for j, value in enumerate(IMFs[i, :]):
            signal_sum[j] = signal_sum[j] + IMFs[i, j]
        corr, p_value = pearsonr(buffer_original_voltage, IMFs[i, :])
        array_dinamico = np.append(array_dinamico, corr)
    Vc_values = buffer_original_voltage - IMFs[-1]
    return Vc_values


def extract_features(buffer, Vc_values):
    Vc_values = np.array(Vc_values)

    abs_voltage_value = np.abs(Vc_values)
    peak_value = np.max(abs_voltage_value)
    mean_voltage = np.mean(Vc_values)
    squared_voltage_values = Vc_values ** 2
    mean_squared_voltage = np.mean(squared_voltage_values)
    rms_value = mean_squared_voltage ** 0.5
    skewness = scipy.stats.skew(Vc_values)
    crest_factor = peak_value / rms_value
    kurtosis_value = kurtosis(Vc_values)
    avg_abs_value = np.abs(Vc_values).mean()
    shape_factor = rms_value / avg_abs_value
    impulse_factor = peak_value / avg_abs_value
    noise_std = Vc_values.std()
    snr = mean_voltage / noise_std

    def calculate_clearance_factor(voltage_values):
        avg_sqrt_voltage = np.mean(np.sqrt(voltage_values))
        clearance_factor = peak_value / (avg_sqrt_voltage ** 2)
        return clearance_factor

    clearance_factor = calculate_clearance_factor(abs_voltage_value)

    original_voltage_values = buffer['Voltage(V)']

    def calculate_sample_std_dev(original_voltage_values):
        original_voltage_values = np.array(original_voltage_values)
        original_voltage_mean = np.mean(original_voltage_values)
        sum_squared_deviations = np.sum((original_voltage_values - original_voltage_mean) ** 2)
        N = len(original_voltage_values)
        sample_std_dev = np.sqrt(sum_squared_deviations / (N - 1))
        return sample_std_dev

    sample_std_dev = calculate_sample_std_dev(original_voltage_values)

    features = [peak_value, mean_voltage, rms_value, skewness, crest_factor, kurtosis_value, shape_factor,
                impulse_factor, snr, sample_std_dev, clearance_factor]
    return features


def extractNextBuffer(UDDS_df, bufferLength, currentTime):
    buffer = UDDS_df[(UDDS_df['Step_Time(s)'] >= currentTime) &
                     (UDDS_df['Step_Time(s)'] < currentTime + bufferLength)]
    if buffer.empty:
        print(currentTime, bufferLength)
        print("Warning: Buffer is empty.")
    return buffer


def extract_features_for_battery(excel_files_directory, feature_files_directory, file_name_template,
                                 buffer_length_in_mins, starting_time):
    excel_files = glob.glob(os.path.join(excel_files_directory, file_name_template))

    for i, excel_file in enumerate(excel_files, start=1):
        UDDS_df = pd.read_excel(excel_file)

        buffer_length_in_seconds = buffer_length_in_mins * 60
        buffer_start_time_in_seconds = starting_time * 60
        print(f"You chose a buffer of {buffer_length_in_seconds} seconds")
        print(f"Preparing file {i}")

        output_csv_file = os.path.join(feature_files_directory, f"features_{i}.csv")

        with open(output_csv_file, 'w') as file:
            file.write(
                "Peak Value,Mean Voltage,RMS,Skewness,Crest Factor,Kurtosis,Shape Factor,Impulse Factor,SNR,Sample Std Dev,Clearance Factor,Discharge_Capacity(Ah)\n")

        buffer_data = extractNextBuffer(UDDS_df, buffer_length_in_seconds, buffer_start_time_in_seconds)
        buffer_original_voltage = buffer_data["Voltage(V)"]
        buffer_original_voltage = np.array(buffer_original_voltage)

        while True:
            if buffer_data.empty:
                print("Buffer is empty. Exiting loop.")
                break

            Vc_values = Vc(buffer_original_voltage)
            features = extract_features(buffer_data, Vc_values)

            # Extract the last value of the "Discharge Capacity (Ah)" column
            last_discharge_capacity = buffer_data.iloc[-1]['Discharge_Capacity(Ah)']

            with open(output_csv_file, 'a') as file:
                features_with_discharge_capacity = features + [last_discharge_capacity]
                file.write(",".join(map(str, features_with_discharge_capacity)) + "\n")

            buffer_start_time_in_seconds += buffer_length_in_seconds

            buffer_data = extractNextBuffer(UDDS_df, buffer_length_in_seconds, buffer_start_time_in_seconds)
            buffer_original_voltage = buffer_data["Voltage(V)"]
            buffer_original_voltage = np.array(buffer_original_voltage)


def elenco_cartelle(input_folder, output_folder, buffer_length_in_mins, starting_time):
    if os.path.exists(input_folder) and os.path.isdir(input_folder):

        print(f"Elenco delle sottocartelle in '{input_folder}':")
        # Ottiene l'elenco di tutti i file e le cartelle nel percorso specificato
        cyclings_list = os.listdir(input_folder)

        # Filtra solo le cartelle
        cycling_folders_list = [c for c in cyclings_list if os.path.isdir(os.path.join(input_folder, c))]

        # Stampa l'elenco delle cartelle, se presenti
        if cycling_folders_list:
            for input_cycles_path in cycling_folders_list:
                output_cycles = os.path.join(output_folder, input_cycles_path)
                os.makedirs(output_cycles, exist_ok=True) # makedirs creates a folder.

                input_cycles_path = os.path.join(input_folder, input_cycles_path)
                print(input_cycles_path)

                batteryList = os.listdir(input_cycles_path)
                battery_folders = [c for c in batteryList if os.path.isdir(
                    os.path.join(input_cycles_path, c)) and c != '_processed_mat' and c != '__MACOSX']
                for battery_folder in battery_folders:
                    output_battery_folder = os.path.join(output_cycles, battery_folder)
                    os.makedirs(output_battery_folder, exist_ok=True)

                    battery_folder = os.path.join(input_cycles_path, battery_folder)
                    print(battery_folder)
                    first_file = os.listdir(battery_folder)[0]
                    file_name_template, sheet_name = extract_tokens(first_file)
                    file_name_template = file_name_template + "out.*.xlsx"
                    print(file_name_template )
                    extract_features_for_battery(battery_folder, output_battery_folder ,file_name_template, buffer_length_in_mins,
                                                 starting_time)


def main():
    input_folder = "/home/haseeb/Data/Cycling_done"
    output_folder = "/home/haseeb/Data/features"
    buffer_length_in_mins = 60  # Adjust as needed
    starting_time = 0  # Adjust as needed

   # file_name_template = "INR21700_M50T_T23_Aging_UDDS_SOC20_80_CC_0_5C_N25_W8_Channel_4.out.*.xlsx"
    #excel_files_directory = input_folder + "\\Cycling1\\W8"
    #file_name_template = output_folder + "\\Cycling1\\W8"

    elenco_cartelle(input_folder, output_folder, buffer_length_in_mins, starting_time)



if __name__ == "__main__":
    main()