from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy import func,update

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/Hp/Desktop/arackiralamasitesi/mydb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

db = SQLAlchemy(app)

@app.route("/",methods=["GET","POST"])
def index():
    page = request.args.get('page', 1, type=int)
    index = db.session.query(Arac,Musteri,Fatura).select_from(Arac).join(Musteri).join(Fatura).paginate(page=page, per_page=4)
    return render_template("index.html",index=index)
    
@app.route("/search",methods=["GET","POST"])
def search():
    if request.method == 'POST':
        page = request.args.get('page', 1, type=int)
        form = request.form
        search_value = form["search"]
        search = "%{}%".format(search_value)
        results = db.session.query(Arac,Musteri,Fatura).select_from(Arac).join(Musteri).join(Fatura) \
        .filter(Musteri.musteri_isim.like(search)).paginate(page=page, per_page=4)
        return render_template("index.html",index=results)
    else:
        return redirect(url_for('index'))

@app.route("/sirket")
def sirket():
    index = db.session.query(Sirket,Arac).select_from(Sirket).join(Arac).all() 
    return render_template('sirket.html',index=index)

@app.route("/musteri/<int:musteri_id>")
def musteri(musteri_id):
    index = db.session.query(Musteri,Fatura,Arac).select_from(Musteri).join(Arac).join(Fatura) \
    .filter(Musteri.musteri_id==musteri_id).all() 
    return render_template('musteri.html',index=index,musteri_id=musteri_id)

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method == 'POST':
        if(db.session.query(Sirket).filter(Sirket.sirket_id==1)==None):
            newSirket = Sirket(sirket_id=1,sirket_isim="SH",adres="Mersin")
            db.session.add(newSirket)
            db.session.flush()
        
        musteri_isim = request.form.get("musteri_isim")
        telefon = request.form.get("telefon")
        marka = request.form.get("marka")
        model = request.form.get("model")
        gunluk_kira_fiyati = request.form.get("gunluk_kira_fiyati")
        kira_gun = request.form.get("kira_gun")
        #print(request.form)
        carpim=int(gunluk_kira_fiyati)*int(kira_gun)

        newMusteri = Musteri(musteri_isim=musteri_isim,telefon=telefon)
        db.session.add(newMusteri)
        db.session.flush()
        newArac = Arac(marka = marka,model= model,gunluk_kira_fiyati=gunluk_kira_fiyati,m_id=newMusteri.musteri_id,s_id=1)
        db.session.add(newArac)
        db.session.flush()
        newFatura = Fatura(kira_gun=kira_gun,toplam_odeme=carpim,m_id=newMusteri.musteri_id)
        db.session.add(newFatura)

        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('add.html')


@app.route("/update/<int:arac_id>/<int:fatura_id>/<int:musteri_id>",methods=["GET","POST"])
def update(arac_id,fatura_id,musteri_id):
    if request.method == 'POST':
        yeniisim = request.form.get("yeniisim")
        yenitelefon = request.form.get("yenitelefon")
        yenimarka = request.form.get("yenimarka")
        yenimodel = request.form.get("yenimodel")
        yenikirafiyati = request.form.get("yenikirafiyati")
        yenikiragun = request.form.get("yenikiragun")
        carpim=int(yenikirafiyati)*int(yenikiragun)

        db.session.query(Musteri)\
        .filter(Musteri.musteri_id==musteri_id)\
        .update({Musteri.musteri_isim: yeniisim})
        db.session.flush()

        db.session.query(Musteri)\
        .filter(Musteri.musteri_id==musteri_id)\
        .update({Musteri.telefon: yenitelefon})
        db.session.flush()
        
        db.session.query(Arac)\
        .filter(Arac.arac_id==arac_id)\
        .update({Arac.marka: yenimarka})
        db.session.flush()

        db.session.query(Arac)\
        .filter(Arac.arac_id==arac_id)\
        .update({Arac.model: yenimodel})
        db.session.flush()

        db.session.query(Arac)\
        .filter(Arac.arac_id==arac_id)\
        .update({Arac.gunluk_kira_fiyati: yenikirafiyati})
        db.session.flush()

        db.session.query(Fatura)\
        .filter(Fatura.fatura_id==fatura_id)\
        .update({Fatura.kira_gun: yenikiragun})
        db.session.flush()

        db.session.query(Fatura)\
        .filter(Fatura.fatura_id==fatura_id)\
        .update({Fatura.toplam_odeme: carpim})
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html',arac_id=arac_id,fatura_id=fatura_id,musteri_id=musteri_id)


@app.route("/delete/<int:arac_id>/<int:fatura_id>/<int:musteri_id>",methods=["GET","POST"])
def delete(arac_id,fatura_id,musteri_id):
    
    db.session.query(Arac)\
    .filter(Arac.arac_id==arac_id)\
    .delete(synchronize_session='evaluate')
    db.session.flush()

    db.session.query(Fatura)\
    .filter(Fatura.fatura_id==fatura_id)\
    .delete(synchronize_session='evaluate')
    db.session.flush()

    db.session.query(Musteri)\
    .filter(Musteri.musteri_id==musteri_id)\
    .delete(synchronize_session='evaluate')
    db.session.commit()
        
    return redirect(url_for('index'))

class Arac(db.Model):
    arac_id = db.Column(db.Integer, primary_key=True)
    marka = db.Column(db.String(30))
    model = db.Column(db.String(40))
    gunluk_kira_fiyati = db.Column(db.Integer)
    m_id = db.Column(db.Integer, db.ForeignKey("musteri.musteri_id"))
    s_id = db.Column(db.Integer, db.ForeignKey("sirket.sirket_id"))

class Musteri(db.Model):
    musteri_id = db.Column(db.Integer, primary_key=True)
    musteri_isim = db.Column(db.String(70))
    telefon = db.Column(db.String(11))
    araclar = db.relationship("Arac",backref='musteri', lazy='select')
    faturalar = db.relationship("Fatura", backref='musteri', lazy='select')

class Sirket(db.Model):
    sirket_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    sirket_isim = db.Column(db.String())
    adres = db.Column(db.String())
    araclar = db.relationship("Arac", backref='sirket', lazy='select')
    

class Fatura(db.Model):
    fatura_id = db.Column(db.Integer, primary_key=True)
    kira_gun = db.Column(db.Integer)
    toplam_odeme = db.Column(db.Integer)
    m_id = db.Column(db.Integer, db.ForeignKey("musteri.musteri_id"))

if __name__=="__main__":
    db.create_all()
    app.run(debug=True)

