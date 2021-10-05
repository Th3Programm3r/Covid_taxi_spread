import numpy as np
import matplotlib.pyplot as plt
import psycopg2
import math
from matplotlib.animation import FuncAnimation
import datetime
import csv
from postgis import Polygon,MultiPolygon
from postgis.psycopg import register
import sys
from shapely.geometry import Point as POINT, Polygon as POLYGON 
from random import randint
from haversine import haversine

def animate(i):
    keysToDelete=[]#lista que vai ter os indexes contaminados no instante i
    temp=offsets[i]
    #verifica se um ponto ficou contaminado ou nao e actualiza os novos valores de probabilidade de todos os pontos nao infectados
    for j in notCont.keys():
        if j<=len(temp):
            t=temp[j]
            coord1=(t[0],t[1])#take coordinates from offsets in instant i
            for index in contTaxi:
                aux=temp[index]
                coord2=(aux[0],aux[1])
                res=haversine(coord1,coord2)
                m=res*1000
                metros=int(m)
                if metros <= 50:
                    number=[0,1]
                    probAdd=notCont[j]
                    sub=1-probAdd
                    prob=[sub,probAdd]
                    decision = random.choices(number, prob)
                    if decision==[1]:
                        contTaxi.append(j)
                        keysToDelete.append(j) 
                        break
                    else:
                        if notCont[j]<1:
                            notCont[j]=notCont[j]+0.1
                    
                    
    cor=[]
    for j in range(0,len(temp)):
        if j in contTaxi:
            cor.append('red')
        else:
            cor.append('green')

    for k in keysToDelete:
        del notCont[k]


                              
    scat.set_color(cor)    
    scat.set_offsets(offsets[i])

#transform linestring to points
def linestring_to_points(line_string):
    xs, ys = [],[]
    points = line_string[11:-1].split(',')
    for point in points:
        (x,y) = point.split()
        xs.append(float(x))
        ys.append(float(y))
    return xs,ys

#get all existent taxis
def getTaxis():
    conn = psycopg2.connect(dbname="tabd",user="postgres",password='asd')
    cursor_psql = conn.cursor()

    sql = """select distinct(taxi) from tracks order by 1 limit 500"""
    cursor_psql.execute(sql)
    results = cursor_psql.fetchall()
    taxis=[]
    for row in results:
        temp=row[0]
        taxis.append(temp)
    
    return taxis
#get all taxis linestring
def getAllLines():
    allLineString=[]
    
    for t in taxis:
        sql = """select st_astext(proj_track) from tracks where taxi='{}' order by ts""".format(t)
        cursor_psql.execute(sql)
        results = cursor_psql.fetchall()

        x, y = [], []
        for row in results:
            xs, ys = linestring_to_points(row[0])
            x = x + xs
            y = y + ys
        allLineString.append(list(zip(x,y)))
    return allLineString

#get the max lenght of a linestring line
def getMax():
    max=0
    for line in allLineString:
        n=len(line)
        if n>max:
            max=n
    return max


scale=1/3000000
conn = psycopg2.connect(dbname="tabd",user="postgres",password='asd')
register(conn)

xs_min, xs_max, ys_min, ys_max = -120000, 165000, -310000, 285000
width_in_inches = (xs_max-xs_min)/0.0254*1.1
height_in_inches = (ys_max-ys_min)/0.0254*1.1

fig, ax = plt.subplots(figsize=(width_in_inches*scale, height_in_inches*scale))
ax.axis('off')
ax.set(xlim=(xs_min, xs_max), ylim=(ys_min, ys_max))

cursor_psql = conn.cursor()
sql = "select distrito,st_union(proj_boundary) from cont_aad_caop2018 group by distrito"
cursor_psql.execute(sql)
results = cursor_psql.fetchall()
xs , ys = [],[]
lis,por=[],[]



for row in results:
    #apanha o conjunto de pontos sem o nome que esta na posicao row[0]
    #guarda na lista lis as coordenadas de lisboa e cria um plot com esses pontos 
    if row[0]=='LISBOA':
        geom = row[1]
        if type(geom) is MultiPolygon:
            for pol in geom:
                #apanha as coordenadas 
                xys = pol[0].coords
                xs, ys = [],[]
                for (x,y) in xys:
                    xs.append(x)
                    ys.append(y)
                    a=(x,y)
                    lis.append(a)
                ax.plot(xs,ys,color='black',lw='0.2')
              
        if type(geom) is Polygon:
            #agrupa os dados em coordenadas x,y
            xys = geom[0].coords
            xs, ys = [],[]
            #coloca todos os valores na posicao x na lista xs e na coordenada y na lista ys
            for (x,y) in xys:
                xs.append(x)
                ys.append(y)
                a=(x,y)
                lis.append(a)
            ax.plot(xs,ys,color='black',lw='0.2')
    #guarda na lista por as coordenadas de porto e cria um plot com esses pontos
    elif row[0]=='PORTO':
        geom = row[1]
        if type(geom) is MultiPolygon:
            for pol in geom:
                #apanha as coordenadas 
                xys = pol[0].coords
                xs, ys = [],[]
                for (x,y) in xys:
                    xs.append(x)
                    ys.append(y)
                    a=(x,y)
                    por.append(a)
                ax.plot(xs,ys,color='black',lw='0.2')
              
        if type(geom) is Polygon:
            #agrupa os dados em coordenadas x,y
            xys = geom[0].coords
            xs, ys = [],[]
            #coloca todos os valores na posicao x na lista xs e na coordenada y na lista ys
            for (x,y) in xys:
                xs.append(x)
                ys.append(y)
                a=(x,y)
                por.append(a)
            ax.plot(xs,ys,color='black',lw='0.2')

    #caso nao for porto ou lisboa
    else:
        geom = row[1]
        if type(geom) is MultiPolygon:
            for pol in geom:
                #apanha as coordenadas 
                xys = pol[0].coords
                xs, ys = [],[]
                for (x,y) in xys:
                    xs.append(x)
                    ys.append(y)
                ax.plot(xs,ys,color='black',lw='0.2')
              
        if type(geom) is Polygon:
            #agrupa os dados em coordenadas x,y
            xys = geom[0].coords
            xs, ys = [],[]
            #coloca todos os valores na posicao x na lista xs e na coordenada y na lista ys
            for (x,y) in xys:
                xs.append(x)
                ys.append(y)
            ax.plot(xs,ys,color='black',lw='0.2')        
        

l=[]   
offsets=[] 
taxis=getTaxis()
    
    
allLineString=getAllLines()
xs,ys=[],[] 
n=getMax()

#cria uma lista offset com os valores juntados de todos os line in linestring na posicao i 
for i in range(0,n):
    for line in allLineString:
        if len(line)>i:
            temp=line[i]
            (x,y)=temp
            l.append([x,y])
    offsets.append(l)
    l=[]

#coloca os pontos x e y na posicao inicial do offset para criar o scatter plot     
for i in offsets[0]:
    xs.append(i[0])
    ys.append(i[1])




#transforma a lista de coordenadas em um objecto polygon importado do pacote shapely.geometry
polyLis = POLYGON(lis)
polyPor = POLYGON(por)

lisTaxi=[]#index taxi lisboa
porTaxi=[]#index taxi porto



temp=offsets[0]
#verifica se uma coordenada esta dentro do poligono do porto ou de lisboa e se estiver adciona a uma lista
for i in range(0,len(temp)):
    if len(lisTaxi)>9 and len(porTaxi)>9:
        break
    t=temp[i]
    p=POINT(t[0],t[1])
    if polyLis.contains(p) and len(lisTaxi)<10:
        lisTaxi.append(i)
    if polyPor.contains(p) and len(porTaxi)<10:
        porTaxi.append(i)
    
#numeros aleatorios para apanhar as posicoes aleatorias dos 10 primeiros taxis de lisboa e do porto
ran1=randint(0, 9)
ran2=randint(0, 9)





notCont={}
contTaxi=[]
if len(lisTaxi)>0:
    contTaxi.append(lisTaxi[ran1])
    
contTaxi.append(porTaxi[ran2])

#lista com as cores em que inicialmente esta contaminado e nao contaminado
color=[]
for i in range(0,len(xs)):
    if i in contTaxi:
        color.append('red')
    else:
        color.append('green')
        notCont[i]=0.1


print(contTaxi)
    
    
    
scat = ax.scatter(xs,ys,c=color,s=10)

anim = FuncAnimation(fig, animate, interval=1, frames=len(offsets)-1,repeat=False)
plt.draw()
plt.show()
conn.close()