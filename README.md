# Pipeline Diarisation Audio CNews - Hackathon Humanités Numériques 2025

<img src="https://www.chartes.psl.eu/sites/default/files/public/media/image/2025-03/logo-chartes-psl-coul.png" width="150" height="150" alt="École Nationale des Chartes" /> <img src="https://www.chartes.psl.eu/sites/default/files/public/styles/default_medium/public/media/image/2026-01/capture-d-ecran-2026-01-05-111216.png?itok=wkzcucFh" width="150" height="150" alt="Infovox Tracker" />

## Introduction

Ce projet s'inscrit dans le cadre de l'édition **2025 du hackathon du Master Humanités Numériques** de l'**École Nationale des Chartes**.

**Porteur du projet** : Baptiste Queuche  
**Contributeurs** : Damien Conceicao, Maria Kirbasova, Marisol de Nazelle, Garance Raynaud, Manon Remot

---

## Contexte et objectif

**Objectif** : Détecter le **temps de parole exact** des personnes qui interviennent sur **CNews**, en identifiant précisément leur identité.

La pipeline traite des enregistrements audio de CNews pour :
- Découper les fichiers longs en segments gérables
- Identifier automatiquement les locuteurs (diarisation)
- Relier chaque segment de parole à une personne identifiée via des fichiers de présence

---

## Pipeline d'exécution

Les trois scripts s'exécutent **dans cet ordre précis** :

```bash
python decoupe_5_min.py
python pyannote_ssh.py  
python correspondance_speaker_ssh.py
```


---

## Convention de nommage des fichiers d'entrée

### Fichiers audio (enregistrements CNews)

```
cson_YYYY-MM-DD_HH-MM-SS.mp3
cson_YYYY-MM-DD_HH-MM-SS.wav
```

*La date/heure dans le nom sert au recalage temporel*

### Fichiers de présence (identités)

```
people-YYYY-MM-DD.csv
```

*Format : colonnes `ID`, `Debut`, `Fin` (format datetime)*

---

## `decoupe_5_min.py` – Découpage automatique

**Rôle** : Découpe chaque enregistrement CNews en segments de 5 minutes.

**Ce qu'il fait** :

- Parcourt tous les fichiers audio du dossier d'entrée
- Crée des segments de 5 min
- Note pour chaque segment : fichier d'origine + heure début/fin

**Entrée** : Fichiers `cson_*.mp3/wav`
**Sortie** : Segments + fichier récapitulatif

---

## `pyannote_ssh.py` – Détection des locuteurs

**Rôle** : Applique la diarisation automatique sur chaque segment de 5 min avec `pyannote.audio`.

**Ce qu'il fait** :

- Détecte les différentes voix et leurs périodes de parole
- Extrait les embeddings (empreintes vocales) de chaque locuteur
- Sauvegarde les résultats par segment

**Techno** : `pyannote/speaker-diarization-3.1` (GPU si disponible)

---

## `correspondance_speaker_ssh.py` – Identification finale

**Rôle** : Recalage temporel + matching avec les personnes connues.

**Ce qu'il fait** :

1. **Recalage** : timestamps relatifs → timeline absolue (via nom des fichiers)
2. **Matching** : associe chaque parole au `Speaker_ID` via fichier `people-YYYY-MM-DD.csv`
3. **Lissage** : résolution des doublons (garde le locuteur le plus parlant)
4. **Agrégation** : embeddings par personne + fichier récapitulatif global

**Sortie finale** :

- `df_total.csv` : tous les segments avec `start`, `end`, `Speaker_ID`, `embeddings`
- `known_embeddings.json` : embeddings par personne identifiée
- `unknown_embeddings.json` : embeddings des inconnus


## `knn.py` - Identification des locuteurs inconnus
`#To do`

---

## Résultat final

La pipeline produit un fichier CSV global prêt pour l'analyse du temps de parole par personne sur CNews :


| start | end | duration | Speaker_ID | embeddings |
| :-- | :-- | :-- | :-- | :-- |
| 2025-01-15 14:23:10 | 2025-01-15 14:23:45 | 35.2s | PERS001 | [0.12, -0.45, ...] |


---

## Prérequis

voir fichier `requirements.txt`

**Token HuggingFace requis** (dans `pyannote_ssh.py`).

---

# Merci aux sponsors et partenaires du Hackaton

<img src="https://www.chartes.psl.eu/sites/default/files/public/styles/default_medium/public/media/image/2025-12/lostma-logo.png?itok=uonkzN2o" width="150" height="150" alt="LostMA" /> <img src="https://www.chartes.psl.eu/sites/default/files/public/styles/default_medium/public/media/image/2025-02/20250115_logo_cartadata.png?itok=TglHc6uf" width="150" height="150" alt="CartaData" /> 

<img src="https://www.chartes.psl.eu/sites/default/files/public/media/image/2025-03/logo-chartes-psl-coul.png" width="150" height="150" alt="École Nationale des Chartes" />  <img src="https://www.chartes.psl.eu/sites/default/files/public/styles/default_medium/public/media/image/2024-04/anr-logo-2021-sigle.jpg?itok=IVl3qIRF" width="150" height="150" alt="ANR" />  <img src="https://www.chartes.psl.eu/sites/default/files/public/styles/default_medium/public/media/image/2025-12/erc_logo.png?itok=Hy50DUHn" width="150" height="150" alt="European council" /> 



