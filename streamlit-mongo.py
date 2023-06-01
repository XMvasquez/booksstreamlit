from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import streamlit as st
import plotly.express as px
import os

# mongodb url 
uri = "mongodb+srv://ximenavasquez3410:Vasquez3410@cluster0.qgtpg76.mongodb.net/?retryWrites=true&w=majority"

# Connect to meme MongoDB database
try:
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")

    db = client.tkdapp
    print("MongoDB Connected successfully!")
except:
    print("Could not connect to MongoDB")

# streamlit run streamlit-mongo.py --server.enableCORS false --server.enableXsrfProtection false

st.title("Books social media")
# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def getReactions(_db):
    items = _db.tkdapp_reactions.find()
    items = list(items)  # make hashable for st.cache_data
    return items

def getComments(_db):
    items = _db.tkdapp_comments.find()
    items = list(items)  # make hashable for st.cache_data
    return items

def getReactionsSummary(_db):
    items = _db.tkdapp_reactions_sumary.find()
    items = list(items)  # make hashable for st.cache_data
    return items

dataReactions = getReactions(db) 

dataComments = getComments(db)

dataReactionsSumary = getReactionsSummary(db)

st.sidebar.title("Ximena Vasquez")
st.sidebar.write("s20006727")
st.sidebar.markdown("___")



st.subheader("Gráficos")

st.write("1. Histograma que muestra la relacion entre la cantidad de interaccion (reacciones) que han tenido las publicaciones")
histoR = px.histogram(dataReactions, x='objectid', nbins=15)
histoR.update_layout(title='Reacciones por publicacion',
                  xaxis_title='publicacion',
                  yaxis_title='Frecuencia')
st.plotly_chart(histoR)

st.write("\n\n2. Histograma que muestra la relacion entre la cantidad de comentarios que han tenido las publicaciones")
histoC = px.histogram(dataComments, x='objectid', nbins=15)
histoC.update_layout(title='Comentarios por publicacion',
                  xaxis_title='publicacion',
                  yaxis_title='Frecuencia')
st.plotly_chart(histoC)

st.write("\n\n3. Grafica de barras que muestra cuantas veces a participado cada competidor.\n Para el grafico se cargaron los primero 30 registros")

barR = px.bar(dataReactions, x='reactionid', y='objectid', orientation='h', color='reactionid')
barR.update_layout(title='¿Cuantas reacciones tienen las publicaciones?',
                  xaxis_title='reacciones',
                  yaxis_title='publicaciones')

st.plotly_chart(barR)

st.write("\n\n4. Grafica de dispersion que muestra las publicaciones en las que los usuarios han comentado")
dispC = px.scatter(dataComments, x='userid', y='objectid')
dispC.update_layout(title='Grafica de Dispersión',
                   xaxis_title='usuario',
                   yaxis_title='publicaciones')
st.plotly_chart(dispC)

st.write("\n\n5. Grafica de dispersion que muestra las reacciones que hay en cada publicacion")
dispR = px.scatter(dataReactions, x='reactionid', y='objectid')
dispR.update_layout(title='Grafica de Dispersión',
                   xaxis_title='reacciones',
                   yaxis_title='publicaciones')
st.plotly_chart(dispR)
st.markdown("___")

#DATOS
st.subheader("\nDatos")

st.write('1. Datos de las reacciones en Formato JSON')
st.write('**JSON Reactions**')
st.json(dataReactions)

st.write('\n\n2. Datos de las reacciones en Formato Tabla')
tablaDataReactions = pd.DataFrame(dataReactions)
st.write('**Tabla Reactions**')
st.dataframe(tablaDataReactions)

st.write('\n\n3. Datos de los comentarios en Formato JSON')
st.write('**JSON Comments**')
st.json(dataComments)

st.write('\n\n4. Datos de los comentarios en Formato Tabla')
st.write('**Tabla Comments**')
tablaDataComments =pd.DataFrame(dataComments)
st.dataframe(tablaDataComments)

st.write('\n\n5. Datos de Reactions sumary en Formato JSON')
st.write('**JSON Reactions sumary**')
st.json(dataReactionsSumary)

#el multiselect filtrar por sede
multiselectdf= tablaDataReactions.sort_values(by="reactionid") #para ordenar en alfabetico
reactionSelect = st.sidebar.multiselect("**6. Filtrar por reaccion**\n\nSelecciona la reaccion para mostrar", options=multiselectdf['reactionid'].unique(), default=multiselectdf['reactionid'].unique())

st.write("\n\n6. Mostrar publicaciones con cada reaccion:\n\n " + ", ".join(reactionSelect)) #concatenar la cadena game
st.write("**Filtrar por reaccion**")
st.write(multiselectdf.query(f"""reactionid==@reactionSelect"""))
st.markdown("___")

#el multiselect filtrar por sede
CommentOrden= tablaDataComments.sort_values(by="userid") #para ordenar en alfabetico
commentSelect = st.sidebar.selectbox("**7. Filtrar por comentario**\n\nSelecciona la publicacion para mostrar", CommentOrden['objectid'].unique())
st.write("\n\n7. Mostrar comentarios con cada publicacion:\n\n") #concatenar la cadena game
st.write("**Filtrar por comentario**")
st.write(CommentOrden.query(f"""objectid==@commentSelect"""))
st.markdown("___")


#  Calcular la cantidad de REACCIONES por objectid en tkdapp_reactions_sumary

st.subheader("\n\nCantidad de reacciones y comentarios\n\n")
reactions_count = {}
for item in dataReactionsSumary:
    objectid = item["_id"]["objectid"]
    reactionid = item["_id"]["reactionid"]
    count = item["n"]

    if objectid not in reactions_count:
        reactions_count[objectid] = {}
    
    reactions_count[objectid][reactionid] = count

for item in dataReactions:
    objectid = item["objectid"]
    reactionid = item["reactionid"]
    
    if objectid not in reactions_count:
        reactions_count[objectid] = {}
    
    if reactionid not in reactions_count[objectid]:
        reactions_count[objectid][reactionid] = 0
    
    reactions_count[objectid][reactionid] += 1

# Mostrar la cantidad de reacciones por objectid
for objectid, reactions in reactions_count.items():
    st.write(f"El objectid **{objectid}** tiene:")
    
    for reaction, count in reactions.items():
        st.write(f"{count} {reaction}")
    
    st.write("---")

comentarios_por_objectid = {}

# Recorrer el JSON y almacenar los comentarios por objectid
for item in dataComments:
    objectid = item["objectid"]
    userid = item["userid"]
    message = item["message"]
    
    if objectid not in comentarios_por_objectid:
        comentarios_por_objectid[objectid] = []
    
    comentarios_por_objectid[objectid].append({"userid": userid, "message": message})

# Mostrar los comentarios por objectid
for objectid, comentarios in comentarios_por_objectid.items():
    st.write(f"Comentarios de **{objectid}**:")
    
    for comentario in comentarios:
        userid = comentario["userid"]
        message = comentario["message"]
        
        st.write(f"{userid}: {message}")
    
    st.write("---")




