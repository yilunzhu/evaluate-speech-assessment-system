import io, os, sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-corpus', help='either l2arctic or sell')
args = parser.parse_args()

if args.corpus == 'l2arctic':
    speaker_path = 'data' + os.sep + 'l2arctic'
elif args.corpus == 'sell':
    speaker_path = 'data' + os.sep + 'sell'
else:
    raise ValueError("Wrong corpus. Try 'l2arctic' or 'sell'.")


trans = {}
for speaker in os.listdir(speaker_path):
    trans[speaker] = []
    trans_path = speaker_path + os.sep + speaker + os.sep + 'transcript'
    for filename in os.listdir(trans_path):
        if filename.endswith('txt'):
            with open(trans_path + os.sep + filename) as f:
                lines = f.readlines()
                for line in lines:
                    if args.corpus == "sell":
                        line = " ".join(line.strip().split()[1:])
                    trans[speaker].append(line.strip().lower())

for speaker in os.listdir(speaker_path):
    trans_path = speaker_path + os.sep + speaker + os.sep + 'transcript'
    speaker_count = 0
    with open(trans_path + os.sep + 'gold_transcript', 'w') as f:
        for line in trans[speaker]:
            f.write(f'{line}\n')
            speaker_count += 1
            if speaker_count == 100:
                break

print('Done')
