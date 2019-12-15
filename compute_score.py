import io, os, sys
import json
import argparse
from collections import defaultdict


parser = argparse.ArgumentParser()
parser.add_argument('-corpus', help='either l2arctic or sell')
args = parser.parse_args()
if args.corpus == 'l2arctic':
    speaker_path = 'data' + os.sep + 'l2arctic'
elif args.corpus == 'sell':
    speaker_path = 'data' + os.sep + 'sell'
elif args.corpus == 'native':
    speaker_path = 'data' + os.sep + 'native'
else:
    raise ValueError("Wrong corpus. Try 'l2arctic' or 'sell'.")


for speaker in os.listdir(speaker_path):
    speaker_score = defaultdict(lambda : {})
    count = 0
    word_count = 0
    speaker_acc = 0.0
    speaker_flu = 0.0
    speaker_comp = 0.0
    speaker_ss = 0.0
    log_dir = speaker_path + os.sep + speaker + os.sep + 'asa.log'
    if args.corpus == 'l2arctic':
        log_dir = speaker_path + os.sep + speaker + os.sep + 'asa.log'
    with open(log_dir, encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            feedback = json.loads(line)
            speaker_score[f'{count}']["PronAccuracy"] = feedback["PronAccuracy"]
            if feedback["PronFluency"] == -1:
                feedback["PronFluency"] = 0.0
            speaker_score[f'{count}']["PronFluency"] = feedback["PronFluency"]
            speaker_score[f'{count}']["PronCompletion"] = feedback["PronCompletion"]
            speaker_score[f'{count}']["word_count"] = len(feedback['Words'])
            word_count += len(feedback['Words'])

            count += 1

        for single_score in speaker_score.values():
            speaker_acc += single_score['PronAccuracy'] * (single_score['word_count'] / word_count)
            speaker_flu += single_score['PronFluency'] * (single_score['word_count'] / word_count)
            speaker_comp += single_score['PronCompletion'] * (single_score['word_count'] / word_count)

        speaker_flu = 100 * speaker_flu
        speaker_comp = 100 * speaker_comp
        speaker_ss = 0.5 * speaker_acc + 0.45 * speaker_flu + 0.05 * speaker_comp
        print(f"o Speaker {speaker}, PronAccuracy=%.2f, PronFluency=%.2f, PronCompletion=%.2f, SuggestedScore=%.2f"
              % (speaker_acc, speaker_flu, speaker_comp, speaker_ss))
