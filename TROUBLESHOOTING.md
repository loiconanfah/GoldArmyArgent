# 🔧 Dépannage - Problème d'Installation Python 3.14

## ⚠️ Problème Identifié

Python 3.14.3 a été installé mais **pip est corrompu**. Toutes les commandes pip échouent avec:
```
distlib\__init__.py: return self.finder.get_bytes(self)
```

## 🎯 Solutions Possibles

### Solution 1: Installer Python 3.12 (RECOMMANDÉ) ✅

Python 3.14 est une version très récente (février 2026) et peut avoir des problèmes de compatibilité.

**Étapes:**

1. **Désinstaller Python 3.14**
   ```powershell
   py uninstall PythonCore\3.14
   ```

2. **Installer Python 3.12 (version stable)**
   ```powershell
   py install 3.12
   ```

3. **Vérifier l'installation**
   ```powershell
   py -3.12 --version
   py -3.12 -m pip --version
   ```

4. **Installer les dépendances**
   ```powershell
   cd d:\GoldArmyArgent
   py -3.12 -m pip install -r requirements-minimal.txt
   ```

### Solution 2: Réinstaller pip pour Python 3.14

Si tu veux garder Python 3.14:

```powershell
# Télécharger get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Réinstaller pip
python get-pip.py

# Tester
python -m pip --version
```

### Solution 3: Utiliser un environnement virtuel

```powershell
cd d:\GoldArmyArgent

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements-minimal.txt
```

### Solution 4: Installation manuelle des packages

Si pip ne fonctionne toujours pas, télécharge les wheels (.whl) manuellement depuis PyPI.

## 🚀 Commandes Rapides

### Vérifier les versions Python installées
```powershell
py list
```

### Utiliser une version spécifique
```powershell
py -3.12 <commande>
```

### Lancer GoldArmyArgent avec une version spécifique
```powershell
py -3.12 main.py test-ollama
py -3.12 main.py interactive
```

## 📋 Checklist de Dépannage

- [ ] Vérifier les versions Python installées (`py list`)
- [ ] Désinstaller Python 3.14 si nécessaire
- [ ] Installer Python 3.12 (version stable)
- [ ] Vérifier que pip fonctionne
- [ ] Installer les dépendances minimales
- [ ] Tester Ollama
- [ ] Lancer le mode interactif

## 💡 Recommandation

**Je recommande la Solution 1** : installer Python 3.12 qui est une version stable et bien testée.

Python 3.14 est sorti il y a quelques jours seulement et peut avoir des bugs avec pip et certaines bibliothèques.

## 🆘 Besoin d'Aide ?

Si les solutions ci-dessus ne fonctionnent pas:
1. Partage le résultat de `py list`
2. Partage le résultat de `python --version`
3. On trouvera une autre solution ensemble !
