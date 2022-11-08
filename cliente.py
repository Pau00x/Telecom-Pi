import gi
import threading
import requests
import math

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GLib
from puzzle1 import Rfid    #import de lector de targetes

#si fa falta s'ha de canviar a la direcció on es troba el puzzle de l'LCD
import site
site.addsitedir('/home/pi/Desktop/Puzzle 1 ')   
import puzzle_lcd #import de l'LCD

# Variable global d'usuari
user = {
    "uid" : "", 
    "name" : ""
}

# Variable global de query
query = ""

# Variable global de la sessió
s = requests.Session()


# Classe de la finestra
class Window(Gtk.Window):
    
    # Inicialitza i configura Window
    def __init__(self):
        
        # Es crea un objecte LCD
        self.lcd = puzzle_lcd.my_lcd()
        
        # Fem que l'LCD mostri per pantalla el missatge de login
        self.lcd.clear()
        
        self.lcd.display("Please, login with",2,1)
        self.lcd.display("your university card",3,0)
        
        # Es crea una variable ACK per controlar quan es pot utilitzar el botó
        self.ACK = 0;

        # Inicia la finestra amb un títol i un tamany
        Gtk.Window.__init__(self, title="Uid Scanner")
        self.set_size_request(800, 500)
        
        # Quan es tanca la finestra, s’acaba el programa
        self.connect("destroy", Gtk.main_quit)

        # Es crea un widget tipus Fixed per a mostrar els widgets
        # a la posició desitjada i s'afegeix a la finestra
        self.fixed = Gtk.Fixed()
        self.add(self.fixed)
        
        # Es crea un botó invisible
        self.button = Gtk.Button(label="Logout")
        self.button.connect("clicked", self.on_button_clicked)
        self.button.set_opacity(0)
              
        # Es crea un widget tipus Label per a mostrar text
        self.label = Gtk.Label()
        self.label.set_use_markup(True) 
        self.label.set_label("Please, login with your university card")
        self.label.set_name("login")
        
        self.nameLabel = Gtk.Label()
        self.nameLabel.set_use_markup(True)
        self.nameLabel.set_label("")
        self.nameLabel.set_opacity(0)
        
        
        # Es creen 2 models de llistes i un widget TreeView per a mostrar les taules
        self.listmodel = Gtk.ListStore(str, str, str)
        self.listmodel2 = Gtk.ListStore(str, str, str, str)
        self.result = Gtk.TreeView()
        self.result.set_name("table")

        
        # Es crea un widget tipus Entry per a introduir la query
        self.entry = Gtk.Entry()
        self.entry.set_size_request(780,40)
        self.entry.connect("key_press_event", self.on_key_press_event)
        self.entry.set_opacity(0)
        
        # Es posen els widgets a les posicions desitjades
        self.fixed.put(self.label, 230,235)
        self.fixed.put(self.button, 690, 10)
        self.fixed.put(self.entry, 10, 75)
        self.fixed.put(self.result, 10, 150)
        self.fixed.put(self.nameLabel, 10,10)
        
        # Es mostra la finestra amb el seu contingut
        self.show_all()
        
        # S’inicia un thread on s’executarà read_uid
        thread = threading.Thread(target=self.read_uid)
        thread.daemon = True
        thread.start()

    # Determina que es fa al fer click al botó
    def on_button_clicked(self, widget):
        # El botó només funciona quan s'ha llegit una targeta
        if self.ACK is 1:
            # Reiniciem el valor d'ACK
            self.ACK = 0
            
            # Canviem el text del Label
            GLib.idle_add(self.label.set_name, "login")
            self.lcd.clear()
            self.lcd.display("Please, login with",2,1)
            self.lcd.display("your university card",3,0)
            self.label.set_label('Please, login with your university card')
            self.label.set_opacity(1)
            self.nameLabel.set_opacity(0)
            self.entry.set_opacity(0)
            
            # En cas d'estar visualitzant una taula l'esborrem
            self.listmodel.clear()
            self.listmodel2.clear()
            
            # Fem el botó invisible
            self.button.set_opacity(0)
            
            threading.Thread(target=self.http_com("logout", "logout"), daemon = True).start()
            
            # Es torna a iniciar un thread on s’executarà read_uid
            thread = threading.Thread(target=self.read_uid)
            thread.daemon = True
            thread.start()

    # Determina que es fa al polsar una tecla
    def on_key_press_event(self, widget, event):
        # Tecla Enter
        if Gdk.keyval_name(event.keyval) == 'Return':
            # Obtenim el text i executem un thread on s’executarà http_com
            query = self.entry.get_text()
            self.entry.set_text("")
            threading.Thread(target=self.http_com("search", query), daemon = True).start()
            
    # Implementació de Rfid.read_uid()
    def read_uid(self):
        # Obtenim l'uid de la targeta i actualitzem la variable global usuari
        rf = Rfid()
        uid = rf.read_uid()
        
        # Actualitzem el valor d'ACK
        self.ACK = 1
        
        #global user
        user["uid"] = uid
        threading.Thread(target=self.http_com("login", "students?student_id="+uid), daemon = True).start()
        
        # Fem el botó visible
        GLib.idle_add(self.button.set_opacity, 1)

    # Envia la query al servidor i retorna la taula
    def http_com(self, request, query):
        # Esborrem les columnes i les files prèvies
        for col in self.result.get_columns():
            self.result.remove_column(col)
        self.listmodel.clear()
        self.listmodel2.clear()

        # Enviem la query al servidor i la transformem a format json
        global s

        r = s.get("http://127.0.0.1:81/" + query)
        
        if(r.text == "Not logged in"):
            self.lcd.clear()
            self.lcd.display("Session expired,",2,2)
            self.lcd.display("please login again",3,1)
            GLib.idle_add(self.label.set_label,"Session expired, please login again") #'Please, login with your university card'
            GLib.idle_add(self.label.set_opacity, 1)
            GLib.idle_add(self.nameLabel.set_opacity, 0)
            GLib.idle_add(self.entry.set_opacity, 0)
            
            # En cas d'estar visualitzant una taula l'esborrem
            self.listmodel.clear()
            self.listmodel2.clear()
            
            # Fem el botó invisible
            GLib.idle_add(self.button.set_opacity, 0)
            
            thread = threading.Thread(target=self.read_uid)
            thread.daemon = True
            thread.start()
            return
        
        if(request == "logout"):
            return
            
        jsn = r.json()
        #global user
        # En cas de ser un inici de sessió
        if request is "login":
            # Actualitzem la variable global usuari i el text del Label
            if(jsn):
                user["name"] = jsn[0]["name"]
                self.lcd.clear()
                self.lcd.display("Welcome",2,7)
                n = math.trunc((20-len(user["name"]))/2)
                self.lcd.display(user["name"], 3, n) 
                GLib.idle_add(self.button.set_label, "Logout")
                GLib.idle_add(self.nameLabel.set_label,"Welcome " + user["name"])
                GLib.idle_add(self.nameLabel.set_opacity, 1)
                GLib.idle_add(self.label.set_opacity, 0)
                GLib.idle_add(self.entry.set_opacity, 1)
            else:
                self.lcd.clear()
                self.lcd.display("Invalid user card,", 2, 1)
                self.lcd.display("please try again", 3, 2)
                GLib.idle_add(self.label.set_name, "invalid")
                GLib.idle_add(self.label.set_label, "Invalid user card, please try again")
                GLib.idle_add(self.label.set_opacity, 1)
                GLib.idle_add(self.button.set_label, "Try again")
 
                
        # En cas de ser una búsqueda    
        elif request is "search":
            # Si és la taula timetables, es necessiten 4 columnes
            if "timetables" in query:
                lm = self.listmodel2
                
                # Amplada a aplicar a les columnes
                sz = 195
                
            # Si és qualsevol altra taula, es necessiten 3 columnes
            else:
                lm = self.listmodel
                
                # Amplada a aplicar a les columnes
                sz = 260
                
            # Apliquem el model de llista al TreeView
            self.result.set_model(model=lm)
            
            # Afegim els valors al model
            for i in range(len(jsn)):
                lm.append(jsn[i].values())
                
            # Per cada columna   
            for i, column in enumerate(jsn[0].keys()):
                # Renderitzem el text
                cell = Gtk.CellRendererText()
                
                # Creem la columna i determinem la seva amplada
                col = Gtk.TreeViewColumn(column, cell, text=i)
                col.set_fixed_width(sz)
                
                # Afegim la columna al TreeView
                self.result.append_column(col)
def app_main():
    win = Window()
    win.style_provider = Gtk.CssProvider()
    win.style_provider.load_from_path('custom.css')
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), win.style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
	

# Programa principal
if __name__ == "__main__":
    app_main()
    Gtk.main()
