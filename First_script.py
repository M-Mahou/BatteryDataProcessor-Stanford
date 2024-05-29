import sys
import pandas as pd
from openpyxl import load_workbook
import numpy as np
import os
from extract_name import extract_tokens

def load_cycle(file_number, starting_row, output_file_number, abs_name, sheet_name):
    # Inizializzazione di una lista vuota per raccogliere le righe
    righe_da_aggiungere = []

    ending_row, righe_da_aggiungere, cont_condition = load_data(abs_name, file_number, starting_row,
                                                    righe_da_aggiungere, sheet_name)

    if (ending_row < 0):
        print("non trovato")
        starting_row = 0
        file_number = file_number + 1

        ending_row, righe_da_aggiungere, cont_condition  = load_data(abs_name, file_number, starting_row,
                                                        righe_da_aggiungere, sheet_name)

        if ending_row < 0:
            file_number = file_number + 1
            starting_row = 0

            ending_row, righe_da_aggiungere, cont_condition  = load_data(abs_name, file_number, starting_row,
                                                            righe_da_aggiungere, sheet_name)

    # nuovo_df = pd.DataFrame(columns=df.columns)

    nuovo_df = pd.DataFrame(righe_da_aggiungere).reset_index(drop=True)
    print(f" ending row: {ending_row}")
    print(f" file_number: {file_number}")
    nuovo_df.to_excel(abs_name + "out." + str(output_file_number) + ".xlsx", index=False)


    return  file_number, ending_row, cont_condition


def load_data(abs_name, file_number, starting_row, righe_da_aggiungere, sheet_name):

    step_index_end = 14
    step_index_start = 7
    colonna_di_ricerca = 'Step_Index'
    abs_name = abs_name + str(file_number) + ".xlsx"
    print(abs_name)
    if not os.path.exists(abs_name):
        return 0, righe_da_aggiungere, False

    df = pd.read_excel(abs_name, sheet_name=sheet_name)
    ending_row = -1


    # Siccome cerchiamo coppie di valori in righe consecutive,
    # dobbiamo iterare fino alla penultima riga per confrontare ciascuna riga con la successiva
    for i in range(starting_row, len(df) - 1):  # len(df) - 1 per non andare oltre l'ultima riga
        # Controlla se la riga corrente ha il valore1 e la riga successiva il valore2
        if df.iloc[i][colonna_di_ricerca] == step_index_end and df.iloc[i + 1][colonna_di_ricerca] == step_index_start:
            ending_row = i
            righe_da_aggiungere.append(df.iloc[i])
            break
        else:
            if step_index_end == df.iloc[i][colonna_di_ricerca]:
                righe_da_aggiungere.append(df.iloc[i])
    return ending_row, righe_da_aggiungere, True

#
def load_cycling(abs_name, sheet_name):
    cont_condition = True
    ending_row = 0
    file_number = 1
    starting_row = 0
    output_file_number = 1
    while cont_condition:
        print(file_number, starting_row, cont_condition, output_file_number)
        file_number, ending_row, cont_condition = load_cycle(file_number, starting_row, output_file_number, abs_name, sheet_name)
        print(file_number, ending_row, cont_condition, output_file_number)
        starting_row = ending_row + 1
        output_file_number += 1



def elenco_cartelle(cartella, file_name, sheet_name):
  """
  Stampa a video l'elenco delle sottocartelle contenute in una cartella data.

  :param cartella: Percorso della cartella di cui stampare le sottocartelle.
  """
  if os.path.exists(cartella) and os.path.isdir(cartella):
    print(f"Elenco delle sottocartelle in '{cartella}':")
    # Ottiene l'elenco di tutti i file e le cartelle nel percorso specificato
    contenuti = os.listdir(cartella)

    # Filtra solo le cartelle
    cartelle = [c for c in contenuti if os.path.isdir(os.path.join(cartella, c))]

    # Stampa l'elenco delle cartelle, se presenti
    if cartelle:
      for sotto_cartella in cartelle:
        sotto_cartella = os.path.join(cartella, sotto_cartella)
        print(sotto_cartella)
        contenuti = os.listdir(sotto_cartella)
        battery_folders = [c for c in contenuti if os.path.isdir(os.path.join(sotto_cartella, c)) and c != '_processed_mat' and c != '__MACOSX']
        for battery_folder in battery_folders:


          battery_folder = os.path.join(sotto_cartella, battery_folder)
          first_file = os.listdir(battery_folder)[0]
          file_name, sheet_name = extract_tokens(first_file)

          load_cycling(os.path.join(battery_folder , file_name), sheet_name)
          print("\t" + battery_folder)


    else:
      print("Nessuna sottocartella trovata.")

  else:
    print("Il percorso specificato non esiste o non è una cartella.")



if __name__ == "__main__":

    sheet_name = "Channel_4_1"
    file_name = "INR21700_M50T_T23_Aging_UDDS_SOC20_80_CC_0_5C_N25_W8_Channel_4."
    percorso_cartella = "C:\\Users\\ayazh\\Desktop\\Master stage\\Cycling_tests"
    elenco_cartelle(percorso_cartella, file_name, sheet_name)







