# -*- coding: utf-8 -*-
import os
import io
import sys
import base64
import json
import hashlib, hmac, time
from datetime import datetime
from collections import defaultdict
from nltk import word_tokenize
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.soe.v20180724 import soe_client, models
import librosa


def wav2base64(file):
    if corpus == 'l2arctic':
        y, sr = librosa.load(file, sr=16000)
        s = base64.b64encode(y)

    else:
        s = base64.b64encode(open(file, "rb").read())
    return s.decode('ascii')


def client(key_id, secret):
    try:
        cred = credential.Credential(key_id, secret)

        httpProfile = HttpProfile()
        httpProfile.endpoint = "soe.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        clientProfile.signMethod = "TC3-HMAC-SHA256"
        client = soe_client.SoeClient(cred, "na-ashburn", clientProfile)

        req = models.TransmitOralProcessWithInitRequest()

        speakers_score = {}
        speakers_score["total_word_count"] = 0
        total_count = 0
        for speaker in os.listdir(IN_DIR):
            # if speaker in ['THV','TLV','TNI','TXHC', 'YBAA', 'YDCK','YKWK','ZHAA']:
            speaker_score = defaultdict(lambda: defaultdict(int))
            speaker_score["speaker_word_count"] = 0
            speaker_path = IN_DIR + os.sep + speaker + os.sep + "wav"
            print(f"Start speaker {speaker}")
            count = 0
            for filename in os.listdir(speaker_path):
                file_path = speaker_path + os.sep + filename
                trans_path = IN_DIR + os.sep + speaker + os.sep + "transcript" + os.sep + "gold_transcript"
                transcripts = []
                with open(trans_path) as f:
                    for line in f.readlines():
                        if corpus == 'native':
                            line = line.split('\t')[1]
                        transcripts.append(line.strip())
                if filename.endswith(".wav"):
                    sessionid = f"{speaker}_{count}"
                    wav = wav2base64(file_path)
                    text = transcripts[count]
                    word_count = len(word_tokenize(text))
                    params = rf'{{"SeqId":1,"IsEnd":1,"VoiceFileType":2,"VoiceEncodeType":1,"UserVoiceData":"{wav}","SessionId":"{sessionid}","RefText":"{text}","WorkMode":1,"EvalMode":2,"ScoreCoeff":3.5}}'
                    req.from_json_string(params)

                    resp = client.TransmitOralProcessWithInit(req)
                    feedback = resp.to_json_string()
                    with open(IN_DIR + os.sep + speaker + os.sep + "asa_recent.log", "a") as f:
                        f.write(f"{feedback}\n")
                    feedback = json.loads(feedback)
                    #                         print(resp.to_json_string())
                    speaker_score[f"{speaker}_{count}"]["PronAccuracy"] = feedback["PronAccuracy"]

                    speaker_score[f"{speaker}_{count}"]["PronFluency"] = feedback["PronFluency"]
                    speaker_score[f"{speaker}_{count}"]["PronCompletion"] = feedback["PronCompletion"]
                    speaker_score[f"{speaker}_{count}"]["SuggestedScore"] = feedback["SuggestedScore"]
                    speaker_score[f"{speaker}_{count}"]["word_count"] = word_count
                    speaker_score["speaker_word_count"] += word_count
                    count += 1
                    total_count += 1
                    if count % 10 == 0:
                        print(f"speaker {speaker} {count} / 100")
                    if count == 100:
                        break

            print(f"Finished speaker {speaker}")
            speakers_score[speaker] = speaker_score
            speakers_score["total_word_count"] += speaker_score["speaker_word_count"]

    except TencentCloudSDKException as err:
        print(err)


if __name__ == '__main__':
	corpus = sys.argv[1]
	if corpus == "sell":
	    IN_DIR = ".." + os.sep + "data" + os.sep + "sell"
	    TRANS_DIR = ".." + os.sep + "out" + os.sep + "sell"
	elif corpus == "l2arctic":
	    IN_DIR = ".." + os.sep + "data" + os.sep + "l2arctic"
	    TRANS_DIR = ".." + os.sep + "out" + os.sep + "l2arctic"
	elif corpus == "native":
	    IN_DIR = ".." + os.sep + "data" + os.sep + "native"
	    TRANS_DIR = ".." + os.sep + "out" + os.sep + "l2arctic"
	else:
	    raise ValueError("Invalid argument. Please enter either 'sell' or 'l2arctic'.")

	key = sys.argv[2]
	secret = sys.argv[3]

    client(key, secret)
