#!/usr/bin/python
import argparse
from argparse import RawTextHelpFormatter
import pygame
from pygame import gfxdraw
import random
import sys
from math import sqrt
from time import sleep
          
class pto():
    '''Creates a point on a coordinate plane with values x and y.'''
    def __init__(self, x=0, y=0):
        self.x, self.y = x,y
    def __str__(self):
        return '({x}, {y})'.format(x=self.x, y=self.y)
    def __add__(self, other):
        if isinstance(other, pto):
            return pto(self.x+other.x, self.y+other.y) #vector addition
        else:
            return pto(self.x+other, self.y+other)
    def __sub__(self, other):
        if isinstance(other, pto):
            return pto(self.x-other.x, self.y-other.y) #vector subtraction
        else:
            return pto(self.x-other, self.y-other)
    def __mul__(self, other):
        if isinstance(other, pto):
            return pto(self.x*other.x, self.y*other.y)
        else:
            return pto(self.x*other, self.y*other) #scalar multiplication
    def __truediv__(self, n):
        return pto(self.x/n, self.y/n)
    def len(self):
        return sqrt(self.x**2+self.y**2) #Euclidean norm

#Auxiliar functions
def totuple(p):
    return (int(p.x), int(p.y))
def fromtuple(p):
    x, y = p
    return pto(x, y)
def dist(p, q):
    return (q-p).len()    
def next_string(s):
    strip_zs = s.rstrip('Z')
    if strip_zs:
        return strip_zs[:-1] + chr(ord(strip_zs[-1]) + 1) + 'A' * (len(s) - len(strip_zs))
    else:
        return 'A' * (len(s) + 1)

class LayoutGraph():
    def __init__(self, c1, c2, W, L, full):
        '''    
        Parametros de layout:
        c1: constante usada para calcular la repulsion entre nodos
        c2: constante usada para calcular la atraccion de aristas
        '''   
        self.W=W
        self.L=L
        self.c1 = c1
        self.c2 = c2
        pygame.display.set_caption('Fruchterman\'s Algorithm')
        self.radio=int(min(self.W, self.L)/50)
        self.reloj=pygame.time.Clock()
        if full:
            self.W, self.L=pygame.display.Info().current_w, pygame.display.Info().current_h
        self.pantalla=pygame.display.set_mode((self.W, self.L), pygame.FULLSCREEN if full else 0)
        
        
    def input(self):
        BOTONIZQ=1
        BOTONMIDDLE=2
        BOTONDER=3
        for evento in pygame.event.get():
            if evento.type==pygame.QUIT:#cierra ventana
                self.running=False
            elif evento.type==pygame.MOUSEBUTTONDOWN:
                self.t=self.initemp
                mpos=self.clip(fromtuple(evento.pos))
                v=self.getnode(mpos)
                if v!=None:
                    if evento.button==BOTONDER:#agregar arista
                        self.arsel=v
                    elif evento.button==BOTONMIDDLE:#fijar nodo
                        self.fixed[v]=not self.fixed[v]
                    else:#seleccionar/borrar nodo
                        self.arsel=None
                        if pygame.key.get_pressed()[pygame.K_RSHIFT] or pygame.key.get_pressed()[pygame.K_LSHIFT]:
                            self.V.remove(v)
                            self.E={(x,y) for (x,y) in self.E if x!=v and y!=v}
                        else:
                            self.selected=v
                else:#agregar nodo
                    name=next_string(max(self.V) if self.V else 'A')
                    self.V.add(name)
                    self.fixed[name]=True if evento.button==BOTONMIDDLE else False
                    self.pos[name]=mpos
                    self.calck()
            elif evento.type==pygame.MOUSEBUTTONUP:
                if evento.button==BOTONDER and self.arsel is not None:
                    mpos=self.clip(fromtuple(evento.pos))
                    v=self.getnode(mpos)
                    if v is not None and v!=self.arsel:
                        ar=(self.arsel, v) if self.arsel>v else (v, self.arsel)
                        if ar in self.E:
                            self.E.remove(ar)
                        elif self.arsel!=v:
                            self.E.add(ar)
                self.arsel=None
                self.selected=None
            elif evento.type==pygame.MOUSEMOTION and self.selected is not None:#move node
                self.t=self.initemp
                self.pos[self.selected]= self.clip(fromtuple(evento.pos))
            elif evento.type==pygame.KEYDOWN:
                if evento.key==pygame.K_q:#quit
                    self.running=False
                if evento.key==pygame.K_g:#gravity
                    self.gravedad=not self.gravedad
                elif evento.key==pygame.K_r:
                    self.reset()
                elif evento.key==pygame.K_p and self.V:#pause
                    if max(self.fixed.values()):
                        self.fixed={v:False for v in self.V}
                    else:
                        self.fixed={v:True for v in self.V}
                elif evento.key==pygame.K_s:#prints graph
                    print(len(self.V))
                    print('\n'.join(v for v in self.V))
                    print('\n'.join("{0} {1}".format(x,y) for (x,y) in self.E))
        
    def draw(self):
        ''' Dibuja (o actualiza) el estado del grafo en pantalla'''
        BLANCO=(0xFF,0xFF,0xFF)
        VERDE=(0,0xFF,0)
        NEGRO=(0,0,0)
        ROJO=(0xFF,0,0)
        self.pantalla.fill(NEGRO)
        for (v,u) in self.E:
            pygame.draw.aaline(self.pantalla, BLANCO, totuple(self.pos[v]), totuple(self.pos[u]))
        for v in self.V:
            if self.selected==v or self.arsel==v:
                color=VERDE
            elif self.fixed[v]:
                color=ROJO
            else:
                color=BLANCO
            pygame.gfxdraw.filled_circle(self.pantalla, int(self.pos[v].x), int(self.pos[v].y), self.radio,  color)
            pygame.gfxdraw.aacircle(self.pantalla, int(self.pos[v].x), int(self.pos[v].y), self.radio,  color)#anti aliased border
        pygame.display.flip()
        self.reloj.tick(50) #frames per second

    def layout(self, G):
        '''
        Aplica el algoritmo de Fruchtermann-Reingold para obtener (y mostrar) 
        un layout        
        '''
        V, E = G
        self.V=set(V)
        self.E={(x,y) if x>y else (y,x) for (x,y) in E}
        self.gravedad=True
        self.running=True
        epsilon = 1e-9 #used to avoid division by zero
        self.area = self.W*self.L
        centro=pto(self.W, self.L)/2
        self.initemp=sqrt(self.area)*0.000018 #initial temperature
        disp = {v: pto() for v in self.V}
        self.fixed = {v: False for v in self.V}
        self.calck()
        self.reset() #random initial positions of vertices
        
        fa = lambda x: x*x/self.k
        fr = lambda x: self.k*self.k/x
        heat = lambda t: min(t*1.22, 0.05)	#temperature increases up to 0.05
        
        # Bucle principal Fruchterman-Reingold
        while self.running:
            # 1: Calcular repulsiones de nodos (actualiza fuerzas)
            for v in self.V:
                disp[v]=pto(0,0)
                for u in self.V:
                    if u!=v:
                        d = self.pos[v]-self.pos[u]
                        dlen=max(d.len(), epsilon)
                        disp[v] = disp[v] + (d/dlen)*fr(dlen)
            # 2: Calcular atracciones de aristas (actualiza fuerzas)
            for v,u in self.E:
                d=self.pos[v]-self.pos[u]
                dlen=max(d.len(), epsilon)
                if v == self.selected or u == self.selected:
                    dlen*=10
                disp[v]= disp[v] - (d/dlen) * fa(dlen)
                disp[u]= disp[u] + (d/dlen) * fa(dlen)
                
            # 3: Calcular fuerza de gravedad
            if self.gravedad:
                for v in self.V:
                    f=centro-self.pos[v]
                    disp[v]=disp[v] + f*4 #gravity force = 4
            
            # 4: En base a fuerzas, actualizar posiciones, setear fuerzas a cero
            for v in self.V:
                if not self.fixed[v] and v!=self.selected:
                    displen=max(disp[v].len(), epsilon)
                    self.pos[v]= self.pos[v] + (disp[v]/displen)*displen*self.t
                    self.pos[v]= self.clip(self.pos[v])
            self.t=heat(self.t)
            self.input()
            self.draw()
        
    def reset(self):
        self.t=self.initemp
        stripborder=lambda d: d-self.radio*2
        self.selected=None
        self.arsel=None
        self.pos = {v: pto(random.random()*stripborder(self.W)+self.radio,
                           random.random()*stripborder(self.L)+self.radio)
                        if not self.fixed[v] else self.pos[v] 
                        for v in self.V}
        
    def clip(self, p):
        return pto( min(self.W-self.radio-1, max(self.radio, p.x)),
                    min(self.L-self.radio-1, max(self.radio, p.y)))
    def calck(self):
        self.k = 0.8*sqrt(self.area/len(self.V)) if self.V else 0
    
    def getnode(self, mousepos):
        for v in self.V:
            if dist(mousepos, self.pos[v])<=self.radio*1.5:
                return v
        return None
        
def leerGrafo(file=sys.stdin):
    npar=file.readline()
    if not npar:
        return ([],[])
    n=int(npar)
    nodos = [file.readline().strip() for x in range(n)]
    aristas = [line.strip().split() for line in file if len(line)>1]
    return (nodos, aristas)

def main():
    parser = argparse.ArgumentParser(description='Fruchterman Interactive Algorithm',
        formatter_class=RawTextHelpFormatter, epilog="""
Blank nodes move freely, red nodes stand still.
Mouse:
    Left   click on empty space: Create a blank node
    Middle click on empty space: Create a red node
    
    Left   click on node: Move node (keep pressed)
    Left   click on node + Shift: Erase node
    Right  click on node: Add edge (keep pressed and join the nodes)
    
    Middle click on node: Change node color
    
Keyboard:
    Q: Quit
    G: Toggle gravity
    R: Randomize nodes
    P: Paint all nodes white/red
    S: Print current graph to console
""")
    
    parser.add_argument('--w', type=int, 
                        help='Ancho de la ventana', 
                        default=700)
    parser.add_argument('--l', type=int, 
                        help='Largo de la ventana', 
                        default=700)
    parser.add_argument('-f', '--fullscreen', 
                        action='store_true', 
                        help='Pantalla completa')

    args = parser.parse_args()
    pygame.init()
    
    G=leerGrafo()
    # Creamos nuestro objeto LayoutGraph
    layout_gr = LayoutGraph(
        c1=1.0,
        c2=2.5,
        W=args.w,
        L=args.l,
        full=args.fullscreen
        )
        
    random.seed()
    # Ejecutamos el layout
    layout_gr.layout(G)
    pygame.quit()
    return


if __name__ == '__main__':
    main()
