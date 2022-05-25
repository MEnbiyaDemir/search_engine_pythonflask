from asyncio.windows_events import NULL
import requests as req
from flask import Flask,render_template, redirect, request,url_for
from py2neo import Graph
import pandas as pd
from pyparsing import null_debug_action


graph = Graph("bolt://localhost:7687", auth=("academy", "academy"))


app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

    
@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/adminpage',methods=["POST","GET"])
def adminpage():
    if request.method == "POST":
        email=request.form.get("emailogin")
        password=request.form.get("passlogin")
        if password == email=="admin":
            
            query='''
            Match (n:Arastirmaci)
            WHERE n.xml = 'yes'
            RETURN n
            '''
            xmlyes = graph.run(query).data()

            
            # kisiler
            query='''
            Match (n:Arastirmaci)
            RETURN n
            '''
            kisiler = graph.run(query).data()

            # yayinlar
            query='''
            Match (n:Yayin)
            RETURN n
            '''
            yayinlar = graph.run(query).data()

            # yayincilar
            query='''
            Match (n:YayinYeri)
            RETURN n
            '''
            yayincilar = graph.run(query).data()

            return render_template("adminpage.html",xmlyes=xmlyes,kisiler=kisiler,yayinlar=yayinlar,yayincilar=yayincilar)
        else:
          return redirect(url_for('index'))

@app.route('/search',methods=["POST","GET"])
def search():

     if request.method == "POST" or request.method == "GET":
        arama_sorgusu=request.form.get("arama")
        if(arama_sorgusu == None):
            arama_sorgusu = ""
        query='''
        MATCH (n)
        WHERE n.name =~ '(?i).*{}.*' OR n.title =~ '(?i).*{}.*'
        RETURN n.name as name,n.pid as pid, n.bookid as bookid, n.title as baslik
        '''.format(arama_sorgusu,arama_sorgusu)
        sonuc = graph.run(query).data()
        

        return render_template("search.html", sonuc=sonuc,arama_sorgusu=arama_sorgusu)
     

@app.route("/person/")
@app.route("/person/<pid1>/<pid2>")
def person(pid1 = None, pid2 = None):
    if(pid1 == None):
        return redirect(url_for('search'))
    else:
        pid = pid1+"/"+pid2

        query='''
        MATCH (n:Arastirmaci {{pid: "{}"}})-[:YAYIN_YAZARI]->(y:Yayin)
        RETURN y
        ORDER BY y.year desc
        '''.format(pid)
        yayinlar = graph.run(query).data()
       

        query='''
        MATCH (n:Arastirmaci {{pid: "{}"}})
        RETURN n.name as name
        '''.format(pid)
        isim = graph.run(query).data()
        
        query='''
        MATCH (n:Arastirmaci {{pid: "{}"}})-[:ORTAK_CALISIR]->(y:Arastirmaci)
        RETURN y
        '''.format(pid)
        coauthors = graph.run(query).data()
        return render_template("person.html",pid1=pid1,pid2=pid2,yayinlar=yayinlar,isim=isim,coauthors=coauthors)
     

@app.route("/publisher/")
@app.route("/publisher/<pid>")
def publisher(pid = None):
    if(pid == None):
        return redirect(url_for('search'))
    else:
        query='''
        MATCH (x:Yayin)-[:YAYINLANIR]->(y:YayinYeri {{name: "{}"}})
        RETURN x
        '''.format(pid)
        yayinlar = graph.run(query).data()
        return render_template("publisher.html",pid=pid,yayinlar=yayinlar)     

@app.route("/book/")
@app.route("/book/<pid1>/<pid2>/<pid3>")
def book(pid1 = None, pid2 = None, pid3 = None):
    if(pid1 == None):
        return redirect(url_for('search'))
    else:
        pid = pid1+"/"+pid2+"/"+pid3
        query='''
        MATCH (n:Yayin {{bookid: "{}"}})
        RETURN n
        '''.format(pid)
        sonuc = graph.run(query).data()

        query='''
        MATCH (n:Yayin {{bookid: "{}"}})<--(a:Arastirmaci)
        RETURN a
        '''.format(pid)
        authors = graph.run(query).data()

        query='''
        MATCH (n:Yayin {{bookid: "{}"}})-->(a:YayinYeri)
        RETURN a
        '''.format(pid)
        tt = graph.run(query).data()
        
        
        if(len(tt) == 0):
            tt=[]
        
        return render_template("book.html",pid=pid,sonuc=sonuc,authors=authors,tt=tt,pid2=pid2)   


@app.route('/deleteperson',methods=["POST","GET"])
def deleteperson():

 if request.method == "POST":
     
    select = request.form.get('comp_select_persons')
    print(select)

    query='''
    Match (n:Arastirmaci {{pid: '{}'}})
    detach DELETE n
    '''.format(select)
    graph.run(query)

    # xmli olan kisi verileri
    query='''
    Match (n:Arastirmaci)
    WHERE n.xml = 'yes'
    RETURN n
    '''
    xmlyes = graph.run(query).data()

    
    # kisiler
    query='''
    Match (n:Arastirmaci)
    RETURN n
    '''
    kisiler = graph.run(query).data()

    # yayinlar
    query='''
    Match (n:Yayin)
    RETURN n
    '''
    yayinlar = graph.run(query).data()

    # yayincilar
    query='''
    Match (n:YayinYeri)
    RETURN n
    '''
    yayincilar = graph.run(query).data()

    return render_template("adminpage.html",xmlyes=xmlyes,kisiler=kisiler,yayinlar=yayinlar,yayincilar=yayincilar)
    #return render_template("adminpage.html",xmlyes=xmlyes,kisiler=kisiler,yayinlar=yayinlar)


@app.route('/deletebook',methods=["POST","GET"])
def deletebook():

 if request.method == "POST":

    select = request.form.get('comp_select_books')
    print(select)

    query='''
    Match (n:Yayin {{bookid: '{}'}})
    detach DELETE n
    '''.format(select)

    graph.run(query)

    # xmli olan kisi verileri
    query='''
    Match (n:Arastirmaci)
    WHERE n.xml = 'yes'
    RETURN n
    '''
    xmlyes = graph.run(query).data()

    
    # kisiler
    query='''
    Match (n:Arastirmaci)
    RETURN n
    '''
    kisiler = graph.run(query).data()

    # yayinlar
    query='''
    Match (n:Yayin)
    RETURN n
    '''
    yayinlar = graph.run(query).data()

    # yayincilar
    query='''
    Match (n:YayinYeri)
    RETURN n
    '''
    yayincilar = graph.run(query).data()

    return render_template("adminpage.html",xmlyes=xmlyes,kisiler=kisiler,yayinlar=yayinlar,yayincilar=yayincilar)


@app.route('/deletepublisher',methods=["POST","GET"])
def deletepublisher():

 if request.method == "POST":

    select = request.form.get('comp_select_publishers')
    print(select)

    query='''
    Match (n:YayinYeri {{name: '{}'}})
    detach DELETE n
    '''.format(select)

    graph.run(query)

    # xmli olan kisi verileri
    query='''
    Match (n:Arastirmaci)
    WHERE n.xml = 'yes'
    RETURN n
    '''
    xmlyes = graph.run(query).data()

    
    # kisiler
    query='''
    Match (n:Arastirmaci)
    RETURN n
    '''
    kisiler = graph.run(query).data()

    # yayinlar
    query='''
    Match (n:Yayin)
    RETURN n
    '''
    yayinlar = graph.run(query).data()

    # yayincilar
    query='''
    Match (n:YayinYeri)
    RETURN n
    '''
    yayincilar = graph.run(query).data()

    return render_template("adminpage.html",xmlyes=xmlyes,kisiler=kisiler,yayinlar=yayinlar,yayincilar=yayincilar)

@app.route('/xml',methods=["POST","GET"])
def xml():
    if request.method == "POST":
        xml_url = request.form.get("urltext")

        #  xml sayfası kime aitse onun pid ve isimini alma
        query='''
        CALL apoc.load.xml("{}")
        YIELD value
        UNWIND value._children AS bookx
        UNWIND bookx._children AS book

        RETURN
        [item in book WHERE item._type = "author"][0]._text as sahip,
        [item in book WHERE item._type = "author"][0].pid as sahipid
        '''.format(xml_url)


        result = graph.run(query).to_data_frame()
        df =  pd.DataFrame(result)
        sahip = df.iloc[0,0]
        sahipid = df.iloc[0,1]
        


        #  bir çok bilgiyi ekleme
        query='''
        CALL apoc.load.xml("{}")
        YIELD value
        UNWIND value._children AS bookx
        UNWIND bookx._children AS book

        UNWIND book.key as bookid
        UNWIND size( [item in book._children WHERE item._type = "author"]) as kackisi
        UNWIND [item in book._children WHERE item._type = "title"][0]._text AS baslik
        UNWIND book._type as tur
        
        UNWIND [item in book._children WHERE item._type = "year"][0]._text as yil

        WITH baslik, kackisi, tur, yil,bookid,
        [item in book._children WHERE item._type = "journal" or item._type = "publisher"][0]._text as publish,
        [i IN range(0, kackisi-1) | [item in book._children WHERE item._type = "author"][i]._text] as authors,
        [i IN range(0, kackisi-1) | [item in book._children WHERE item._type = "author"][i].pid] as authorsid

        MERGE (y:Arastirmaci {{name: "{}"}})
        SET y.pid = "{}", y.xml = "yes"

        MERGE (b:Yayin {{bookid: bookid}})
        SET b.title = baslik, b.year = yil, b.tur = tur

        MERGE (y)-[:YAYIN_YAZARI]->(b)

        foreach (n in publish | MERGE (g:YayinYeri {{name:n}}) MERGE (b)-[:YAYINLANIR]->(g))
        foreach (n in authors | MERGE (a:Arastirmaci {{name:n}})  MERGE (y)-[:ORTAK_CALISIR]->(a) MERGE (a)-[:YAYIN_YAZARI]->(b)    )

        WITH y
        MATCH (y)-[r:ORTAK_CALISIR]->(y) DELETE r

        '''.format(xml_url, sahip, sahipid, xml_url)

        graph.run(query)


        # coauthorlara pid ekleme
        query='''
        CALL apoc.load.xml("{}")
        YIELD value
        UNWIND value._children AS bookx
        UNWIND bookx._children AS book

        MATCH (n {{name: "{}"}})-[:ORTAK_CALISIR]->(m)
        WITH   [item in book._children WHERE item._text = m.name][0].pid  as asas, m
        ORDER BY asas 
        foreach(y in asas | set m.pid = y) 
        '''.format(xml_url,sahip)
        graph.run(query)
        
        # <ee> electronic edition linki ekleme
        query='''
        CALL apoc.load.xml("{}")
        YIELD value
        UNWIND value._children AS bookx
        UNWIND bookx._children AS book

        UNWIND [item in book._children WHERE item._type = "ee"][0]._text as publishlink
        UNWIND [item in book._children WHERE item._type = "title"][0]._text AS baslik

        MATCH x=(n:Yayin)
        WHERE n.title = baslik
        FOREACH (n IN nodes(x) | SET n.ee = publishlink)
        '''.format(xml_url)
        graph.run(query)


        #  pages ekleme
        query='''
        CALL apoc.load.xml("{}")
        YIELD value
        UNWIND value._children AS bookx
        UNWIND bookx._children AS book

        UNWIND [item in book._children WHERE item._type = "pages"][0]._text as pages
        UNWIND [item in book._children WHERE item._type = "title"][0]._text AS baslik

        MATCH x=(n:Yayin)
        WHERE n.title = baslik
        FOREACH (n IN nodes(x) | SET n.pages = pages)
        '''.format(xml_url)
        graph.run(query)

        # coauthorslar arasındaki ORTAK_CALISIR bağlantıyı ekleme
        query='''
        MATCH (a:Arastirmaci)-[:YAYIN_YAZARI ]->(y:Yayin)<--(c:Arastirmaci)
        MERGE (a)-[:ORTAK_CALISIR]->(c)
        MERGE (c)-[:ORTAK_CALISIR]->(a)
        '''
        graph.run(query)

        # xmli olan kisi verileri
        query='''
        Match (n:Arastirmaci)
        WHERE n.xml = 'yes'
        RETURN n
        '''
        xmlyes = graph.run(query).data()

        
        # kisiler
        query='''
        Match (n:Arastirmaci)
        RETURN n
        '''
        kisiler = graph.run(query).data()

        # yayinlar
        query='''
        Match (n:Yayin)
        RETURN n
        '''
        yayinlar = graph.run(query).data()

        # yayincilar
        query='''
        Match (n:YayinYeri)
        RETURN n
        '''
        yayincilar = graph.run(query).data()

        return render_template("adminpage.html",xmlyes=xmlyes,kisiler=kisiler,yayinlar=yayinlar,yayincilar=yayincilar)
    

if __name__=="__main__":
    app.run(debug=True)

    