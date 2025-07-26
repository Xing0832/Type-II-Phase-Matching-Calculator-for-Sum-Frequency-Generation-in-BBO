#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 16:30:22 2025

@author: august
"""
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

from phase_matching_class import phase_matching as PM


# Variable globale pour l'image
logo_img = None

def generate_plots():
    try:
        # Récupérer les valeurs
        var1 = var1_combobox.get()  # Modification ici
        var2 = float(entry_var2.get())
        var3 = float(entry_var3.get())
        var4 = float(entry_var4.get())
        var5 = float(entry_var5.get())
        
        plt.figure('delta_k')
        plt.clf()
        plt.figure('k')
        plt.clf()
        
        obj_PM = PM(var1, var2, var3, var4, var5)
        turning_angle, fig1, fig2 = obj_PM.get_PM()
        
        # Figure 1
        plt.figure('delta_k')
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
        plt.title('minimum |Δk| at turning angle : {}°'.format(round(turning_angle, 1)))
        plt.xlabel('turning angle (°)')
        plt.ylabel('|Δk| (1/μm)')
        plt.grid() 
        
        # Figure 2
        plt.figure('k')
        plt.title('k vectors at phase matching condition')
        plt.xlabel('k_x (1/μm)')
        plt.ylabel('k_y (1/μm)')
        
        # Afficher les figures
        show_figure(fig1, frame1)
        show_figure(fig2, frame2)
        
        error_label.config(text="")
    except ValueError:
        error_label.config(text="Veuillez entrer des nombres valides")

def show_figure(figure, frame):
    for widget in frame.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=BOTH, expand=True)

# Création de la fenêtre principale
root = Tk()
root.title("TYpe II BBO phase matching")
root.geometry("900x700")

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
img.thumbnail((600, 600))

logo_img = ImageTk.PhotoImage(img)
ttk.Label(logo_frame, image=logo_img).pack()


# Frames pour les graphiques (inchangés)
plots_frame = ttk.Frame(root)
plots_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

frame1 = ttk.LabelFrame(plots_frame, text="Figure 1")
frame1.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

frame2 = ttk.LabelFrame(plots_frame, text="Figure 2")
frame2.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

# Génération initiale
generate_plots()

root.mainloop()