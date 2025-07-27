#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 16:30:22 2025

@author: august
"""

import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

from phase_matching_class import phase_matching as PM

%matplotlib inline

# Variable globale pour l'image
logo_img = None

# plotter les figures
fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()

def generate_plots():
    try:
        # Récupérer les valeurs
        var1 = var1_combobox.get()  # Modification ici
        var2 = float(entry_var2.get())
        var3 = float(entry_var3.get())
        var4 = float(entry_var4.get())
        var5 = float(entry_var5.get())
        
        
        obj_PM = PM(var1, var2, var3, var4, var5)
        theta_fluo_out_list, delta_k_list, turning_angle, k_gate, k_gate_out, k_somme, r_c, k_fluo, k_fluo_out = obj_PM.get_PM()
        
        ax1.clear()
        ax2.clear()
        
        # Figure 1
        ax1.set_title('minimum |Δk| at turning angle : {}°'.format(round(turning_angle, 1)))
        ax1.plot(theta_fluo_out_list, delta_k_list)
        ax1.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        ax1.set_xlabel('turning angle (°)')
        ax1.set_ylabel('|Δk| (1/μm)')
        ax1.grid() 
        
        # Figure 2        
        # plotting gate vector
        ax2.set_title('k vectors at phase matching condition')
        ax2.set_xlabel('k_x (1/μm)')
        ax2.set_ylabel('k_y (1/μm)')
        ax2.plot(np.nan, np.nan, color='grey', label='air-BBO interface')
        ax2.plot(np.nan, np.nan, color='grey',ls='--', label='BBO surface normal')
        ax2.set_aspect('equal')
        origin = [0], [0]

        ax2.quiver(*origin, k_gate[0], k_gate[1],  color='red', label='k_gate',
                   angles='xy', scale_units='xy', scale=1, alpha=0.4)
        ax2.quiver(-k_gate_out[0], -k_gate_out[1], k_gate_out[0], k_gate_out[1], 
                   color='red', 
                    angles='xy', scale_units='xy', scale=1,)
        
        # plotting fluo vector
        ax2.quiver(*origin, k_fluo[0], k_fluo[1],  color='blue', label='k_fluo',
                   angles='xy', scale_units='xy', scale=1, alpha=0.4)
        ax2.quiver(-k_fluo_out[0], -k_fluo_out[1], k_fluo_out[0], k_fluo_out[1], 
                   color='blue',
                    angles='xy', scale_units='xy', scale=1,)
        
        # plotting sum vector
        ax2.quiver(*origin, k_somme[0], k_somme[1],  color='purple', label='k_s',
                   angles='xy', scale_units='xy', scale=1, alpha=0.4)
        
        # plotting optic axis
        ax2.quiver(*origin, r_c[0]*100, r_c[1]*100,  color='yellow', label='optic axis',
                   angles='xy', scale_units='xy', scale=1, alpha=0.8, linewidth=0.2)
        
        xlim = max(abs(k_somme[0]), abs(k_gate[0]), abs(k_fluo[0]))+0.5
        ylim = max(abs(k_somme[1]),abs(k_gate_out[1]), abs(k_fluo_out[1]))+0.5
        
        xylim = max(xlim, ylim)
        
        ax2.set_xlim(-xylim, xylim)
        ax2.set_ylim(-xylim, xylim)
        ax2.vlines(0, -xylim, xylim, color='grey')
        ax2.hlines(0, -xylim/2, xylim/2, color='grey', linestyle='--')
        ax2.text(0.34, 0.15, "air", fontsize='20', transform=ax2.transAxes)
        ax2.text(0.6, 0.15, "BBO", fontsize='20', transform=ax2.transAxes)
        ax2.legend(loc='upper left')
        
        error_label.config(text="")
          
        # c) Redessiner sur les canvases existants
        canvas1.draw()
        canvas2.draw()
    except ValueError:
        error_label.config(text="Veuillez entrer des nombres valides")


# Création de la fenêtre principale
root = Tk()
root.title("TYpe II BBO phase matching")
root.geometry("1200x900")

# Frame pour les paramètres
param_frame = ttk.LabelFrame(root, text="Paramètres d'entrée", padding=10)
param_frame.pack(fill=X, padx=10, pady=5)

# Frame pour les entrées (à gauche)
input_frame = ttk.Frame(param_frame)
input_frame.pack(side=LEFT, fill=BOTH, expand=True)

# Menu déroulant pour var1 (case A ou case B)
ttk.Label(input_frame, text="optical axis configuration:").grid(row=0, column=0, padx=5, pady=2, sticky=W)
var1_combobox = ttk.Combobox(input_frame, values=['case A', 'case B'], width=8, state="readonly")
var1_combobox.grid(row=0, column=1, padx=5, pady=2)
var1_combobox.set('case A')  # Valeur par défaut

# Autres champs de saisie (inchangés)
ttk.Label(input_frame, text="gate wavelength (nm):").grid(row=1, column=0, padx=5, pady=2, sticky=W)
entry_var2 = ttk.Entry(input_frame, width=8)
entry_var2.grid(row=1, column=1, padx=5, pady=2)
entry_var2.insert(0, "1480")

ttk.Label(input_frame, text="pump wavelength (nm):").grid(row=2, column=0, padx=5, pady=2, sticky=W)
entry_var3 = ttk.Entry(input_frame, width=8)
entry_var3.grid(row=2, column=1, padx=5, pady=2)
entry_var3.insert(0, "370")

ttk.Label(input_frame, text="theta_gate_pump (°):").grid(row=3, column=0, padx=5, pady=2, sticky=W)
entry_var4 = ttk.Entry(input_frame, width=8)
entry_var4.grid(row=3, column=1, padx=5, pady=2)
entry_var4.insert(0, "8.5")

ttk.Label(input_frame, text="theta_cut (°):").grid(row=4, column=0, padx=5, pady=2, sticky=W)
entry_var5 = ttk.Entry(input_frame, width=8)
entry_var5.grid(row=4, column=1, padx=5, pady=2)
entry_var5.insert(0, "25")

# Bouton de génération
generate_btn = ttk.Button(input_frame, text="Générer", command=generate_plots)
generate_btn.grid(row=5, column=0, columnspan=2, pady=5)

# Message d'erreur
error_label = ttk.Label(input_frame, text="", foreground="red")
error_label.grid(row=6, column=0, columnspan=2)

# Logo (à droite) - inchangé
logo_frame = ttk.Frame(param_frame)
logo_frame.pack(side=RIGHT, padx=10)
img = Image.open("caseA_caseB.png")
img.thumbnail((700, 700))

logo_img = ImageTk.PhotoImage(img)
ttk.Label(logo_frame, image=logo_img).pack()


# Frames pour les graphiques (inchangés)
plots_frame = ttk.Frame(root)
plots_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

frame1 = ttk.LabelFrame(plots_frame, text="|Δk| vs turning angle",width=80, height=100)
frame1.pack(side=LEFT, fill=BOTH, expand=False, padx=5, pady=5)

frame2 = ttk.LabelFrame(plots_frame, text="k vectors",width=180, height=100)
frame2.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)

# 5. Création unique des canvases et pack
canvas1 = FigureCanvasTkAgg(fig1, master=frame1)
canvas1.get_tk_widget().pack(fill=BOTH, expand=True)

canvas2 = FigureCanvasTkAgg(fig2, master=frame2)
canvas2.get_tk_widget().pack(fill=BOTH, expand=True)

# Génération initiale
generate_plots()

root.mainloop()