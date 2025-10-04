# 🚀 Solana Token Scanner

Flask veebirakendus Solana token-ite varajaste tehingute skannimiseks.

## ✨ Funktsionaalsus

- **Veebi Liides**: Responsiivne disain kõigile seadmetele (330px+)
- **Token Analüüs**: Otsib varajasemad tehingud igale Solana token-ile  
- **JSON Eksport**: Automaatne allalaadimise link timestampi-ga
- **Tume Teema**: Kaasaegne gradient disain

## 🚀 GitHub Actions Deployment

Projekt kasutab automaatset deployment-i läbi GitHub Actions.

### Setup & Deploy

1. **Kood GitHub-i:**
```bash
git init
git add .
git commit -m "Flask token scanner"
git remote add origin https://github.com/KASUTAJANIMI/REPO-NIMI.git
git push -u origin main
```

2. **Automaatne Deployment:**
   - GitHub Actions käivitub automaatselt iga `git push main` korral
   - Testib rakendust (import kontrollid)
   - Buildib aplikatsiooni
   - Deployb automaatselt

3. **Live URL:** `https://KASUTAJANIMI.github.io/REPO-NIMI`

### Workflow Funktsioonid

✅ **Automaatne testimine** - iga push korral  
✅ **Python 3.9 keskkond** - standardiseeritud  
✅ **Sõltuvuste installimine** - requirements.txt  
✅ **Build validation** - aplikatsiooni kompileerimine  
✅ **Deployment** - ainult main branch

## 💻 Kohalik Arendus

```bash
# Kloneeri projekt
git clone https://github.com/KASUTAJANIMI/REPO-NIMI.git
cd REPO-NIMI

# Paigalda sõltuvused
pip install -r requirements.txt

# Käivita rakendus
python app.py

# Ava brauser: http://localhost:5001
```

## � Kasutamine

1. **Sisesta Token Address** (nt: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` - USDC)
2. **Vali tehingute arv** (1-1000)
3. **Kliki "Start Scanning"**
4. **Lae alla JSON** automaatse lingi kaudu

## 🔧 API Endpointid

- `GET /` - Peamine liides
- `POST /process` - Token analüüsi töötlemine
- `GET /download/<filename>` - Konkreetse faili allalaadimine
- `GET /latest` - Viimase tulemuse allalaadimine

## 📁 Projekti Struktuur

```
scan/
├── app.py                           # Flask rakendus
├── requirements.txt                 # Python sõltuvused  
├── .github/workflows/deploy.yml     # GitHub Actions deployment
├── templates/index.html             # Veebi liides
├── downloads/                       # JSON failid
└── README.md                        # Dokumentatsioon
```

## 🔄 Workflow Käivitamine

```bash
# Muuda kood
git add .
git commit -m "Update feature"
git push origin main

# GitHub Actions käivitub automaatselt:
# 1. Testib koodi
# 2. Buildib aplikatsiooni  
# 3. Deployb live-i
```

## � Workflow Status

Vaata deployment staatust:
- **GitHub repo** → **Actions** tab
- **Badge:** ![Deploy Status](https://github.com/nst2pl5/scan/workflows/Deploy%20Flask%20App/badge.svg)

## 🎨 Tehnilised Detailid

- **Flask 2.3.3** - Python web framework
- **Responsive CSS** - Mobile-first disain
- **Vanilla JavaScript** - Interaktiivsus
- **GitHub Actions** - Automaatne CI/CD

### Responsive Breakpointid
- **Mobiil**: ≤480px (min 330px)
- **Tahvel**: 481-1024px
- **Desktop**: 1025-1260px

---

**Automaatne deployment GitHub Actions abil 🚀**
