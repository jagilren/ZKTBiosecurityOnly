# This will import all the widgets
# and modules which are available in
# tkinter and ttk module
from sys import exit
import requests
import csv
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.ttk import *
import tkinter.font as font
import tkinter.messagebox
from tkinter.constants import DISABLED, NORMAL
import time, datetime
from threading import Thread
import os
from subprocess import *
import subprocess
import ctypes

class DelayRouteOpenGaraje(Toplevel):
    pass
    '''def __init__(self):
        super().__init__(master=master)
        self.btnOK = Button(self, text='OK ', command=self.destroy())  # height=2, width=3
        self.btnOK.pack()
        self.lblAViso = Label(self, text='GARAJE EN RECORRIDO DE APERTURA \n ESPERA UNOS SEGUNDOS MÁS')
        self.lblAViso.pack()
        global boolGarageInRouteOpen
        self.threadDelayRouteOpen = Thread(target=self.DelayRouteOpen(), name='threadDelayRouteOpen')
        '''
#This Class Show report of all Open Garajes, according to sensor state
class WindowOpenendDoors(Toplevel):
    def __init__(self, master= None, myheaders= None, Dict_Door_ID= None, **my_dict):
        super().__init__(master=master)
        self.title('GARAJES REPORTADOS COMO ABIERTOS')
        self.geometry("900x600")
        self.lift()
        self.grab_set()
        self.OpenDoorsListBox = Listbox(self, width=int(self.winfo_reqwidth()/2), height=int(self.winfo_reqheight()/2))  # reqwidth method return value in pixels
        underline_font = font.Font(family='Aerial 13',underline=True, size=12, weight='bold',slant='italic')
        custom_font = font.Font(family='Tahoma', underline=False, size=14, weight='bold')
        self.OpenDoorsListBox.grid(column=0, row=1, rowspan=2, columnspan=1, sticky=W)
        self.OpenDoorsListBox.configure(background="white",font=(custom_font))
        self.putListBox()
        print(f'Ancho de TopLevel={self.winfo_reqwidth()}, Alto de TopLevel={self.winfo_reqheight()}')
        HayAbiertas= False
        self.OpenDoorsListBox.insert(0,'Las siguientes habitaciones se reportan como abiertas. Revise el sensor para corregir')
        self.OpenDoorsListBox.itemconfigure(0,{'bg':"khaki3",'fg':"white"})

        #self.OpenDoorsListBox.itemconfigure(0,background="white", font=underline_font)
        for element in my_dict.keys():
            print(f'El elemento actual es {element}')
            if Dict_Door_Type[element] == 'SEDAN':

                if API_Door_Status(Dict_Door_ID[element]) == '2': #2 SIGNIFICA ABIERTA
                    HayAbiertas= True

                    self.OpenDoorsListBox.insert(1,'')
                    self.OpenDoorsListBox.itemconfigure(1,{'bg':'white', 'fg':'white'})
                    self.OpenDoorsListBox.insert(2, element)
                    self.OpenDoorsListBox.itemconfigure(2, {'bg':'skyblue4', 'fg':'white'})
        if HayAbiertas==False:
            self.OpenDoorsListBox.insert(2, '')
            self.OpenDoorsListBox.insert(2, 'Ninguna puerta está abierta')



    def putListBox(self):
        pass


class NewWindow(Toplevel):
    def __init__(self, master=None, boton=None, hab_ENTRY=None, IDDoor=None, IDAuxOut=None, DoorType=None, my_headers=None):
        global boolGarageInRouteOpen
        super().__init__(master=master)
        self.title(boton.cget('text'))
        self.my_headers = my_headers
        self.geometry("400x200")
        self.RedundantOperation = False
        self.boton = boton
        self.hab_ENTRY=hab_ENTRY
        self.labelHabitacion = boton.cget('text')
        self.IDDoor = IDDoor
        self.IDAuxOut = IDAuxOut
        self.DoorType = DoorType
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.DoorStatus = '1'
        self.intervalosecs=int(Dict_Ini_Params['SecsIntervalForLockInNormallyOpen'])
        self.thread_AssignMagneticas = Thread(target=self.AuxOutClose_LockNObyIntervalByMagneticas, name='threadAssignMagneticas')
        self.thread_AssignElectricas = Thread(target=self.DoorOpen_ButtonOpen_ButtonClose_Electricas, name='threadAssignElectricas')
        self.threadCloseGarage = Thread(target=self.GarageStatus_GarageClose, name='threadCloseGarage')
        self.threadUnBlockMagneticas = Thread(target=self.AuxOutNormalOpen_LockNObyInterval_AuxOutNormalClose_Magneticas, name='threadUnBlockMagneticas')
        self.threadUnBlockElectricas = Thread(target=self.AuxOutOpen_AuxOutClose, name='threadUnBlockElectricas')
        self.threadBlockElectricas = Thread(target=self.AuxOutNormalClose, name='threadBlockElectricas')
        self.threadDelayRouteOpen = Thread(target=DelayRouteOpenOrClose, args=(self.boton,), name='threadDelayRouteOpen')
        self.threadBlinkColorListBox = Thread(target=self.blinking_ListBoxProcess,args=("orchid1","SeaGreen1","snow",20),name='threadBlinkColorListBox')
        print(f'Estado de Recorrido de la puerta {boton} = {not(boolGarageInRouteOpen)}')
        #Cambia el Texto de la EntryBox de Habitación para consulta de estado Rápido luego de salir de la Ventana
        self.hab_ENTRY.delete(0, END)
        self.hab_ENTRY.insert(0,self.boton.cget('text')[3:5])



        def close_win(e):
            self.destroy()

        # Gets the requested values of the height and width.
        windowWidth = self.winfo_reqwidth() * 2
        windowHeight = self.winfo_reqheight() * 2
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.winfo_screenwidth() / 2 - windowWidth / 2)
        positionDown = int(self.winfo_screenheight() / 2 + windowHeight / 10)
        self.geometry("+{}+{}".format(positionRight, positionDown))
        self.lift()
        self.focus_force()
        self.grab_set()
        #self.focus_set()


        print("Width", windowWidth, "Height", windowHeight)
        #Drawing  Canvas  and Buttons in NewWindow: Window
        if DoorType == 'SEDAN': #Para SEDAN aplica un thread diferente porque son motores electricos NO
            self.btnAbrir = Button(self, text='Abrir', command=self.AssignProcessElectricas)  # height=2, width=3
            self.btnAbrir.grid(row=2, column=0, sticky=NS, pady=20)  # ,
        elif DoorType == 'MOTO': #Para MOTO  aplica un thread diferente porque son Cerraduras Magneticas NC
            self.btnAbrir = Button(self, text='Abrir', command=self.AssignProcessMagneticas)  # height=2, width=3
            self.btnAbrir.grid(row=2, column=0, sticky=NS, pady=20)  # ,
        else:
            pass
        if DoorType == 'SEDAN':
            self.btnCerrar = Button(self, text='Cerrar', command=self.CloseGarageProcess,
                                    state='ENABLED')  # height=2, width=3
            self.btnCerrar.grid(row=2, column=1, sticky=NS, pady=20)

        self.btnLock = Button(self, text='Bloquear ', command=self.BlockProcess)  # height=2, width=3
        self.btnLock.grid(row=6, column=0, sticky=NS, pady=20)  # ,

        self.btnUnLock = Button(self, text='Des-Bloquear', command=self.UnBlockProcess)  # height=2, width=3
        self.btnUnLock.grid(row=6, column=1, sticky=NS, pady=20)  # ,

        labelStatusDoor = Label(self, textvariable="Puerta Abierta", relief=RAISED)
        labelStatusDoor.grid(row=7, column=0, pady=20, columnspan=2, rowspan=2, sticky=NSEW)
        labelStatusDoor.config(text="Open_Door")
        print(self.btnUnLock.grid_info())
        self.grab_set()
        self.bind('<Escape>', lambda e: close_win(e))

    def UnBlockProcess(self):
        #El proceso de desbloqueo es diferente para Puertas con Motor electrico que para Puertas con cerradura magnética
        if Dict_Door_Type[self.boton.cget('text')] == 'SEDAN':
            self.threadUnBlockElectricas.daemon = True
            self.threadUnBlockElectricas.start()
        elif Dict_Door_Type[self.boton.cget('text')] == 'MOTO':
            self.threadUnBlockMagneticas.daemon = True
            self.threadUnBlockMagneticas.start()
        else:
            pass
        self.Write_logListBox('--- DES-BLOQUEADA ---')
        self.foreground_logListBox("goldenrod1")
        threadLabelWaiting = MTThread(name='Labeling', target=LabelWaiting)
        threadLabelWaiting.start()
        self.destroy()
    def AssignProcessElectricas(self):
        self.thread_AssignElectricas.daemon = True
        self.thread_AssignElectricas.start()
        time.sleep(3) # Para asegurarse que la ventana emergente PACIENCIA si se active
        self.destroy()
        time.sleep(2) #Para que no se den Click super rápido en otro botón

    def AssignProcessMagneticas(self):
        self.thread_AssignMagneticas.daemon = True
        self.thread_AssignMagneticas.start()
        time.sleep(1) # Para asegurarse que la ventana emergente PACIENCIA si se active
        self.destroy()
        time.sleep(2) #Para que no se den Click super rápido en otro botón

    def CloseGarageProcess(self):
        self.threadCloseGarage.daemon = True
        self.threadCloseGarage.start()
        time.sleep(3)  # Para asegurarse que la ventana emergente PACIENCIA si se active
        self.destroy()
        # classthreadCloseDoor = MTThread(name='Labeling', target=self.VerifyStatusDoor_CloseDoor)
        # classthreadCloseDoor
        # classthreadCloseDoor.start()

    def BlockProcess(self):
        #El proceso de desbloqueo es diferente para Puertas con Motor electrico que para Puertas con cerradura magnética
        if Dict_Door_Type[self.boton.cget('text')] == 'SEDAN' or 'MOTO':
            self.threadBlockElectricas.daemon = True
            self.threadBlockElectricas.start()
        self.Write_logListBox('--- BLOQUEADA ---')
        self.foreground_logListBox("SeaGreen1")
        threadLabelWaiting = MTThread(name='Labeling', target=LabelWaiting)
        threadLabelWaiting.start()
        self.destroy()

    def API_door(self, intervalosecs):
        endpoint_Door = f'http://' + Dict_Ini_Params[
            'IPV4AddressServer'] + '/api/door/remoteOpenById?' + 'doorId=' + self.IDDoor + \
                        f'&interval={intervalosecs}' + APIToken
        # print(frame_buttons'url_abrir_cerrar_puerta {endpoint_Door}')
        response = requests.post(endpoint_Door, headers=self.my_headers)
        print(f'Respuesta JSON API_RemoteOpenbyID over Lock Interface in InBioPro: {response.json()}')

    def API_Close_door(self):
        endpoint_Door = 'http://' + Dict_Ini_Params[
            'IPV4AddressServer'] + '/api/door/remoteCloseById?doorId=' + self.IDDoor \
                        + APIToken
        # print(frame_buttons'url_abrir_cerrar_puerta {endpoint_Door}')
        response = requests.post(endpoint_Door, headers=self.my_headers)
        print(f'Respuesta JSON API_RemoteCloseByID: {response.json()}, {self.labelHabitacion}')

    def VerifyStatusDoor_CloseDoor(self):
        if API_Door_Status(self.IDDoor) == '2':  # Verificamos que está abierta
            print(f'Cerrando Garaje Sedan')
            self.API_door()  # Enviamos Pulso de Abrir Garaje para que esta se Cierre, pues la API Door/remote_Close_ByID no cierra la puerta
        else:
            print("Garaje Ya Esta Cerrada.  No se Ejecuta la acción")

    def AuxOutOpen_AuxOutClose(self):
        ResponseButtonOpen = self.API_AuxOutRemoteNormalOpen()
        if ResponseButtonOpen == 'success':
            labelQueryResult.config(text=self.boton.cget('text') + " Desbloqueda", background='red')

        for element1 in range(int(Dict_Ini_Params['TimeOutButtonNormalOpen'])):
            time.sleep(1)
            #print(frame_buttons'Threading Time = {element1} Waiting for AuxClose Execute threadUnBlockProcess')
        ResponseButtonClose = self.API_AuxOutNormalClose()
        # threadButtonClose = MTThread(name='ClosingButton', target=self.API_AuxOutNormalClose)
        # threadButtonClose.start()
        self.destroy()

    def Write_logListBox(self, texto):
        ct = datetime.datetime.now()
        logListBox.insert(0, self.boton.cget('text') + texto + ' ' + str(ct).split('.')[0])

    def foreground_logListBox(self, colorista):
        ct = datetime.datetime.now()
        logListBox.itemconfigure(0, background="skyblue4", foreground=colorista)
    def blinking_ListBoxProcess(self, blinkColor,colorista,backColor, blinkTime):
        color=colorista
        for segundos in range(0, blinkTime):
            color = blinkColor if color == colorista else colorista
            time.sleep(0.5)
            logListBox.itemconfigure(0, background="skyblue4", foreground=color)
    def blinking_ListBoxThread(self):
        self.threadBlinkColorListBox.daemon=True
        self.threadBlinkColorListBox.start()

    def GarageStatus_GarageClose(self):
        if API_Door_Status(self.IDDoor) == '2': #2 SIGNIFICA ABIERTA
            print(f'Garaje Abierto....Cerrando Garaje')
            self.threadDelayRouteOpen.daemon = True
            self.threadDelayRouteOpen.start()

            try:
                self.API_door(intervalosecs=1)  # Cierra la puerta  para SEDAN si está abierta. Con comando de Abrir por caprichos de ZKT
                self.Write_logListBox('--- CERRANDO GARAJE ---')
                self.foreground_logListBox("SeaGreen1")
            except:
                print('Error en API de Cerrado de Garaje')
        else:
            print("GARAJE Ya está Cerrada.  No se ejecuta la acción")
            self.Write_logListBox('--- GARAJE DE CARRO YA ESTÁ CERRADO ---')
            self.foreground_logListBox("orchid1")

    def AuxOutNormalOpen_LockNObyInterval_AuxOutNormalClose_Magneticas(self): # Para Cerraduras Magneticas del Motel Only
        # Algoritmo para Des-Bloquear Puertas de MOTO Motel ONLY
        import logging
        # Para DEBUG
        for i in range(5):
            logging.debug('entry in function AuxOutNormalOpen_LockNObyInterval_AuxOutNormalClose_Magneticas')
            print(f'entry in function AuxOutNormalOpen_LockNObyInterval_AuxOutNormalClose_Magneticas')

        # No Vamos a Revisar estado de la puerta, porque esta funcion Aplica sólo para Magéticas MOTO
        # Activamos la continuidad entre los pines NO y Common de la bornera  AuxOut in InBioPro
        self.API_AuxOutRemoteNormalOpen() #Mejor  este porque No tiene Intervalo

        self.Write_logListBox('--- DESBLOQUEADA PUERTA MOTO ---')
        labelQueryResult.config(text="Esperando...", background='black')
        self.foreground_logListBox("goldenrod1")

        # Traemos valor del Intervalo de segundos en Lock que dará continuidad a pines NO and Common
        intervalosecs=int(Dict_Ini_Params['SecsIntervalForLockInNormallyOpen'])

        # Enviamos Pulso Temporizado a interfaz Lock Intervalosecs  de NO y Common, aislando pines NC y Common
        # Pasa de NC a NO, para desenergizar la línea del Neutro  que va al Magneto, Intervalosecs >=240 por Revisar
        self.API_door(intervalosecs)

        # Esperamos Intervalosecs para volver a actuar sobre Interface Lock y Nuevamente continuidad entre NO y Common
        for segundos in range(intervalosecs):
            time.sleep(1)
            print(f'Activado Interruptor lado Cliente por {intervalosecs*2-segundos} segundos')
        # Repite Comando. Pasa de NC a NO, para desenergizar la línea del Neutro  que va al Magneto, Intervalosecs >=240 por Revisar
        self.API_door(intervalosecs)
        for segundos in range(intervalosecs):
            time.sleep(1)
            print(f'Activado Interruptor lado Cliente por {intervalosecs*1-segundos} segundos')

        '''Pasados Time of  activesecs * 2 Activamos la continuidad entre los pines NC y Common de la bornera  AuxOut
            Lo cual permitira que la puerta se pueda abrir directamente desde el Physical Button o el Comando Abrir del aplicativo
            pero No del Interruptor del Clado del Cliente'''
        self.API_AuxOutNormalClose() #No Tiene Intervalo

        '''        if not(self.RedundantOperation):
                    self.Write_logListBox(f'--- {self.boton.cget("text")} DESBLOQUEADA ---')
                    self.foreground_logListBox("goldenrod1")
                time.sleep(2)
        '''
        self.Write_logListBox(f'--- {self.boton.cget("text")} BLOQUEADA ---')
        self.foreground_logListBox("SeaGreen1")
    def AuxOutClose_LockNObyIntervalByMagneticas(self):
        # Algoritmo para Abrir Puertas de MOTO Motel ONLY
        # Sólo aplica para Puerta MOTO Magnetica en ONLY, ya sea desde la Aplicación en Python como del Botón Plan B emergerncia
        for i in range(5):
            print(f'entry in function AuxOutNormalOpen_LockNObyInterval_AuxOutNormalClose_Magneticas')

        '''Para garantizar Aislamiento del neutro en el  Interruptor del lado del cliente debemos asegurarnos que AuxOut
         este in NC y common. Esto lo visualizamos si el LED  del LOW LEVEL TRIGGER RELAY MODULE esta apagado'''

        # Abre de una por gravedad si es MOTO o peaton sin importar estado de la puerta.
        self.API_door(intervalosecs=10)
        print(f'Wait...02 seconds for AuxNormalOpen Execution')
        time.sleep(2)
        '''Activamos la continuidad entre los pines NC y Common de la bornera  AuxOut
            Lo cual permitira que la puerta se pueda abrir directamente desde el Physical Button o el Comando Abrir'''
        self.API_AuxOutNormalClose() #No Tiene Intervalo
        self.Write_logListBox('--- ABRIÓ PUERTA MOTO ---')
        self.foreground_logListBox("goldenrod1")
        labelQueryResult.config(text="Esperando...", background='black')
        #Descomentar siguiente línea si se desea Activar el Interruptor del lado del cliente para que pueda salir de la habitación MOTO durante los 4 minutos siguietnes a su entrada
        #self.API_AuxOutRemoteNormalOpen()
        #Ciclo For para demorar el tiempo de Desactivación del Botón de Bloqueo
        for element in range(int(Dict_Ini_Params['TimeOutButtonNormalOpen'])):
            time.sleep(1)
            print(f'Resting Time Isolate Interruptor Client Side  = {int(Dict_Ini_Params["TimeOutButtonNormalOpen"])-element}  \n')
        self.API_AuxOutNormalClose()
        self.Write_logListBox('--- BLOQUEADA ---')
        self.foreground_logListBox("SeaGreen1")
    def DoorOpen_ButtonOpen_ButtonClose_Electricas(self):
        # Algoritmo para Abrir Garajes de Vehículo SEDAN. Sólo Aplica para SEDAN en Motel Only
        # Vamos a Revisar si el garaje está Abierto
        if API_Door_Status(self.IDDoor) == '1':  #1 SIGNIFICA CERRADA
            print(f'GARAJE en recorrido de Apertura')
            try:
                self.threadDelayRouteOpen.daemon = True
                self.threadDelayRouteOpen.start()
                self.API_door(intervalosecs=1)  # Abre si está cerrada para SEDAN
            except:
                print('Error en API_Door, Revise API desde la Plataforma ZKT')

        else:
            print("GARAJE Ya está Abierta.  No se ejecuta la acción")
            self.RedundantOperation = True
            self.Write_logListBox('--- GARAJE YA ESTÁ ABIERTO --- MIRE LAS CÁMARAS O USE EL BOTON "CERRAR"---')
            self.foreground_logListBox("orchid1")
            self.blinking_ListBoxThread()
        time.sleep(2)
        print(f'Wait...02 seconds for AuxNormalOpen Execution')
        self.API_AuxOutRemoteNormalOpen()
        if not(self.RedundantOperation):
            self.Write_logListBox(f'--- {self.boton.cget("text")} DESBLOQUEADA ---')
            self.foreground_logListBox("goldenrod1")
        time.sleep(2)
        if Dict_Door_Type[self.boton.cget('text')] == 'SEDAN':
            if API_Door_Status(self.IDDoor) == '2': #2 Siginifica Garaje o Puerta Abierta
                if not(self.RedundantOperation):
                    self.Write_logListBox(f'--- GARAJE {self.boton.cget("text")}  ESTÁ ABIERTO  ---')
                    self.foreground_logListBox("goldenrod1")
            else:  # Si no cambió el estado del Sensor
                self.Write_logListBox('--- GARAJE PERMANECIO CERRADA ---')
                self.foreground_logListBox("pink")
        else:  # Si es Moto o Peaton
            self.Write_logListBox('--- ABRIÓ GARAJE ---')
            self.foreground_logListBox("goldenrod1")

        labelQueryResult.config(text="Esperando...", background='black')
        #Ciclo For para demorar el tiempo de Desactivación del Botón de Bloqueo
        for element in range(int(Dict_Ini_Params['TimeOutButtonNormalOpen'])):
            time.sleep(1)
            print(f'Resting Time for  Threading AuxButtoonClose  = {int(Dict_Ini_Params["TimeOutButtonNormalOpen"])-element}  "AuxButtonClose Next to Execute threadAssignProcess" \n')
        self.API_AuxOutNormalClose()
        self.Write_logListBox('--- BLOQUEADA ---')
        self.foreground_logListBox("SeaGreen1")

    def AuxOutNormalClose(self):
        ResponseButtonClose = self.API_AuxOutNormalClose()
        if ResponseButtonClose == 'success':
            labelQueryResult.config(text=self.boton.cget('text') + " Bloqueada", background='green')
        threadLabelWaiting = MTThread(name='Labeling', target=LabelWaiting)
        threadLabelWaiting.start()
        self.destroy()

    def API_AuxOutNormalClose(self):
        endpoint_Aux = 'http://' + Dict_Ini_Params[
            'IPV4AddressServer'] + '/api/auxOut/remoteCloseByAuxOutById?id=' + self.IDAuxOut + \
                       APIToken
        response = requests.post(endpoint_Aux, headers=self.my_headers)
        print(f'json response CloseAuxOut:   {response.json()}:,  {self.labelHabitacion} ')
        return response.json()['message']


    def API_AuxOutRemoteNormalOpen(self):
        endpoint_Aux = 'http://' + Dict_Ini_Params[
            'IPV4AddressServer'] + '/api/auxOut/remoteNormalOpenByAuxOutById?id=' + self.IDAuxOut + \
                       APIToken
        response = requests.post(endpoint_Aux, headers=self.my_headers)
        print(f'json response NormalOpenAuxOut:   {response.json()}')
        # time.sleep(5)
        return response.json()['message']

    def btn_Abrir(self):
        self.API_door(intervalsecs = 1)
        self.btnAbrir['state'] = DISABLED
        self.btnAbrir.config(cursor="watch")
        self.btnLock.focus()
        self.btnLock.grab_set()
        time.sleep(5)
        self.destroy()
        print(f'HEADERS:   {self.my_headers}')
        # print(frame_buttons'json response abrir:{response.json()}')

    def API_print(self, response):
        print(f'{response} Tipo de Respuesta {type(response)}')
        print(f'Status Code: {response.status_code}')
        print(f"Headers Content Type: {response.headers['content-type']}")
        print(f'Yeison Final::{response.json()}')

def DelayRouteOpenOrClose(btn):
    boolGarageInRouteOpen = True
    btn.bind("<Button>",
             lambda e: messagebox.showinfo("Paciencia","Garaje en recorrido 'PACIENCIA'"))
    print (f'Cambió Bind para <Button> {btn.cget("text")}')
    print (f'Thead Delay Route Open Garage Iniciado durante {int(Dict_Ini_Params["DelayRouteOpenGaraje_Secs"])}')
    time.sleep(int(Dict_Ini_Params["DelayRouteOpenGaraje_Secs"])) # Demora de la Apertura Total del Garage
    boolGarageInRouteOpen = False
    btn.bind("<Button>",
             lambda e, boton=btn, IDDoor=Dict_Door_ID[btn.cget('text')], IDAuxOut=Dict_AuxOut_ID[btn.cget('text')],
                    DoorType=Dict_Door_Type[btn.cget('text')]: NewWindow(master, boton, hab_ENTRY, IDDoor, IDAuxOut, DoorType,
                                                                         my_headers))
def validate_entry(text, new_text):
    try:
        if not (new_text):
            return TRUE
        if len(new_text) > 2:
            return FALSE
        if int(new_text) > 78:
            return FALSE
        return text.isdecimal()
    except:
        hab_ENTRY.config(text="")
        return FALSE

    finally:
        print(f'Entraste al finally')

def LabelWaiting():
    for tiempo in range(5):
        time.sleep(1)
        print("Waiting for Change Text Label")
    labelQueryResult.config(text="Esperando...", background='black')

class MTThread(Thread):
    def __init__(self, name=None, target=None):
        self.mt_name = name
        self.mt_target = target
        Thread.__init__(self, name=name, target=target)
        print("name en def __init__", name)

    def start(self):
        super().start()
        Thread.__init__(self, name=self.mt_name, target=self.mt_target)

    def run(self):
        super().run()
        Thread.__init__(self, name=self.mt_name, target=self.mt_target)


threadLabelWaiting = MTThread(name='Labeling', target=LabelWaiting)
def submitQuery(labelQueryResult, BioSecurityStatus):
    if not (hab_var.get()):
        print('No se encontró valor en Rigth Button Operation over Button Habitaciones')
        return
    if BioSecurityStatus == False:
        infoconexion = messagebox.showinfo("Error de Conexión", "Servidor de Puertas Desconectado \n Verifique RED")
        return
    prefixHab = 'HAB0' + hab_var.get() if len(hab_var.get()) == 1 else 'HAB' + hab_var.get()
    IDAuxOut = Dict_AuxOut_ID[prefixHab]
    IDDoor = Dict_Door_ID[prefixHab]
    typeDoor = Dict_Door_Type[prefixHab]
    Dict_DoorType_Sinonyms = {'MOTO': 'PUERTA', 'SEDAN': 'GARAJE', 'HIBRIDO':'PUERTA'}
    messagePrefix = Dict_DoorType_Sinonyms[typeDoor]

    if (API_Door_Status(IDDoor) == '1'):
        labelQueryResult.config(text=prefixHab + " " + messagePrefix + " está Cerrada(o)", background="green")
    elif (API_Door_Status(IDDoor) == '2'):
        labelQueryResult.config(text=prefixHab + " " + messagePrefix + " está Abierta(o)", background="red")
    elif (API_Door_Status(IDDoor) not in ['1', '2']):
        labelQueryResult.config(text=prefixHab + " Estado del Sensor Desconocido", background="purple")
    threadLabelWaiting.start()

def API_Door_Status(IDDoor):
    print(f'Api Status Ejecutado, {IDDoor}')
    endpoint_Door = 'http://' + Dict_Ini_Params['IPV4AddressServer'] + '/api/door/doorStateById?' + 'doorId=' + IDDoor + \
                    APIToken
    try:
        response = requests.get(endpoint_Door, headers=my_headers)
        print(f'json response:   {response.json()}')
        DoorStatus = response.json()['data'][0]['sensor']
        print(f'Estado Sensor Puerta= {DoorStatus}')
        return DoorStatus
    except:
        return "Puerta o Garaje Inexistente"

# Specify path
def VerificaTXT(filetxt):
    isExist = os.path.exists(filetxt)
    return isExist

def CheckAllFilesExist(queryexist=True):
    list_configFiles = ['./AuxOut.txt', './doors.txt', './RAM4GB.png']
    for ConfigFiles in list_configFiles:
        queryexist = queryexist * VerificaTXT(ConfigFiles)
    if (queryexist):
        pass
    else:
        master.destroy()


def leer_csv(filename):
    fields = []
    rows = {}
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        fields = next(csvreader)
        for row in csvreader:
            # door_ids=row.split(",")
            rows[row[0]] = row[1]
    return rows

boolGarageInRouteOpen = False
intCountWarningConnectivy=0
Dict_Door_ID = leer_csv('doors.txt')
Dict_AuxOut_ID = leer_csv('AuxOut.txt')
Dict_Door_Type = leer_csv('doors_type.txt')
Dict_Ini_Params = leer_csv('zkt.ini')

global my_headers, APIToken
BasicAuth=Dict_Ini_Params['BasicAuth']
APIToken=Dict_Ini_Params['APIToken']
my_headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
              'Authorization': BasicAuth}


BioSecurityStatus = False
master = Tk()
num_displays = ctypes.windll.user32.GetSystemMetrics(80)
#num_displays=0
widthMaxWindow = ctypes.windll.user32.GetSystemMetrics(16)
heightMaxWindow = ctypes.windll.user32.GetSystemMetrics(17)
screen_width = int(widthMaxWindow/num_displays)  if num_displays>0 else 1020
screen_height = int(heightMaxWindow/num_displays) if num_displays>0 else 768
btnRelativeRowPos=0
btnRelativeColPos=0
master.geometry(f'{screen_width}x{screen_height}')
      # "1140x900+0+0") se pone x x in lowercase para significar pixeles.  Y los ceros para desplazar 0 Unidades desde el left top corner

frame_buttons = Frame(master)
f_foot = Frame(master)

style = Style()
style.configure('TButton', font=('Tahoma', 10), borderwidth='4',background='black',foreground='black',highlightthickness='20')
#style_Garaje = {'fg': 'black', 'bg': 'SlateBlue2', 'activebackground':'SlateBlue2', 'activeforeground': 'SlateBlue2'}
#style.configure('TButton', **style_Garaje)
style.map('TButton', foreground=[('active','!disabled', ('magenta'))], background=[('active', 'black')])
styleButtonGaraje =Style()
styleButtonGaraje.configure('small.TButton', font=('Tahoma', 8, 'bold'), background="red",foreground='orange red')
styleButtonGaraje.configure('sedan.TButton', font=('Tahoma', 10), background="black",foreground='blue')
styleButtonGaraje.configure('moto.TButton', font=('Tahoma', 10), background="red",foreground='orange red')


style.configure('TFrame', bordercolor='pink', background='#68839B', borderwidth=1)

labelTitleQuery = Label(f_foot, text="Consulta Estado", font=('calibre', 11, 'bold'), padding=1, foreground="white",
                        background='black')
labelTitleQuery.grid(row=62, column=0, sticky=W, pady=2)

hab_var = StringVar()

frame_buttons = Frame(master, style="Custom.TFrame")
frame_buttons.grid(row=0, column=0)

f_foot = Frame(master)
#Ponerlo en Column 0 Garantiza que se posiciona en la Izquierda
f_foot.grid(row=70, column=0, columnspan=20, sticky=NS) #

f_query = Frame(f_foot)
f_query.grid(columns=1, row=0,columnspan=5,sticky=W) #,

f_openedDoors = Frame(f_foot)
f_openedDoors.grid(columns=7, row=0) #,

hab_ENTRY = Entry(f_query, textvariable=hab_var, font=('calibre', 11, 'bold'), width=5, validate="key",
                  validatecommand=(master.register(validate_entry), "%S", "%P"))
hab_ENTRY.grid(row=0, column=0, sticky=W) #
btnQuery = Button(f_query, text="CONSULTAR", padding=1, command=NONE, width=15)
btnQuery.grid(row=1, column=0, pady=2, sticky=W) #
btnQuery.bind("<Button>",lambda e, IDDoor=hab_var.get(), BioSecurityStatus=True: submitQuery(labelQueryResult, BioSecurityStatus))
btnQuery.bind('<Return>',lambda e, IDDoor=hab_var.get(), IDAuxOut=hab_var.get(): submitQuery(labelQueryResult, BioSecurityStatus))
btnQOpenedDoors =Button(f_openedDoors, text="PUERTAS ABIERTAS", padding=1, command=NONE, width=18,style="small.TButton")
btnQOpenedDoors.grid(row=2, column=6, pady=2)
my_dict={'a': 'A', 'b': 'B'}
btnQOpenedDoors.bind("<Button>", lambda e: WindowOpenendDoors(master, my_headers, Dict_Door_ID, **btn_dict))
myFont = font.Font(family='Helvetica')

global logListBox
logListBox = Listbox(f_foot, width=120, height=int(16))  #width is noumbre of characteres !pixels; height is lines not pixels
logListBox.configure(background="skyblue4", foreground="white", font=('Aerial 13'))
logListBox.grid(column=0,row=5,rowspan=2, columnspan=20,sticky=W)



#btnQOpenedDoors['font']=myFont



labelQueryResult = Label(f_query, text="Esperando...:", font=('calibre', 11, 'bold'), foreground='white',
                         background='black')
labelQueryResult.grid(row=3, column=0, pady=2, sticky=W)

radek_line = 2  # Construye Matriz de Botones Set  ROW  of  matríz of Buttons
bunka_column = 0
last_btn_pos_y1=0  #Establece un valor semilla para determinar la posición de la última fila de los btn_dict
btn_dict={}
#Ciclo para Generar Array of Buttons of Habitaciones
for element in Dict_Door_ID.keys():
    state = DISABLED

    if len(Dict_Door_ID[element]) == 32:
        state = NORMAL
        if (Dict_Door_Type[element]=='SEDAN'):
            btn_dict[element] = Button(frame_buttons, text=element, padding=10, state=state, style="TButton")

        elif (Dict_Door_Type[element]=='MOTO' or Dict_Door_Type[element]=='HIBRIDO'):
            btn_dict[element] = Button(frame_buttons, text=element, padding=10, state=state, style="moto.TButton")

        btn_dict[element].bind("<Button>",
                      lambda e, boton=btn_dict[element], IDDoor=Dict_Door_ID[btn_dict[element].cget('text')], IDAuxOut=Dict_AuxOut_ID[btn_dict[element].cget('text')],
                             DoorType=Dict_Door_Type[btn_dict[element].cget('text')]: NewWindow(master, boton, hab_ENTRY, IDDoor, IDAuxOut,
                                                                                       DoorType,
                                                                                       my_headers))
        btn_dict[element].bind("<Button-3>",
                               lambda e, boton_label=btn_dict[element].cget("text")[-2:]: RigthClickOverButtonHabitacion(
                                   boton_label))
        #btn_dict[element].bind("<Button-3>",lambda e, IDDoor=hab_var.get(), BioSecurityStatus=True: submitQuery(labelQueryResult, BioSecurityStatus))


    else:
        btn_dict[element] = Button(frame_buttons, text='...', padding=10, state=state)

    last_btn_pos_y1 = btn_dict[element].winfo_y() if btn_dict[element].winfo_rooty() >= last_btn_pos_y1 else last_btn_pos_y1

    frame_buttons.rowconfigure(radek_line, minsize=(screen_height/2/8)) #Se divide por 8 porque son 8 filas de Habitaciones y Se divide por 2 para dejar espacio al log de notificaciones
    frame_buttons.columnconfigure(bunka_column, minsize=(screen_width-100)/10) #Se Divide por 10 porque hay 10 columnas de habitaciones por cada fila
    btn_dict[element].grid(row=radek_line, column=bunka_column, padx=2, pady=2, sticky=NSEW)
    #master.update()


    bunka_column += 1
    if bunka_column == 5:  # changed this variable to make it easier to test code.
        bunka_column = 0
        radek_line += 1
#Valores finales para la Ventana Principal del mainloop

master.geometry(f'{screen_width+100}x{screen_height}')
master.title('Apertura Puertas y Garajes Motel Only')
master.config(bg='#68839B')
p1 = PhotoImage(file='RAM4GB.png')
p1 = master.iconphoto(True, p1)


def RigthClickOverButtonHabitacion(boton_label):
    print(f'Click derecho sobre habitación: {boton_label}')
    hab_var.set(boton_label)
    submitQuery(labelQueryResult,BioSecurityStatus)
def checkPing():
    global BioSecurityStatus
    my_address = Dict_Ini_Params['IPV4AddressServer'].split(':')[0]
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    output = Popen(["ping", "-n", "2", my_address], startupinfo=startupinfo, stdout=PIPE).communicate()[0]
    if output.find(b'time') > 0 or output.find(b'tiempo') > 0:
        BioSecurityStatus = True
    elif output.find(b'time') == -1 and output.find(b'tiempo')  == -1:
        BioSecurityStatus = False
    print(f'BioSecurityStatus={BioSecurityStatus}')
    if (BioSecurityStatus):
        return 1 #output.find(b'time')   If return -1, then Host inaccessible
    else:
        return -1

def WarningConectivity():
    while True:
        global intCountWarningConnectivy
        if logListBox.size() > 16:
            logListBox.delete(0, END)
        y = checkPing()
        if y == -1:
            print('Servidor de Apertura de Puertas Caido o Fuera de Línea')
            ct = datetime.datetime.now()
            logListBox.configure(background="LightBlue1", foreground="red", font=('Aerial 13'))
            logListBox.insert(0,
                              "Servidor de Apertura de Puertas y Garajes Caido o Fuera de Línea" + ' --- ' + str(ct).split('.')[
                                  0])
            time.sleep(3)
            messagebox.showerror("Error de Conectividad",
                                 "Error de Conexion con el Server BioTime \nReinicie el Computador \nSi el problema Continúa Comuníquese con Soporte Técnico")
            time.sleep(1)
            master.destroy()
            exit()

        elif y >= 0:
            print('Servidor de Aperturas de Puertas y Garajes Online')
            ct = datetime.datetime.now()
            if (intCountWarningConnectivy== 0 or intCountWarningConnectivy> 20):
                logListBox.configure(background="skyblue4", foreground="white", font=('Aerial 13'))
                logListBox.insert(0, "Servidor de Apertura está Conectado   en línea" + ' --- ' + str(ct).split('.')[0])
                intCountWarningConnectivy=0
        intCountWarningConnectivy = +1
        time.sleep(int(Dict_Ini_Params['WatchDog_Server_Secs']))


#  Rutina para Determinar si hay conexion con el Servidor de BioTime
if  (checkPing() == -1):
    messagebox.showerror("Error de Conectividad", "Error de Conexion con el Servidor \nReinicie el Computador \nSi el problema Continúa llame a Soporte Técnico")
    #time.sleep(1)
    #  Alternative para Modal Window
    #  master.after(5000, lambda: _show('Title', 'Prompting after 5 seconds'))
    master.destroy()
    exit()

#WindowOpenDoor=WindowOPenendDoors()

threadCheckConectivity = MTThread(name='Conectivity', target=WarningConectivity)
threadCheckConectivity.daemon = True
threadCheckConectivity.start()

CheckAllFilesExist()
# master.bind('W', lambda event: hab_ENTRY.focus())
master.mainloop()
# Line Footer01
# Line01 from Github
