from tkinter import *
from tkinter import ttk
from math import log10, sqrt
from tkinter.filedialog import askopenfile
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame

judul = "Specsi Program v1.2"


def takefromfile():
    file = askopenfile(mode='r', filetypes=[('Text Files', '*.txt')])
    if file is not None:
        data = pd.read_csv(filepath_or_buffer=file)
        # asumsi file masih merupakan data individual
        p = data.at[0, "Pressure"]
        t = data.at[0, "Temperature"]
        s = data.at[0, "Salinity"]
        reset()
        e1.insert(0, t)
        e2.insert(0, p)
        e3.insert(0, s)
        hitung()


def printtofile():
    T = str(e1.get())
    P = str(e2.get())
    S = str(e3.get())
    V = str(e4.get())
    D = str(e5.get())
    hasil = open("hasil.txt", "a+")

    hasil.write("\nData perhitungan :\n")
    hasil.write("Pressure : " + P + " desibar\n")
    hasil.write("Temperature : " + T + " \N{DEGREE SIGN}C\n")
    hasil.write("Salinity : " + S + " PSS-78\n")
    hasil.write("Hasil perhitungan :\n")
    hasil.write("Spesific Volume Anomaly : " + V + " M\u00B3/Kg\n")
    hasil.write("Density Anomaly : " + D+" Kg/M\u00B3")

    hasil.close()


def hitung():  # Input yang diterima program
    #global P, T, S, volume, densitas

    # tekanan dalam satuan desibar
    # temperatur dalam satuan deg celcius
    # salinitas (PSS-78)
    #  Asumsi input dalam angkat positif
    # Odd; should never have negative S anyway.
    try:
        T = float(e1.get())
        P = float(e2.get())
        S = float(e3.get())
    except:
        e4.delete(0, END)
        e5.delete(0, END)
        e4.insert(0, "Masukkan Angka Saja")
        e5.insert(0, "Masukkan Angka Saja")

    else:
        if T < 0:
            e1.delete(0, END)
            e1.insert(0, "value outside range!")
        if P < 0 or P > 10000:
            e2.delete(0, END)
            e2.insert(0,  "value outside range!")
        if S < 0 or S > 40:
            e3.delete(0, END)
            e3.insert(0,  "value outside range!")
        else:
            P = P/10  # mengubah satuan tekanan menjadi BAR
            SR = sqrt(abs(S))  # mengambil akar dari salinitas
        # notes:
        # R1-> pure warter density at atmospheric pressure
        # R2-> seawater density atm pressure coeff involving salinity (notasi "A" dalam Millero dan Poisson, 1981)
        # R3-> seawater density atm pressure coeff involving salinity (notasi "B" dalam Millero dan Poisson, 1981)
        # R4-> notasi "C" dalam Millero dan Poisson, 1981
        # PURE WATER DENSITY AT ATMOSPHERIC PRESSURE
        #  program processing
            # BIGG P.H(1967) BR. J  APPLIED PHYSICS 8 PP 521-537
            R1 = ((((6.536332e-9*T-1.120083e-6)*T+1.001685e-4)
                   * T-9.095290e-3)*T+6.793952e-2)*T-28.263737
            # SEAWATER DENSITY ATM PRESS. COEFFICIENTS INVOLVING SALINITY
            #  "A" NOTATION OF MILLERO AND POISSON 1981
            R2 = (((5.3875e-9*T-8.2467e-7)*T+7.6438e-5)
                  * T-4.0899e-3)*T+8.24493e-1
            # "B" NOTATION OF MILLERO AND POISSON 1981
            R3 = (-1.6546e-6*T+1.0227e-4)*T-5.72466e-3

            R4 = 4.8314e-4
            R3500 = 1028.1063
            DR350 = 28.106331

            # Olah data
            # INTERNATIONAL ONE-ATMOSPHERE EQUATION OF STATE OF SEAWATER
            SIG = (R4*S + R3*SR + R2)*S + R1
            # SPECIFIC VOLUME AT ATMOSPHERIC PRESSURE
            V350P = 1.0/R3500
            SVA = -SIG*V350P/(R3500+SIG)
            # specific volume anomaly dengan P = 0
            SIGMA = SIG+DR350
        # SCALE SPECIFIC VOL. ANAMOLY TO NORMALLY REPORTED UNITS
            SVAN = SVA*1.0e+8

            # menghitung compressi
            E = (9.1697e-10*T+2.0816e-8)*T-9.9348e-7
            BW = (5.2787e-8*T-6.12293e-6)*T+3.47718e-5
            B = BW + E*S

            # menghitung compressi
            D = 1.91075e-4
            C = (-1.6078e-6*T-1.0981e-5)*T+2.2838e-3
            AW = ((-5.77905e-7*T+1.16092e-4)*T+1.43713e-3)*T-0.1194975
            A = (D*SR + C)*S + AW

            # variabel perhitungan compressi
            B1 = (-5.3009e-4*T+1.6483e-2)*T+7.944e-2
            A1 = ((-6.1670e-5*T+1.09987e-2)*T-0.603459)*T+54.6746
            KW = (((-5.155288e-5*T+1.360477e-2)*T-2.327105)*T+148.4206)*T-1930.06
            KO = (B1*SR + A1) * S + KW
        # EVALUATE PRESSURE POLYNOMIAL
        # K EQUALS THE SECANT BULK MODULUS OF SEAWATER
        # DK=K(S,T,P)-K(35,0,P)
        # K35=K(35,0,P)
            DK = (B*P+A)*P + KO
            K35 = (5.03217e-5*P+3.359406)*P+21582.27
            GAM = P/K35
            PK = 1.0 - GAM
            SVA = SVA*PK + (V350P + SVA)*P*DK/(K35*(K35+DK))

            # Hasil perhitungan anomali volume
            SVAN = SVA*1.0e+8
            V350P = V350P*PK

            # Hasil perhitungan anomali densitas
            DR35P = GAM/V350P
            DVAN = SVA/(V350P*(V350P+SVA))
            # Density Anomaly
            DAN = DR350+DR35P-DVAN

            volume = SVAN
            densitas = DAN
            return_data(volume, densitas)


def reset():
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)
    e4.delete(0, END)
    e5.delete(0, END)


def return_data(data1, data2):
    e4.delete(0, END)
    e5.delete(0, END)
    e4.insert(0, "{:.2f}".format(data1))
    e5.insert(0, "{:.4f}".format(data2))


'''
main program
'''


jndl = Tk()
jndl.title(judul)
jndl.resizable(False, False)
# Setting icon of master window
p1 = PhotoImage(file='s.png')
jndl.iconphoto(False, p1)
l1 = Label(jndl, text="Suhu:")
l2 = Label(jndl, text="Tekanan:")
l3 = Label(jndl, text="Salinitas:")
l4 = Label(jndl, text="\N{DEGREE SIGN}C")
l5 = Label(jndl, text="desibar")
l6 = Label(jndl, text="PSS-78")
l7 = Label(jndl, text="Hasil perhitungan")
l8 = Label(jndl, text="Anomali Volume: ")
l10 = Label(jndl, text="Anomali Densitas: ")
l12 = Label(jndl, text=" M\u00B3/Kg")
l13 = Label(jndl, text=" Kg/M\u00B3")
# grid method to arrange labels in respective

# rows and columns as specified
l1.grid(row=1, column=0, sticky=W, pady=2)
l2.grid(row=2, column=0, sticky=W, pady=2)
l3.grid(row=3, column=0, sticky=W, pady=2)
l4.grid(row=1, column=2, sticky=W, pady=2)
l5.grid(row=2, column=2, sticky=W, pady=2)
l6.grid(row=3, column=2, sticky=W, pady=2)
l7.grid(row=1, column=4, sticky=W, pady=2)
l8.grid(row=2, column=4, sticky=W, pady=2)
l10.grid(row=3, column=4, sticky=W, pady=2)
l12.grid(row=2, column=6, sticky=W, pady=2)
l13.grid(row=3, column=6, sticky=W, pady=2)


# entry widgets, used to take entry from user
e1 = Entry(jndl)
e2 = Entry(jndl)
e3 = Entry(jndl)
e4 = Entry(jndl)
e5 = Entry(jndl)

b1 = Button(jndl, text="Hitung!", command=hitung)
b2 = Button(jndl, text="Print", command=printtofile)
b3 = Button(jndl, text="Reset", command=reset)
b4 = Button(jndl, text="Insert", command=takefromfile)
# this will arrange entry widgets
e1.grid(row=1, column=1, pady=2)
e2.grid(row=2, column=1, pady=2)
e3.grid(row=3, column=1, pady=2)
e4.grid(row=2, column=5, sticky=W, pady=2)
e5.grid(row=3, column=5, sticky=W, pady=2)

b1.grid(row=4, column=3)
b2.grid(row=4, column=8)
b3.grid(row=4, column=4)
b4.grid(row=4, column=7)
# Run the GUI
jndl.mainloop()
