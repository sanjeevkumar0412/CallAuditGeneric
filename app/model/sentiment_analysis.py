import os,json
os.environ["OPENAI_API_KEY"] = "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"
import openai

class SentimentAnalysis:
    _instance = None

    def __init__(self, path):
        self.path = path

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def get_sentiment(self,text):
        prompt = f"The following text expresses a sentiment: '{text}' The sentiment of this text is:"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": ""}
            ],
            temperature=0,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n"]
        )
        sentiment = response['choices'][0]['message']['content'].strip()

        if "positive" in sentiment.lower():
            score = 1
        elif "negative" in sentiment.lower():
            score = -1
        else:
            score = 0
        data ={'sentiment':sentiment,'score':score}
        return data

    def transcribe_data_from_database(self):
        #Databse Query here
        # table_name = 'AudioRecord'
        # column_value = 'filename'

        with open(self.path, 'r') as file:# Read text data from the file
            texts = file.readlines()
            # print(texts)
        results = [{"text": text.strip(), "sentiment": self.get_sentiment(text.strip())['sentiment'],
                    "score": self.get_sentiment(text.strip())['score']} for text in texts]

        return results

if __name__ == "__main__":
    path="D:/Cogent-AI/app/chunk_6.txt"

    # Single Input Entry

    input_text = input("Please enter input for Sentiment Analysis:")
    sentiment_instance=SentimentAnalysis.get_instance()
    sentiment = sentiment_instance.get_sentiment(input_text)
    print("Single Sentiment",sentiment)

    # For FIle or DB

    # analyzer = SentimentAnalysis(path)
    # sentiment_results = analyzer.transcribe_data_from_database()
    # sentiment_list_data= json.dumps(sentiment_results, indent=2)
    # print("Result>>>>>>",sentiment_list_data)