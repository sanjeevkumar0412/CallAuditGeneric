import os
os.environ["OPENAI_API_KEY"] = ""
import openai

class SentimentAnalysis:
    def get_sentiment(text):
        prompt = f"The following text expresses a sentiment: '{text}' The sentiment of this text is:"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": ""}
            ],
            temperature=0.5,
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


if __name__ == "__main__":
    text = input("Enter the text to analyze: ")
    sentiment = SentimentAnalysis.get_sentiment(text)
    print(f"The sentiment of the text is {sentiment}")