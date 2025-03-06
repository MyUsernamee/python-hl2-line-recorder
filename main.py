import os
import numpy
import sounddevice as sd
import argparse
from tqdm import tqdm
import wave
import re
from time import sleep

# Function to record audio and save it to a given path
def record_audio(path, duration=10, fs=44100):
	print("Recording...")
	if not os.path.exists(os.path.split(path)[0]):
		os.makedirs(os.path.split(path)[0])
	audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16')

	for i in tqdm(range(int(fs * duration / 100))):
		sleep(1.0 / fs * 100)

	with wave.open(path, 'wb') as wf:
		wf.setnchannels(2)
		wf.setsampwidth(2)
		wf.setframerate(fs)
		wf.writeframes(audio_data.tobytes())

	print(f"Recording saved as {path}")

# Function to play audio from a given relative path
def play_audio(path):
	with wave.open(path, 'rb') as wf:
		fs = wf.getframerate()
		channels = wf.getnchannels()
		audio_data = wf.readframes(wf.getnframes())
		audio_array = numpy.frombuffer(audio_data, dtype='int16')

	print("Playing audio...")
	sd.play(audio_array, fs * channels)
	sd.wait()
	print("Playback finished.")

# Function to get the length of the audio clip in seconds
def get_audio_length(path):
	with wave.open(path, 'rb') as wf:
		frames = wf.getnframes()
		rate = wf.getframerate()
		length = frames / float(rate)
	print(f"Audio length: {length} seconds")
	return length

# Returns a list of tuples where the first is the path voice line and the second.
def load_close_captions(path):
	
	with open(path, "rb") as f:
		contents = f.read().decode('utf-16')
		captions = re.findall(r"\"([^\"]*)\"\s\"([^\"]*)\"", contents)
		for i, value in enumerate(captions):
			captions[i] = (captions[i][0].replace(".", "/"), captions[i][1])
		return captions

def main():
	 
	parser = argparse.ArgumentParser("recorder")
	parser.add_argument("line_filter", help="This is a regex filter that is used for your voice lines", type=str)	
	args = parser.parse_args()
	

	captions = load_close_captions("./closecaption_english.txt")
	lines = []
	  
	for caption in captions:
		if re.findall(args.line_filter, caption[0]):
			lines.append(caption)

	for (file, line) in lines:
		try:

			path = "sound/vo/" + file + ".wav"

			if not os.path.exists("./lines/" + path):
				continue

			print(line)
			print("Press r to record, p to play the recording, o to play the original file, and d for done and move to next")

			option = input(":")

			while option != "d":
				if option == "r":
					record_audio("./recorded/" + path, get_audio_length("./lines/" + path))
				if option == "o":
					play_audio("./lines/" + path)
				option = input(":")
				

		except KeyboardInterrupt as e:

			exit(0)
			

def make_data_set():

	parser = argparse.ArgumentParser("recorder")
	parser.add_argument("line_filter", help="This is a regex filter that is used for your voice lines", type=str)	
	parser.add_argument("name", type=str)
	args = parser.parse_args()
	
	captions = load_close_captions("./closecaption_english.txt")
	lines = []
	  
	for caption in captions:
		if re.findall(args.line_filter, caption[0]):
			lines.append(caption)


	out = ""

	for (file, line) in lines:
		try:

			path = "sound/vo/" + file + ".wav"

			if not os.path.exists("./lines/" + path) or len(line.strip()) == 0:
				continue

			print(line)
			
			out = out + "\n" + f"{os.path.abspath('lines/' + path)}|{args.name}|en|{re.sub(r'<[^>]*>', '', line)}"

		except KeyboardInterrupt as e:

			exit(0)
	
	print(out)

	f = open("dataset.txt", "wb")
	f.write(out.encode('utf-8'))
	f.close()
	
main()