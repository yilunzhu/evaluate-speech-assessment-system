corpus=$1

if [ "$corpus" == "sell" ]; then
	data_dir=data/sell
	pred_dir=out/sell
elif [ "$corpus" == "l2arctic" ]; then
	data_dir=data/l2arctic
	pred_dir=out/l2arctic
else
	echo "Invalid argument."
	exit 1
fi

for dir in $data_dir/*; do
	speaker="$(cut -d'/' -f3 <<< "$dir")"
	echo $speaker
	wer $data_dir/$speaker/transcript/gold_transcript $pred_dir/pred_transcripts/$speaker
	# > $pred_dir/wer/$speaker.wer
done

# wer ref hyp