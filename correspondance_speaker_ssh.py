import pandas as pd
import json
from datetime import datetime
from collections import OrderedDict
import hashlib

fichier_compil = pd.read_csv("chunk_5_min/recap_segments.csv")

fichier_compil['segment_file'] = fichier_compil['segment_file'].apply(
    lambda x: x.split('.')[0] + ".json"
)

def correct_time_stamp(df, dossier, folder_embed):
    liste_df = []

    for index, row in df.iterrows():
        nom_fichier = row['original_file'].replace(".mp3", ".json")
        date_obj = nom_fichier.replace("cson_", "").replace(".json", "")
        date_obj = datetime.strptime(date_obj, "%Y-%m-%d_%H-%M-%S")
        nom_fichier = row['segment_file'].replace(".mp3", ".json")

        # Charger le fichier JSON
        with open(f"{dossier}/{nom_fichier}", 'r') as f:
            data = json.load(f)

        # Charger fichier des embeddings
        df_embeds = pd.read_csv(f"{folder_embed}/{nom_fichier.replace('.json', '.csv')}", sep=";")

        heures, minutes, secondes = map(int, row['start_time'].split()[2].split(':'))
        début = heures * 3600 + minutes * 60 + secondes

        for segment in data:
            segment['start'] += début
            segment['start'] = date_obj + pd.to_timedelta(segment['start'], unit='s')
            segment['end'] += début
            segment['end'] = date_obj + pd.to_timedelta(segment['end'], unit='s')
            segment['middle'] = segment['start'] + pd.to_timedelta(segment['duration'] / 2, unit='s')

            matching_embedding = df_embeds.loc[df_embeds['Speaker'] == segment['speaker'], 'Embeddings']
            if not matching_embedding.empty:
                segment['embeddings'] = matching_embedding.values[0]
            else:
                segment['embeddings'] = None

            segment['unique_id'] = get_unique_id(segment['speaker'], nom_fichier)

        liste_df.append(pd.DataFrame(data))

    return liste_df

def give_name_to_speaker(df):
    date_obj = df['middle'].iloc[0].date()
    csv_name = f"1fps/people-{date_obj.strftime('%Y-%m-%d')}.csv"
    id_list = []

    people_df = pd.read_csv(csv_name)

    for col in ["Debut", "Fin"]:
        people_df[col] = pd.to_datetime(people_df[col])

    for index, row in df.iterrows():
        middle_time = row['middle']
        matched = people_df[(people_df['Debut'] <= middle_time) & (people_df['Fin'] >= middle_time)]
        if not matched.empty:
            id_list.append(matched['ID'].values[0])
        else:
            id_list.append("Unknown")
    df['Speaker_ID'] = id_list

    return df

def get_dict_id(df):
    df = df[df['Speaker_ID'] != "Unknown"].copy()
    result_dict = {}

    for speaker_id in df['Speaker_ID'].unique():
        speakers_list = df[df["Speaker_ID"] == speaker_id]['speaker'].unique().tolist()
        result_dict[speaker_id] = speakers_list

    return result_dict

def smooth_speaker(df, dict_id):
    for key, values in dict_id.items():
        if len(values) > 1:
            time_dict = {}
            for value in values:
                tmp_df = df[(df["speaker"] == value) & (df['Speaker_ID'] == key)].copy()
                duration = tmp_df["duration"].sum()
                time_dict[value] = duration
            sorted_dict = sorted(time_dict.items(), key=lambda kv: kv[1])
            sorted_dict = OrderedDict(sorted_dict)

            for ktr in list(sorted_dict.keys())[:-1]:
                df.loc[(df['speaker'] == ktr) & (df['Speaker_ID'] == key), 'Speaker_ID'] = 'Unknown'

    speaker_dict = get_dict_id(df)

    for key, speaker_list in speaker_dict.items():
        for speaker in speaker_list:
            # Mise à jour de Speaker_ID pour les lignes correspondantes
            df.loc[df['speaker'] == speaker, 'Speaker_ID'] = key

    return df

def get_unique_id(speaker_id, csv_name):
    hash_object = hashlib.sha256(f"{csv_name}_{speaker_id}".encode())
    unique_id = hash_object.hexdigest()
    return unique_id[:10]


def get_embed_per_id(df):
    result_dict = {}
    for speaker_id in df[df['Speaker_ID'] != "Unknown"]['Speaker_ID'].unique():
        tmp_df = df[df['Speaker_ID'] == speaker_id]
        embeddings_list = list(set(tmp_df['embeddings'].tolist()))
        result_dict[str(speaker_id)] = embeddings_list

    with open("json_embed_id/known_embeddings.json", 'w') as f:
        json.dump(result_dict, f, indent=4)

    result_un_dict = {}
    for speaker_id in df[df['Speaker_ID'] == "Unknown"]['unique_id'].unique():
        tmp_df = df[df['unique_id'] == speaker_id]
        embeddings_list = list(set(tmp_df['embeddings'].tolist()))
        result_un_dict[str(speaker_id)] = embeddings_list

    with open("json_embed_id/unknown_embeddings.json", 'w') as f:
        json.dump(result_un_dict, f, indent=4)

df = correct_time_stamp(fichier_compil, "pred_5m", "embeddings")
df_named = give_name_to_speaker(df[0])
dict_id = get_dict_id(df_named)
clean_dict = smooth_speaker(df_named, dict_id)

list_df = []

for df_i in df:
    df_named = give_name_to_speaker(df_i)
    dict_id = get_dict_id(df_named)
    clean_dict = smooth_speaker(df_named, dict_id)
    list_df.append(clean_dict)

df_concat = pd.concat(list_df, ignore_index=True)

d = {'start': df_concat['start'], 'end': df_concat['end'], 'duration': df_concat['duration'], 'Speaker_ID': df_concat['Speaker_ID'], 'unique_id': df_concat['unique_id'], 'embeddings': df_concat['embeddings']}
df_concat = pd.DataFrame(data=d)
df_concat.to_csv("df_emission/df_total.csv", index=False)



get_embed_per_id(df_concat)
print(type(df_concat['embeddings'][0]))