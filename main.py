import db
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime,time
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = '827868ee587c28d77682a8944cf3505a840bc1b3bd37d5e3e87e572b88b23e80'

@app.route("/accueilclient",methods=['GET','POST'])
def accueilclient():
    if (request.method == 'POST'):
        try:
            email = request.form['email']
            mdp = request.form['password']
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("set search_path to projet ")
                    cur.execute("select mdp from client where email = %s",(email,))
                    resultat = cur.fetchone()
            if resultat is not None:
                a = resultat[0]
                if check_password_hash(a,mdp) :
                    session['client'] = email
                    return redirect(url_for('client'))
                else :
                    return render_template('accueilclient.html',message = "验证失败")
            else :
                return render_template('accueilclient.html',message = "验证失败")
        except Exception as e :
            return render_template('accueilclient.html',message = "验证失败")
    return render_template('accueilclient.html',message = None)

@app.route("/register")
def register():
    return render_template('register.html',message = None)

@app.route("/register/verifier",methods=['GET','POST'])
def verifier():
    try:
        prenom = request.form['prenom']
        nom = request.form['nom']
        email = request.form['email']
        telephone = request.form['telephone']
        mdp = request.form['motDePasse']
        confirm = request.form['confirmationMotDePasse']
        ville = request.form['villeInsee']
        adresse = request.form['adresse']
        parraine = request.form['parraine']
        if (ville =='') :
            ville = None
        if (parraine =='') :
            parraine = None
        if (adresse =='') :
            adresse = None
        if (confirm != mdp):
            return render_template('register.html',message = '两次输入的密码不同')
        elif (len(ville)!=5):
            return render_template('register.html',message = "城市名无效")
        elif (len(telephone) != 10 ):
            return render_template('register.html',message = "手机号码格式错误")
        else :
            mdp = generate_password_hash(mdp)
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("set search_path to projet")
                    cur.execute("insert into client values(%s,%s,%s,%s,%s,%s,%s,%s)",(email,nom,prenom,telephone,mdp,adresse,ville,parraine))
                    return render_template('succes.html')
    except Exception as e :
        return render_template('register.html',message = "验证失败")

@app.route("/register/verifier/succes")
def succes():
    return render_template('succes.html')

@app.route("/accueil")
def accueil():
    return render_template('accueil.html')

@app.route("/accueillivreur",methods=['GET','POST'])
def accueillivreur():
    if (request.method == 'POST'):
        try:
            matricule = request.form['matricule']
            mdp = request.form['password']
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("set search_path to projet ")
                    cur.execute("select mdp_l from livreur where matricule = %s",(matricule,))
                    resultat = cur.fetchone()
            if resultat is not None:
                a = resultat[0]
                if check_password_hash(a,mdp) :
                    session['livreur'] = matricule
                    with db.connect() as conn:
                        with conn.cursor() as cur:
                            cur.execute("set search_path to projet ")
                            cur.execute("update livreur set etat = 'ON' where matricule = %s",(matricule,))
                    return redirect(url_for('livreur'))
                else :
                    return render_template('accueillivreur.html',message = "验证失败")
            else :
                return render_template('accueillivreur.html',message = "验证失败")
        except Exception as e :
            return render_template('accueillivreur.html',message = "验证失败")
    return render_template('accueillivreur.html',message = None)

@app.route("/client")
def client():
    email = session.get('client')
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("select nom,prenom from client where email = %s",(email,))
            resultat = cur.fetchone()
            nom, prenom = resultat
    current_time = datetime.now().time()
    current_time = current_time.replace(microsecond=0)
    atime = time(12, 0)
    atime = atime.replace(microsecond=0)
    btime = time(17,0)
    btime = btime.replace(microsecond=0)
    if current_time < atime:
        message = "早上好"
    elif current_time < btime and current_time > atime :
        message = "下午好"
    else:
        message = "晚上好"
    return render_template('client.html',nom = nom,prenom = prenom,message = message,current_time = current_time)

@app.route('/Verclient')
def Verclient():
    if 'client' in session :
        return redirect(url_for('client'))
    else:
        return redirect(url_for('accueilclient'))

@app.route('/Verlivreur')
def Verlivreur():
    if 'livreur' in session :
        return redirect(url_for('livreur'))
    else:
        return redirect(url_for('accueillivreur'))

@app.route('/Verrestaurant')
def Verrestaurant():
    if 'restaurant' in session :
        return redirect(url_for('restaur'))
    else:
        return redirect(url_for('accueilrestaurant'))

@app.route('/client/clientprofil')
def clientprofil():
    return render_template('clientprofil.html')

@app.route('/client/clientprofil/Historique')
def Historique():
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("SELECT commande.idresto,commande.idcommande,temps_com,temps_fin,choisir.nom_plat,quantite,prix FROM commande JOIN choisir ON commande.idcommande = choisir.idcommande JOIN offre ON choisir.nom_plat = offre.nom_plat AND commande.idresto = offre.idresto WHERE commande.email = %s and temps_fin is not NULL",(session['client'],))
            resultat = cur.fetchall()
    if resultat:
        result_dict = {}
        prixtotal = {}
        for idresto, idcommande, temps_com, temps_fin, nom_plat, quantite, prix in resultat:
            if idcommande in result_dict:
                result_dict[idcommande]['items'].append({
                    'idresto': idresto,
                    'temps_com': temps_com,
                    'temps_fin': temps_fin,
                    'nom_plat': nom_plat,
                    'quantite': quantite,
                    'prix': prix
                })
            else:
                result_dict[idcommande] = {
                    'items': [{
                        'idresto': idresto,
                        'temps_com': temps_com,
                        'temps_fin': temps_fin,
                        'nom_plat': nom_plat,
                        'quantite': quantite,
                        'prix': prix
                    }],
                    'prixtotal': 0
                }
            prixtotal.setdefault(idcommande, 0)
            prixtotal[idcommande] += prix * quantite
        for idcommande, data in result_dict.items():
            data['prixtotal'] = prixtotal[idcommande]
        return render_template('Historique.html', result_dict=result_dict, message=None)
    else :
        return render_template('Historique.html',result_dict=None,message = "没有历史记录。 ")


@app.route("/client/clientprofil/annuler",methods=['GET','POST'])
def annuler():
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("SELECT commande.idresto,commande.idcommande,temps_com,temps_fin,choisir.nom_plat,quantite,prix FROM commande JOIN choisir ON commande.idcommande = choisir.idcommande JOIN offre ON choisir.nom_plat = offre.nom_plat AND commande.idresto = offre.idresto WHERE commande.email = %s and temps_fin is NULL",(session['client'],))
            resultat = cur.fetchall()
    if resultat:
        result_dict = {}
        prixtotal = {}
        for idresto, idcommande, temps_com, temps_fin, nom_plat, quantite, prix in resultat:
            if idcommande in result_dict:
                result_dict[idcommande]['items'].append({
                    'idresto': idresto,
                    'temps_com': temps_com,
                    'temps_fin': temps_fin,
                    'nom_plat': nom_plat,
                    'quantite': quantite,
                    'prix': prix
                })
            else:
                result_dict[idcommande] = {
                    'items': [{
                        'idresto': idresto,
                        'temps_com': temps_com,
                        'temps_fin': temps_fin,
                        'nom_plat': nom_plat,
                        'quantite': quantite,
                        'prix': prix
                    }],
                    'prixtotal': 0
                }
            prixtotal.setdefault(idcommande, 0)
            prixtotal[idcommande] += prix * quantite
        for idcommande, data in result_dict.items():
            data['prixtotal'] = prixtotal[idcommande]
            return render_template('annuler.html',result_dict=result_dict,message = None)
    else :
        return render_template('annuler.html',message = "没有正在进行的订单。" , result_dict = None)

@app.route("/client/clientprofil/annuler/annulerverifier",methods=['POST'])
def annulerverifier():
    idcommande = request.form['idcommande']
    current_time = datetime.now()
    dtime = current_time.strftime('%Y-%m-%d %H:%M:%S')
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("update commande set temps_fin = %s  where idcommande = %s",(dtime,idcommande,))
    return redirect(url_for('annuler'))

@app.route('/client/clientprofil/noter',methods=['GET','POST'])
def noter():
    if (request.method == 'POST'):
        note = int(request.form['noter'])
        comment = request.form['comment'] or None
        idcommande =request.form['idcommande']
        idresto = request.form['idresto']
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("set search_path to projet")
                cur.execute("insert into evaluation values(%s,%s,%s,%s,%s)",(idresto,session['client'],note,comment,idcommande,))
        return redirect(url_for('noter'))
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet")
            cur.execute("SELECT commande.idresto,commande.idcommande,temps_com,temps_fin,choisir.nom_plat,quantite,prix FROM commande JOIN choisir ON commande.idcommande = choisir.idcommande JOIN offre ON choisir.nom_plat = offre.nom_plat AND commande.idresto = offre.idresto WHERE commande.email = %s and temps_fin is not null and not exists (select * from evaluation where evaluation.idresto = commande.idresto and evaluation.idcommande= commande.idcommande)",(session['client'],))
            resultat = cur.fetchall()
    if resultat:
        result_dict = {}
        prixtotal = {}
        for idresto, idcommande, temps_com, temps_fin, nom_plat, quantite, prix in resultat:
            if idcommande in result_dict:
                result_dict[idcommande]['items'].append({
                    'idresto': idresto,
                    'temps_com': temps_com,
                    'temps_fin': temps_fin,
                    'nom_plat': nom_plat,
                    'quantite': quantite,
                    'prix': prix
                })
            else:
                result_dict[idcommande] = {
                    'items': [{
                        'idresto': idresto,
                        'temps_com': temps_com,
                        'temps_fin': temps_fin,
                        'nom_plat': nom_plat,
                        'quantite': quantite,
                        'prix': prix
                    }],
                    'prixtotal': 0
                }
            prixtotal.setdefault(idcommande, 0)
            prixtotal[idcommande] += prix * quantite
        for idcommande, data in result_dict.items():
            data['prixtotal'] = prixtotal[idcommande]
            return render_template('noter.html',result_dict=result_dict,message = None)
    else :
        return render_template('noter.html',result_dict = None,message = "没有等待评价的订单。")

@app.route('/client/clientprofil/fidelite')
def fidelite():
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet")
            cur.execute("select count(idcommande) from commande where email = %s",(session['client'],))
            resultat = cur.fetchone()
            fidelite = resultat[0] * 10
            cur.execute("select parraine from client where email = %s",(session['client'],))
            a = cur.fetchone()
            if (a):
                fidelite = fidelite + 5
            if fidelite >100 :
                fidelite = 100
    return render_template('fidelite.html', fidelite=fidelite)

@app.route('/client/clientprofil/parraine',methods=['GET','POST'])
def parraine():
    if (request.method == 'POST'):
        try :
            parraine = request.form['parraine']
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("set search_path to projet")
                    cur.execute("update client set parraine = %s where email = %s",(parraine,session['client'],))
            return redirect(url_for('parraine'))
        except Exception as e :
            return render_template('parraine.html',message1 = "用户不存在")
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet")
            cur.execute("select parraine from client where email = %s ",(session['client'],))
            resultat = cur.fetchone()
            a = resultat[0]
    if a :
        return render_template('parraine.html',message ="你已经推荐了用户" )
    else :
        return render_template('parraine.html',message = None)


@app.route("/recherche",methods=['GET','POST'])
def recherche():
    if (request.method == 'POST'):
        nom = request.form['Nom']
        note = request.form['note']
        nombreavis = request.form['nombreavis']
        motclef = request.form['motclef']
        result = None
        restu = []
        nombre_re = []
        if(nom or note or nombreavis or motclef):
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("set search_path to projet")
                    current_datetime = datetime.now()
                    formatted_time = current_datetime.strftime("%H:%M:%S")
                    cur.execute("select ville_insee from client where email = %s",(session['client'],))
                    client_adresse = cur.fetchone()
                    if(nom):
                        cur.execute("Select idresto,nom_resto,sum(note)/count(note) AS note_r,count(commentaire) as nbcom from restaurant natural join evaluation where nom_resto = %s and ville_insee = %s and horaire_fer > %s and horaire_ouv < %s group by restaurant.idresto  ",(nom,client_adresse.ville_insee,formatted_time,formatted_time))
                        result = cur.fetchall()
                        if(note):
                            for i in result:
                                if i.note_r >= int(note):
                                    restu.append(i)
                            result = restu
                            if (nombreavis):
                                for i in restu:
                                    if i.nbcom >= int(nombreavis) :
                                        nombre_re.append(i)
                                result = nombre_re
                        elif(nombreavis):
                            for i in result:
                                if i.nbcom >= int(nombreavis) :
                                    nombre_re.append(i)
                            result = nombre_re
                        else:
                            cur.execute("select idresto, nom_resto from restaurant where nom_resto = %s and ville_insee = %s and horaire_fer > %s and horaire_ouv < %s",(nom,client_adresse.ville_insee,formatted_time,formatted_time))
                            result = cur.fetchall()
                    elif(note):
                        cur.execute("Select idresto,nom_resto,sum(note)/count(note) AS note_r,count(commentaire) as nbcom from restaurant natural join evaluation where  horaire_fer > %s and horaire_ouv < %s and ville_insee = %s group by restaurant.idresto  ",(formatted_time,formatted_time,client_adresse.ville_insee))
                        result = cur.fetchall()
                        for i in result:
                            if i.note_r >= int(note):
                                restu.append(i)
                        result = restu
                    elif(nombreavis):
                        cur.execute("Select idresto,nom_resto,sum(note)/count(note) AS note_r,count(commentaire) as nbcom from restaurant natural join evaluation where  horaire_fer > %s and horaire_ouv < %s and ville_insee = %s group by restaurant.idresto  ",(formatted_time,formatted_time,client_adresse.ville_insee))
                        result = cur.fetchall()
                        for i in result:
                            if i.nbcom >= int(nombreavis) :
                                nombre_re.append(i)
                        result = nombre_re
                    elif(motclef):
                        cur.execute("Select restaurant.idresto,nom_resto from restaurant  where horaire_fer > %s and horaire_ouv < %s and ville_insee = %s and nom_resto like %s",(formatted_time,formatted_time,client_adresse.ville_insee,'%' + motclef + '%'))
                        result = cur.fetchall()
                    return render_template('recherche.html',result = result)
    return render_template('recherche.html')


@app.route('/restaurant/<idresto>',methods = ['GET','POST'])
def idresto(idresto):
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet")
            cur.execute("select prix,offre.nom_plat,description,photo from offre , plat where offre.nom_plat = plat.nomplat and idresto = %s",(idresto,))
            result = cur.fetchall()
            cur.execute("select nom_resto,adresse_resto,horaire_ouv,horaire_fer,specialite,tel_resto,ville_insee from restaurant  where idresto = %s",(idresto,))
            result1 = cur.fetchone()
            cur.execute("select email,note,commentaire from evaluation where idresto = %s",(idresto,))
            result2 = cur.fetchall()
            return render_template('restaurant.html',result = result,idresto = idresto,result1 = result1,result2 = result2)


@app.route('/order/<code>',methods = ['GET','POST'])
def order(code):
    count = 0
    if (request.method == 'POST'):
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("set search_path to projet")
                current_datetime = datetime.now()
                formatted_time = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("insert into commande (temps_com,idresto,email) values (%s,%s,%s) returning idcommande ",(formatted_time,code,session['client']))
                result1 = cur.fetchall()
                cur.execute("select idresto,nom_plat,prix from offre ")
                result = cur.fetchall()
                for i in result:
                    if i[0] == int(code):
                        nom_plat = request.form.get(i[1])
                        if (nom_plat):
                            count = count + int(nom_plat) * int(i.prix)
                            cur.execute("insert into choisir values(%s,%s,%s)",(result1[0],i.nom_plat,nom_plat))
                return render_template('order.html',count = count)

@app.route('/livreur')
def livreur():
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("select nom_l,prenom_l from livreur where matricule= %s",(session['livreur'],))
            resultat = cur.fetchone()
            nom, prenom = resultat
    current_time = datetime.now().time()
    current_time = current_time.replace(microsecond=0)
    atime = time(12, 0)
    atime = atime.replace(microsecond=0)
    btime = time(17,0)
    btime = btime.replace(microsecond=0)
    if current_time < atime:
        message = "早上好"
    elif current_time < btime and current_time > atime :
        message = "下午好"
    else:
        message = "晚上好"
    return render_template('livreur.html',nom = nom,prenom = prenom,message = message,current_time = current_time)

@app.route('/logoutliv',methods=['POST'])
def logoutliv():
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("update livreur set etat = 'OFF' where matricule = %s",(session['livreur'],))
    session.pop('livreur', None)
    return redirect(url_for('accueil'))

@app.route('/logoutcli',methods=['POST'])
def logoutcli():
    session.pop('client', None)
    return redirect(url_for('accueil'))

@app.route('/logoutrestaurant', methods=['POST'])
def logoutrestaurant():
    session.pop('restaurant', None)
    return redirect(url_for('accueil'))


@app.route('/livreurchoisir',methods = ['GET','POST'])
def livreurchoisir():
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet")
            cur.execute("select ville_insee from travaille where matricule = %s",(session['livreur'],))
            livreur_adresse = cur.fetchone()
            cur.execute("select idcommande,idresto,email from commande natural join restaurant where temps_fin is NULL and idcommande not in (select idcommande from livrer) and ville_insee = %s",(livreur_adresse.ville_insee,))
            result = cur.fetchall()
            return render_template('livreurchoisir.html',result = result)

@app.route('/livreurcommande/<int:idcommande>',methods = ['GET','POST'])
def livreurcommande(idcommande):
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet")
            cur.execute("insert into livrer values(%s,%s)",(session['livreur'],idcommande))
            cur.execute("update livreur set etat = 'Livrer' where matricule = %s",(session['livreur'],))
            cur.execute("select adresse from client natural join commande where idcommande = %s",(idcommande,))
            result = cur.fetchone()
            cur.execute("select adresse_resto from restaurant natural join commande where idcommande = %s",(idcommande,))
            result1 = cur.fetchone()
            return render_template('livreurcommande.html',idcommande = idcommande,result = result,result1 = result1)

@app.route('/enfinlivrer',methods = ['GET','POST'])
def enfinlivrer():
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet")
            current_datetime = datetime.now()
            formatted_time = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("update commande set temps_fin = %s where idcommande = %s",(formatted_time,request.form.get('idcommande')))
            cur.execute("update livreur set etat = 'ON' where matricule = %s",(session['livreur'],))
            return redirect(url_for('livreur'))

@app.route('/livreur/choisirville',methods = ['GET','POST'])
def choisirville():
    if (request.method=='POST'):
        ville = request.form['ville']
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("set search_path to projet ")
                cur.execute("update travaille set ville_insee = %s where matricule = %s",(ville,session['livreur'],))
        return redirect(url_for('choisirville'))
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("select insee,nom from ville where insee not in (select ville_insee from travaille where matricule = %s)",(session['livreur'],))
            resultat = cur.fetchall()
    return render_template('choisirville.html', message = resultat)

@app.route("/accueilrestaurant",methods=['GET','POST'])
def accueilrestaurant():
    if (request.method == 'POST'):
        try:
            idresto = request.form['idresto']
            mdp = request.form['password']
            with db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("set search_path to projet ")
                    cur.execute("select mdp from restaur where idresto = %s",(idresto,))
                    resultat = cur.fetchone()
            if resultat is not None:
                a = resultat[0]
                if check_password_hash(a,mdp) :
                    session['restaurant'] = idresto
                    return redirect(url_for('restaur'))
                else :
                    return render_template('accueilrestaurant.html',message = "验证失败")
            else :
                return render_template('accueilrestaurant.html',message = "验证失败")
        except Exception as e :
            return render_template('accueilrestaurant.html',message = "验证失败")
    return render_template('accueilrestaurant.html',message = None)

@app.route("/restaur")
def restaur():
    idresto = session.get('restaurant')
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("select nom_resto from restaurant where idresto = %s",(idresto,))
            resultat = cur.fetchone()
            nom = resultat[0]
    current_time = datetime.now().time()
    current_time = current_time.replace(microsecond=0)
    atime = time(12, 0)
    atime = atime.replace(microsecond=0)
    btime = time(17,0)
    btime = btime.replace(microsecond=0)
    if current_time < atime:
        message = "早上好"
    elif current_time < btime and current_time > atime :
        message = "下午好"
    else:
        message = "晚上好"
    return render_template('restaur.html',nom = nom, message = message,current_time = current_time)

@app.route('/commanderesto',methods = ['GET','POST'])
def commanderesto():
    info_resto = session['restaurant']
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute("select idcommande,nom_plat,quantite from commande natural join choisir  where temps_fin is NULL and idresto = %s",(info_resto,))
            result = cur.fetchall()
            return render_template('commanderesto.html',result = result)


@app.route('/restaur/restaurantprofil')
def restaurantprofil():
    return render_template('restaurantprofil.html')

@app.route('/inforesto',methods = ['GET','POST'])
def inforesto():
    result = None
    if (request.method == 'POST'):
        nom_change = request.form.get('nom')
        text_change = request.form.get('text')
        nom_change = nom_change.replace("'","")
        with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("set search_path to projet ")
                cur.execute("update restaurant set {} = %s where idresto = %s"
                            .format(nom_change), (text_change, session['restaurant']))
                result = True
                return render_template('inforesto.html', result=result)
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute(
                "select nom_resto,adresse_resto,horaire_fer,horaire_ouv,specialite,tel_resto,ville_insee from restaurant where idresto = %s",
                (session['restaurant'], ))
            infos = cur.fetchone()
    return render_template('inforesto.html', result=result, infos=infos)


@app.route("/restaur/restaurantprofil/Changeroffre",methods = ['GET','POST'])
def Changeroffre():
    result = None
    message = None
    if (request.method == 'POST'):
      try:
        nom_plat = request.form.get('nom_plat')
        prix = request.form.get('prix')
        text_change = request.form.get('text')
        if prix is not None:
            with db.connect() as conn:
             with conn.cursor() as cur:
                cur.execute("set search_path to projet ")
                cur.execute("update offre set prix = %s where nom_plat = %s and idresto = %s "
                            ,(text_change,nom_plat, session['restaurant']))
                result = True
                return render_template('Changeroffre.html', result=result)
        elif nom_plat is not None and prix is None:
         with db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute("set search_path to projet ")
                cur.execute("update offre set nom_plat = %s where nom_plat = %s and idresto = %s "
                            ,(text_change,nom_plat,session['restaurant']))
                result = True
                return render_template('Changeroffre.html', result=result)
      except Exception as e :
          message = "Le plat n'exist pas !"
    with db.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("set search_path to projet ")
            cur.execute(
                "select idresto,nom_plat,prix from offre where idresto = %s",
                (session['restaurant'], ))
            offre = cur.fetchall()
    return render_template('Changeroffre.html', result=result, infos=offre,message =message)



if __name__ == '__main__':
    app.run()
