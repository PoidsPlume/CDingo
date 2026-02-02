from pyannote.audio import Pipeline
import os
from pydub import AudioSegment
from pathlib import Path
import glob
import json
import pandas as pd
import torch

os.environ["HF_TOKEN"] = ""

segments_list = glob.glob('chunk_5_min/*.wav')

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=os.environ["HF_TOKEN"])

if torch.cuda.is_available():
    pipeline.to(torch.device("cuda"))
    print("GPU activé")
else:
    print("GPU non disponible, utilisation du CPU")

diarizations = []
for segment in segments_list:
    print(segment)
    diarization = pipeline(segment)

    speakers_list = []
    embeddings = []

    for s, speaker in enumerate(diarization.speaker_diarization.labels()):
        embeddings.append(diarization.speaker_embeddings[s])
        speakers_list.append(speaker)

    csv_bname = Path(segment).stem + ".csv"
    csv_path = os.path.join("embeddings", csv_bname)
    
    d = {'Speaker': speakers_list, 'Embeddings': embeddings}
    embed_df = pd.DataFrame(data=d)

    embed_df.to_csv(csv_path, sep=';')

    basename = Path(segment).stem
    diarizations.append(diarization)
    segments = []
    for seg, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
        segments.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "speaker": speaker,
            "duration": round(seg.end - seg.start, 2)
        })
    fname = Path(segment).stem + ".json"
    json_path = os.path.join("pred_5m", fname)
    with open(json_path, 'w') as f:
        json.dump(segments, f, indent=2)
