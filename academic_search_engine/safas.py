from asyncio.windows_events import NULL
import requests as req
from flask import Flask,render_template, redirect, request,url_for
from py2neo import Graph
import pandas as pd
from pyparsing import null_debug_action

graph = Graph("bolt://localhost:7687", auth=("academy", "academy"))

query='''
match (n:Arastirmaci {pid: '297/6826'})--(y:Yayin)
return y.bookid as bookid
'''
sonuc = graph.run(query).to_data_frame()
df =  pd.DataFrame(sonuc)
i = range(df.size)

for n in i:
    sahip = df.iloc[n,0]
    print(sahip)
    query='''
    match (n:Yayin {{bookid: '{}'}})--(a:Arastirmaci)
    return a.name
    '''.format(sahip)
    sonuc = graph.run(query).data()
    print(sonuc)
