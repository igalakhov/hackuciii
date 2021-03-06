from pytube import YouTube
import nltk
import re
import heapq
import indicoio
import json
import numpy

video_info = {}
indicoio.config.api_key = '1d39c9a3ab4e5550c7b88a66aaac025a'

url = "https://www.youtube.com/watch?v=dfsUz2O2jww"
yt = YouTube(url)

video_info["timestamped"] = []

# get the audio file
a = yt.captions.get_by_language_code('en')
caps = a.generate_srt_captions()
caps = caps.split("\n\n")
caps = [i.split("\n") for i in caps]
text = ""

for i in caps:
    for j in i[2:]:
        text += j
        video_info["timestamped"].append([
            i[1].split(" --> ")[0],
            i[1].split(" --> ")[1],
            " ".join(i[2:])
        ])

text = re.sub(r"<[^>]*>", " ", text)
text = re.sub(r'\s+', ' ', text)
text = text.replace("...", ".")
text = text.replace("…", "")
text = text.replace(".", ". ")
text = re.sub(r'\s+', ' ', text)
sentences = nltk.sent_tokenize(text)
video_info["full_transcript"] = text
stopwords = nltk.corpus.stopwords.words('english')

word_frequencies = {}
for word in nltk.word_tokenize(text):
    if word not in stopwords:
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1


maximum_frequency = max(word_frequencies.values())
for word in word_frequencies.keys():
    word_frequencies[word] = (word_frequencies[word]/maximum_frequency)

sentence_scores = {}
for sent in sentences:
    for word in nltk.word_tokenize(sent.lower()):
        if word in word_frequencies.keys():
            if len(sent.split(' ')) < 30:
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]

summary_sentences = heapq.nlargest(len(sentences), sentence_scores, key=sentence_scores.get)

video_info["summary_variable"] = summary_sentences

politicalValues = indicoio.political(text)
personalityValues = indicoio.personality(text)
emotionValues = indicoio.emotion(text)

video_info["political"] = politicalValues
video_info["personality"] = personalityValues
video_info["emotion"] = emotionValues
video_info["url"] = url


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)


print(json.dumps(video_info, cls=MyEncoder))
