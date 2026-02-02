import os
from pathlib import Path
import pandas as pd
import librosa
import soundfile as sf

# 🔹 Paramètres
input_dir = Path("1fps")       # dossier contenant MP3/WAV
output_dir = Path("chunk_5_min")     # dossier où stocker les segments
output_dir.mkdir(exist_ok=True)
segment_sec = 5 * 60  

summary = []

# 🔹 Boucle sur tous les fichiers audio
for audio_file in input_dir.glob("*"):
    base_name = audio_file.stem
    suffix = audio_file.suffix.lower()
    
    if suffix not in [".wav", ".mp3"]:
        print(f"Format non supporté : {audio_file.name}, skip")
        continue

    print(f"🔄 Chargement : {audio_file.name} ...")
    
    # Lecture
    y, sr = librosa.load(audio_file, sr=None, mono=True)  # sr=None = garde fréquence originale
    duration = librosa.get_duration(y=y, sr=sr)
    
    start = 0
    segment_index = 1

    while start < duration:
        end = min(start + segment_sec, duration)
        y_segment = y[int(start*sr):int(end*sr)]

        segment_name = f"{base_name}_{segment_index:02d}.wav"
        segment_path = output_dir / segment_name
        sf.write(segment_path, y_segment, sr)

        # Ajouter au récap
        summary.append({
            "original_file": audio_file.name,
            "segment_file": segment_name,
            "start_time": str(pd.to_timedelta(start, unit='s')),
            "end_time": str(pd.to_timedelta(end, unit='s'))
        })

        start += segment_sec
        segment_index += 1

# 🔹 Sauvegarde CSV
df_summary = pd.DataFrame(summary)
df_summary.to_csv(output_dir / "recap_segments.csv", index=False)

print(f"Découpage terminé ! {len(summary)} segments créés.")
print(f"Tableau récapitulatif : {output_dir / 'recap_segments.csv'}")