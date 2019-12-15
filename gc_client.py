import io
import os
import argparse

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file("/mnt/c/Users/zhuda/Desktop/speech.json")


# def explicit():
#     from google.cloud import storage
#
#     # Explicitly use service account credentials by specifying the private key
#     # file.
#     storage_client = storage.Client.from_service_account_json(
#         "/mnt/c/Users/zhuda/Desktop/speech.json")
#
#     # Make an authenticated API request
#     buckets = list(storage_client.list_buckets())
#     print(buckets)
#
# explicit()


parser = argparse.ArgumentParser()
parser.add_argument('-corpus', help='either l2arctic or sell')
args = parser.parse_args()

if args.corpus == 'l2arctic':
    speaker_path = 'data' + os.sep + 'l2arctic'
elif args.corpus == 'sell':
    speaker_path = 'data' + os.sep + 'sell'
else:
    raise ValueError("Wrong corpus. Try 'l2arctic' or 'sell'.")

pred_trans_path = 'out' + os.sep + args.corpus + os.sep + 'pred_transcripts'

# Instantiates a client
client = speech.SpeechClient(credentials=credentials)

print('Start transcriting...')
speaker_count = 0
for speaker in os.listdir(speaker_path):
    speaker_trans = []
    trans_count = 0
    file_path = speaker_path + os.sep + speaker + os.sep + 'wav'
    for file in os.listdir(file_path):
        # Loads the audio into memory
        with io.open(file_path + os.sep + file, 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)

            config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                # sample_rate_hertz=16000,
                language_code='en-US')

            # Detects speech in the audio file
            response = client.recognize(config, audio)

            transcript = ""
            for result in response.results:
                # print('Transcript: {}'.format(result.alternatives[0].transcript))
                transcript += result.alternatives[0].transcript.strip().lower()
                transcript += " "
            speaker_trans.append(transcript.strip())
            trans_count += 1
            if trans_count % 50 == 0:
                print(f'speaker {speaker}, finished {trans_count}/100')
            if trans_count == 100:
                break
    with open(pred_trans_path + os.sep + speaker, 'w', encoding='utf8') as f:
        for line in speaker_trans:
            f.write(f'{line}\n')
    speaker_count += 1
    print(f'Finished speaker {speaker}')
print(f'finished trancripting.')
