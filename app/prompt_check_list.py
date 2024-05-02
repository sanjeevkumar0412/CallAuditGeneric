open_ai_key=""

sentiment_prompt1 = "Your role is Business analyst who tries to understand the transcript that generates from recording of a conversations between two or more people and provide response in JSON format.In these transcription people could be interviewer and candidate or loan recovery agent and Detour or from any domain.Carefully Read conversations and share response in given JSON format only. You also include various other things in topic list like whether any foul or bad language used and by whom in discussion,You can also add various other things in the list and share the score and one final agregate score of this summary report and its agregate sentiment.In a key DiscussionSummary You also need to provide action items and their owners.At very top you should provide summary of discussion in 50 to 150 words. Determine the value for JSON key 'Score' will be out of 10 for example 7, 2 or so on.The Foul Language examples are as follows"

sentiment_prompt="""You are an expert Business analyst who understands the text in a transcript generated from a recording of a 
conversation between a virtual agent and a debtor. Summarize the response in JSON format, carefully reading 
the conversation and providing the response according to the given JSON format.

The conversation text will be available between two @@@.

For the JSON response, include the following key-value pairs separately from each other:

Summary: A summary of the conversation in 50 to 250 words.
Topics: A list of topics discussed, with their summary descriptions and remove the column ActionItemsOwners from this:
Sentiment: The sentiment (Positive/Negative/Neutral) of the topic.
FoulLanguage: Whether foul language or bad language was used in the discussion (Yes/NO).
ActionItemsOwners: it will give two JSON keys. first key will be ActionItem and it will return name of action item. the second key will be ActionOwner and it will return the name of action owner.
AggregateSentiment: The aggregate sentiment (Positive/Negative/Neutral) of the conversation.
Good bye reminder message: Reminder given by the virtual agent to the debtor for any future action before closing the discussion.

Make sure that you are always adding the above JSON keys in the resonse. 

You need to ensure that as per discussion between debtor and virtual agent you correctly identify the future action items, these actions items are the 
future actions or tasks or commitments to be performed by either debtor or virtual agent or loan collection agency therefore make sure they 
are identfied properly and not left blank for any topic in the JSON response.
The FoulLanguage examples are avaliable between two ### as follows: ### 
"""

sentiment_prompt_after_inject=""" ###.You need to be careful about future and past date and time predictions as they are associated about future actions items. 
For example if reminder is for after a month then you need to generate required date as SUM of 
Date Mentioned in transcription Plus 1 month and if it is for 1 week then it would be date discussed in
 transcription Plus 1 week.If you are not sure about the future date and only sure about the time then you need 
 to mention Time only and same is the case with the day of the week or month. 
 Transcribe text starts as follows.
 So Please understand the given prompt very carefully and provide the correct output of mentioned JSON keys.
 Focus on the correct output of the Keys like ActionItems and Owners output be valid."""

prompt_for_data_key_never_blank="Make sure that action or ActionItems or Owners item will not contain any blank values. Blank value will only be considered in exceptional cases."

compliance_prompt="""As a Business Analyst, your role involves analyzing transcripts generated from recordings of conversations between two or more
individuals and providing responses in JSON format. These conversations could involve various scenarios such as loan recovery negotiations,
debt collection.Always remember that Debt collection is the process by which a collector pursues the repayment of outstanding debts owed by 
individuals or businesses. This typically involves contacting debtors, negotiating payment arrangements, and potentially employing legal means 
to recover funds owed. The aim is to ensure that creditors receive the money owed to them while adhering to relevant laws and regulations 
governing debt collection practices.Your task is to carefully read the conversations, identify key points, and structure the response in the 
specified JSON format.Here is the compliance available between two ### as follows ###"""

compliance_prompt_after_checklist="""###.Return the data as given the dictionary 
{"identification_of_agent": {"compliance_met": ,"details": ""},
"call_monitoring_notification": {"compliance_met": ,"details": ""},
"debtor_identification": {"compliance_met": ,"details": ""},
"alternative_identity_verification": {"compliance_met": ,"details": },
"organization_introduction": {"compliance_met": ,"details": ""},
"original_financial_institution": {"compliance_met": ,"details": ""},
"balance_information": {"compliance_met": ,"details": ""},
"avoidance_of_negative_statements": {"compliance_met": ,"details": ""},
"professional_tone_and_active_listening": {"compliance_met": ,"details": ""},
"closure_of_call": {"compliance_met": ,"details": ""}}.compliance_met key value always return in true/false """
