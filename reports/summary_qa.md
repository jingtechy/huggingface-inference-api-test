# Question Answering Test Summary — 2025-08-23T12:52:44
## Summary Statistics
- **Total Tests**: 10
- **Average Exact Match**: 0.400
- **Average F1 Score**: 0.533

## Detailed Results
| Model | Task | Unanswerable | Input | Expected Answers | Output | Exact Match | F1 Score |
|---|---|---|---|---|---|---|---|
| deepset/roberta-base-squad2 | question_answering | False | Who&nbsp;identified&nbsp;gravity&nbsp;as&nbsp;a​force? | isaac&nbsp;newton,&nbsp;isaac&nbsp;newton,&nbsp;isaac​newton,&nbsp;isaac&nbsp;newton | Isaac&nbsp;Newton | 1.000 | 1.000 |
| deepset/roberta-base-squad2 | question_answering | False | The&nbsp;Amazon&nbsp;region&nbsp;is&nbsp;home​to&nbsp;how&nbsp;many&nbsp;species&nbsp;of​insect? | 2.5&nbsp;million,&nbsp;about&nbsp;2.5&nbsp;million,​2.5&nbsp;million | 2.5&nbsp;million | 1.000 | 1.000 |
| deepset/roberta-base-squad2 | question_answering | True | King&nbsp;Sigimund's&nbsp;Column&nbsp;is&nbsp;an​example&nbsp;of&nbsp;what&nbsp;kind&nbsp;of​attraction&nbsp;in&nbsp;UNESCO? |  | architectural | 0.000 | 0.000 |
| deepset/roberta-base-squad2 | question_answering | False | How&nbsp;is&nbsp;the&nbsp;prime&nbsp;number​p&nbsp;in&nbsp;Bertrand's&nbsp;postulate&nbsp;expressed​mathematically? | n&nbsp;<&nbsp;p&nbsp;<&nbsp;2n​−&nbsp;2,&nbsp;n&nbsp;<&nbsp;p​<&nbsp;2n&nbsp;−&nbsp;2,&nbsp;a​or&nbsp;μ,&nbsp;n&nbsp;<&nbsp;p​<&nbsp;2n&nbsp;−&nbsp;2,&nbsp;n​<&nbsp;p&nbsp;<&nbsp;2n&nbsp;−​2 | at&nbsp;least&nbsp;one&nbsp;prime&nbsp;number​p&nbsp;with&nbsp;n&nbsp;<&nbsp;p​<&nbsp;2n&nbsp;−&nbsp;2 | 0.000 | 0.533 |
| deepset/roberta-base-squad2 | question_answering | False | Can&nbsp;the&nbsp;President&nbsp;of&nbsp;the​Council&nbsp;vote&nbsp;on&nbsp;important&nbsp;matters​related&nbsp;to&nbsp;the&nbsp;European&nbsp;Central​Bank? | do&nbsp;not&nbsp;have&nbsp;voting&nbsp;rights,​not,&nbsp;not,&nbsp;not | do&nbsp;not&nbsp;have&nbsp;voting&nbsp;rights | 1.000 | 1.000 |
| deepset/roberta-base-squad2 | question_answering | False | Where&nbsp;was&nbsp;the&nbsp;Gate&nbsp;of​King&nbsp;Hugo? | tours,&nbsp;tours,&nbsp;tours | Huguon | 0.000 | 0.000 |
| deepset/roberta-base-squad2 | question_answering | False | Which&nbsp;tribes&nbsp;did&nbsp;Genghis&nbsp;Khan​unite? | mongol&nbsp;and&nbsp;turkic&nbsp;tribes,&nbsp;mongol​and&nbsp;turkic&nbsp;tribes,&nbsp;the&nbsp;mongol​and&nbsp;turkic&nbsp;tribes | Mongol&nbsp;and&nbsp;Turkic&nbsp;tribes&nbsp;of​the&nbsp;steppes | 0.000 | 0.800 |
| deepset/roberta-base-squad2 | question_answering | False | What&nbsp;group&nbsp;operates&nbsp;St&nbsp;Dominic's​College&nbsp;in&nbsp;Wanganui? | society&nbsp;of&nbsp;st&nbsp;pius&nbsp;x,​the&nbsp;society&nbsp;of&nbsp;st&nbsp;pius​x,&nbsp;catholic&nbsp;schismatic | Society&nbsp;of&nbsp;St&nbsp;Pius&nbsp;X | 1.000 | 1.000 |
| deepset/roberta-base-squad2 | question_answering | True | Besides&nbsp;the&nbsp;study&nbsp;of&nbsp;prime​numbers,&nbsp;what&nbsp;general&nbsp;theory&nbsp;was​considered&nbsp;the&nbsp;official&nbsp;example&nbsp;of​the&nbsp;military? |  | number&nbsp;theory | 0.000 | 0.000 |
| deepset/roberta-base-squad2 | question_answering | True | What&nbsp;did&nbsp;the&nbsp;agreement&nbsp;not​aim&nbsp;to&nbsp;do&nbsp;regarding&nbsp;Germany? |  | prevent&nbsp;Germany&nbsp;from&nbsp;re-establishing&nbsp;dominance​in&nbsp;the&nbsp;production&nbsp;of&nbsp;coal​and&nbsp;steel | 0.000 | 0.000 |
