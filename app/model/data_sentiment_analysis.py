import os
# os.environ["OPENAI_API_KEY"] = ""
# import openai

# class SentimentAnalysis:
#     def get_sentiment(text):
#         prompt = f"The following text expresses a sentiment: '{text}' The sentiment of this text is:"
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": ""}
#             ],
#             temperature=0.5,
#             max_tokens=1,
#             top_p=1,
#             frequency_penalty=0,
#             presence_penalty=0,
#             stop=["\n"]
#         )
#         sentiment = response['choices'][0]['message']['content'].strip()
#         return sentiment
#
#

# if __name__ == "__main__":
#     text = input("Enter the text to analyze: ")
#     sentiment = SentimentAnalysis.get_sentiment(text)
#     print(f"The sentiment of the text is {sentiment}")
#
# data=[('you went well or not well. So the technical needs to be improved? Every everywhere the technical', 'Neutral', 0), ("needs to be improved. Why? So because I don't know I mean I mean I gave my 100% today but", 'fr', 0), ("there was still a question that I didn't knew. Okay but but but you have good confidence right your", 'Neutral', 0), ('presentation skill is good. Thank you sir. Your presentation is also good right but wherever', 'Positive', 1), ('you have to do the improvement definitely you have to do the improvement. Sure sir. It cannot be', 'Enc', 0), ('ignored. So this is from our side and by the way you perform well if I say the example of today', 'Positive', 1), ('you you perform good right and anything I think from an adversary if you wanted to give any', 'Positive', 1)]
# d={k:v for k, v,c in data}
# print(d)
# for x in data:
#     print(x)
# {x:x for x in data}


import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)
def test(msg):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": msg,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

print(test("I like this food.It's awesome"))