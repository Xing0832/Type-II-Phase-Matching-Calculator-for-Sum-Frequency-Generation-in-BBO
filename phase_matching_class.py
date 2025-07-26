#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 26 14:04:40 2025

@author: august
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar


class __toolbox__():
    def __init__(self):
        pass
    
    '''
    ##############################################################################
    bibliotèque de fonctions
    
    ref pour n_wl_gate :
        doi:10.1063/1.339536 
    
    ref pour ne_theta :
        Born & Wolf, Principles of Optics (7th ed.)
    
    ##############################################################################
    '''
    @staticmethod
    # dependance de longueur d'onde
    def n_wl(wl,pola):
        if pola == 'e':
            A = 2.3730
            B = 0.0128
            C = -0.0156
            D = -0.0044
        elif pola == 'o':
            A = 2.7405
            B = 0.0184
            C = -0.0179
            D = -0.0155
        else:
            print('pola must be e or o')
            return
        wl /= 1000
        n_sq = A + B / (wl**2 + C) + D*wl**2
        
        return n_sq**0.5
    
    @staticmethod
    # dependance angulaire
    def ne_theta(theta, ne90, no):
        '''
        theta: l'angle entre k et l'axe optique en radian
        ne90: valeur de ne sortant de n_wl
        no: valeur de no sortant de n_wl
        '''
        inver_ne_sq = np.sin(theta)**2/(ne90**2) + np.cos(theta)**2/(no**2)
        return (1/inver_ne_sq)**0.5
    
    @staticmethod
    # deviation de loi Snell
    def Snell_deviation(theta_in, theta_out, ne90_in, no_in, n_out, theta_cut):
    
        theta_c = theta_cut - theta_in
            
        ne_theta_c = __toolbox__.ne_theta(theta_c, ne90_in, no_in)
        
        # calculer la différence entre sin(theta_out)/sin(theta_in) et n_out, n_in
        Snell_dev = abs(np.sin(theta_out)/np.sin(theta_in) - ne_theta_c/n_out)
        
        return Snell_dev
    
    ########################### coordonnées polaires ############################
    
    @staticmethod
    # polaire à cartésien
    def polar_2_cartes(v_polar):
        x = np.cos(v_polar[0])*v_polar[1]
        y = np.sin(v_polar[0])*v_polar[1]
        return np.array([x,y])
    
    
    ################################# vecteurs ##################################
    
    @staticmethod
    # angle entre deux vecteurs
    def angle_entre_vecteurs(u, v):
        """
        Calcule l'angle entre deux vecteurs u et v (en radians et degrés).
        """
        u = np.array(u)
        v = np.array(v)
    
        # Produit scalaire
        dot = np.dot(u, v)
    
        # Normes
        norm_u = np.linalg.norm(u)
        norm_v = np.linalg.norm(v)
    
        # Cosinus de l'angle
        cos_theta = dot / (norm_u * norm_v)
    
        # Clamp la valeur pour éviter des erreurs numériques (ex. cos_theta > 1 à cause de l'arrondi)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
        # Angle en radians
        theta_rad = np.arccos(cos_theta)
    
        return theta_rad
    
    @staticmethod
    # k_fluo dans le cristal
    def get_k_fluo(wl, n_out, n_in, theta_out):
        theta_in = np.arcsin(np.sin(theta_out)*n_out/n_in)
        k_longueur = 2 * np.pi * n_in / (wl/1000)
        k_fluo = __toolbox__.polar_2_cartes([theta_in, k_longueur])
        return k_fluo
    
    @staticmethod
    # k_gate dans le cristal
    def get_k_gate_and_ne(wl, n_out, no_in, ne_in_90, theta_out, theta_cut):
        if theta_out < 0: 
            theta_in_bound = [theta_out, 0]
        else:
            theta_in_bound = [0, theta_out] # y compris theta_out_gate == 0 
        res = minimize_scalar(__toolbox__.Snell_deviation, bounds=theta_in_bound, method='bounded',
                              args=(theta_out, ne_in_90, no_in, n_out, theta_cut))
        theta_in = res.x
        
        ne_in = __toolbox__.ne_theta(theta_in, ne_in_90, no_in)
        k_longueur = 2 * np.pi * ne_in / (wl/1000)
        
        k_gate = __toolbox__.polar_2_cartes([theta_in, k_longueur])
        return k_gate, ne_in
    
    
class phase_matching(__toolbox__):
    def __init__(self, config, wl_gate, wl_fluo, theta_fluo_gate, theta_cut):
        self.wl_gate = wl_gate
        self.wl_fluo = wl_fluo
        self.config = config
        self.theta_fluo_gate = theta_fluo_gate
        self.theta_cut = theta_cut
        
    def get_PM(self):
        
        '''
        ##############################################################################
        partie 1: définir gate et pompe en dehors, angle externelle du cystal
        ##############################################################################
        '''
        
        ########################### partie constante ################################
        
        # longueur d'onde de la pompe et de la gate
        wl_gate = self.wl_gate
        wl_fluo = self.wl_fluo
        wl_somme = 1/ (1/wl_fluo + 1/wl_gate)
        
        # toutes les indices de réfraction indépendantes à theta
        ne90_gate = __toolbox__.n_wl(wl_gate, 'e')
        no_gate = __toolbox__.n_wl(wl_gate, 'o')
        no_fluo = __toolbox__.n_wl(wl_fluo, 'o')
        n_air = 1.000293
        
        # définir la géométrie constante
        config = self.config
        theta_fluo_gate = self.theta_fluo_gate * np.pi / 180
        theta_cut = self.theta_cut * np.pi / 180 
        
        if config == 'case A':
            theta_cut *= -1
        
        
        # l'axe optique du cristal
        r_c = __toolbox__.polar_2_cartes([theta_cut, 1])
        
        ########################### partie à optimiser ###############################
        
        # définir la géométrie à optimiser en utilisant la convention d'Ernsting (fluo_out en dessous)
        theta_fluo_out_list = np.linspace(-np.pi/2 + theta_fluo_gate, np.pi/2, 200)
        
        
        '''
        ##############################################################################
        partie 2: optimisation
        ##############################################################################
        '''
        
        delta_k_list = []
        for theta_fluo_out in theta_fluo_out_list:
            
            # calculer k_gate, k_fluo, et k_somme et ses indices de réfraction
            theta_gate_out = theta_fluo_out - theta_fluo_gate
            
            k_gate, ne_gate = __toolbox__.get_k_gate_and_ne(wl_gate, n_air, 
                                                   no_gate, ne90_gate, 
                                                   theta_gate_out, theta_cut)
            
            k_fluo = __toolbox__.get_k_fluo(wl_fluo, n_air, no_fluo, theta_fluo_out)
            
            k_somme = k_gate + k_fluo
            
            ne_somme = __toolbox__.ne_theta(__toolbox__.angle_entre_vecteurs(r_c, k_somme), 
                                   __toolbox__.n_wl(wl_somme, 'e'), 
                                   __toolbox__.n_wl(wl_somme, 'o'))
            
            # calculer l'angle entre entre k_gate et k_somme, et l'angle entre k_fluo et k_somme
            theta_g_s = __toolbox__.angle_entre_vecteurs(k_somme, k_gate)
            theta_f_s = __toolbox__.angle_entre_vecteurs(k_somme, k_fluo)
            
            # test
            theta_g_c = __toolbox__.angle_entre_vecteurs(r_c, k_gate)
            ne_gate_somme_direction = __toolbox__.ne_theta(theta_g_c, ne90_gate, no_gate)
            
            # calculer delta_k en 2*pi/nm
            delta_k = abs( no_fluo*np.cos(theta_f_s)/wl_fluo + ne_gate_somme_direction*np.cos(theta_g_s)/wl_gate - ne_somme/wl_somme )
            
            delta_k_list.append(delta_k)
        
        
        '''
        ##############################################################################
        partie 3: visualisation
        ##############################################################################
        '''
        ########################### montrer les resi ###############################
        
        fig_delta_k = plt.figure('delta_k', constrained_layout=True)
        plt.plot(theta_fluo_out_list*180/np.pi, delta_k_list)
        
        theta_fluo_out_opt = theta_fluo_out_list[np.where(delta_k_list == min(delta_k_list))[0][0]]
        
        # print('###################################################################')
        # print('turning angle:', theta_fluo_out_opt*180/np.pi)
        # print('###################################################################')
        
        ########################### dessiner les vecteurs ############################
        
        # à l'intérieur
        theta_gate_out = theta_fluo_out_opt - theta_fluo_gate
        k_gate, ne_gate = __toolbox__.get_k_gate_and_ne(wl_gate, n_air, 
                                                        no_gate, ne90_gate, 
                                                        theta_gate_out, theta_cut)
        
        k_fluo = __toolbox__.get_k_fluo(wl_fluo, n_air, no_fluo, theta_fluo_out_opt)
        
        k_somme = k_gate + k_fluo
        
        # à l'extérieur
        k_gate_out = __toolbox__.polar_2_cartes([theta_gate_out, 2*np.pi*n_air/(wl_gate/1000)])
        k_fluo_out = __toolbox__.polar_2_cartes([theta_fluo_out_opt, 2*np.pi*n_air/(wl_fluo/1000)])
        
        
        # plotting
        fig_k = plt.figure('k')
        plt.gca().set_aspect('equal')
        
        origin = [0], [0]
        
        # plotting gate vector
        plt.quiver(*origin, k_gate[0], k_gate[1],  color='red', label='k_gate',
                   angles='xy', scale_units='xy', scale=1, alpha=0.4)
        plt.quiver(-k_gate_out[0], -k_gate_out[1], k_gate_out[0], k_gate_out[1], 
                   color='red', 
                    angles='xy', scale_units='xy', scale=1,)
        
        # plotting fluo vector
        plt.quiver(*origin, k_fluo[0], k_fluo[1],  color='blue', label='k_fluo',
                   angles='xy', scale_units='xy', scale=1, alpha=0.4)
        plt.quiver(-k_fluo_out[0], -k_fluo_out[1], k_fluo_out[0], k_fluo_out[1], 
                   color='blue',
                    angles='xy', scale_units='xy', scale=1,)
        
        # plotting sum vector
        plt.quiver(*origin, k_somme[0], k_somme[1],  color='purple', label='k_s',
                   angles='xy', scale_units='xy', scale=1, alpha=0.4)
        
        # plotting optic axis
        plt.quiver(*origin, r_c[0]*100, r_c[1]*100,  color='yellow', label='optic axis',
                   angles='xy', scale_units='xy', scale=1, alpha=0.8, linewidth=0.2)
        
        plt.plot(np.nan, np.nan, color='grey', label='air-BBO interface')
        plt.plot(np.nan, np.nan, color='grey',ls='--', label='BBO surface normal')
        
        xlim = max(abs(k_somme[0]), abs(k_gate[0]), abs(k_fluo[0]))+0.5
        ylim = max(abs(k_somme[1]),abs(k_gate_out[1]), abs(k_fluo_out[1]))+0.5
        
        xylim = max(xlim, ylim)
        
        plt.xlim(-xylim, xylim)
        plt.ylim(-xylim, xylim)
        plt.vlines(0, -xylim, xylim, color='grey')
        plt.hlines(0, -xylim/2, xylim/2, color='grey', linestyle='--')
        plt.figtext(0.34, 0.15, "air", fontsize='20')
        plt.figtext(0.6, 0.15, "BBO", fontsize='20')
        plt.legend(loc='upper left')

        return theta_fluo_out_opt*180/np.pi, fig_delta_k, fig_k
