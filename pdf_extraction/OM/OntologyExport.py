# coding: utf-8

import json
import copy
single_button = {
                    "textButton": {
                        "text": "question",
                        "onClick": {
                            "action": {
                                "actionMethodName": "Question key"
                            }
                        }
                    }
                }

hangout_template = {
    "newmessage": True,
    "cards": [
        {
            "sections": [
                {
                    "widgets": [
                        {
                            "image": {},
                            "buttons": []
                        }
                    ]
                }
            ]
        }
    ]
}

faq_template =  {
      "alternateAnswers": [
        [
          {
            "channel": "hangoutchat",
            "text": "var message = print(JSON.stringify(message));",
            "type": "advance"
          }
        ]
      ],
      "alternateQuestions": [],
      "answer": [
        {
          "channel": "default",
          "text": "sample answer",
          "type": "basic"
        }
      ],
      "question": "List Indian states",
      "responseType": "message",
      "tags": [],
      "terms": [
        "Tiny"
      ]
    }

hangout_small_template =           {
            "channel": "hangoutchat",
            "text": "var message = print(JSON.stringify(message));",
            "type": "advance"
          }

class OntologyExport():

    def __init__(self):
        self.input_file_path = "om_input.json"

    def convert_hangout_template(self, data):
        converted_list = []
        for que_key, payload in data.items():
            ms = copy.deepcopy(hangout_template)
            result = dict()
            bubbles = list()
            for image_url in payload["answer"]:
                image_bubble = copy.deepcopy(hangout_template)
                image_bubble["cards"][0]["sections"][0]["widgets"][0]["image"]["imageUrl"] = image_url
                bubbles.append(copy.deepcopy(image_bubble))

            child_present = False
            for child in payload.get("children",[]):
                child_present = True
                single_button["textButton"]["text"] = data[child]["question"]
                single_button["textButton"]["onClick"]["action"]["actionMethodName"] = child
                ms["cards"][0]["sections"][0]["widgets"][0]["buttons"].append(copy.deepcopy(single_button))

            if child_present:
                bubbles.append(copy.deepcopy(ms))
            result["temp_question"] = que_key
            result["messages"] = copy.deepcopy(bubbles)
            converted_list.append(copy.deepcopy(result))
        return converted_list

    def create_ontology_import(self, data):
        faq_list = []
        for item in data:
            question = item.pop("temp_question")

            message_list = list()
            for message in item.get("messages"):
                small_message = copy.deepcopy(hangout_small_template)
                message_text = "var message = "+json.dumps(message)+" \n "+"print(JSON.stringify(message));"
                small_message["text"] = message_text
                message_list.append(copy.deepcopy(small_message))

            faq_template["alternateAnswers"][0] = copy.deepcopy(message_list)
            faq_template["question"] = question
            faq_list.append(copy.deepcopy(faq_template))
        return {"faqs":faq_list, "synonyms": {}}

    def convert_driver(self):
        with open(self.input_file_path) as json_file:
            data = json.load(json_file)
            hangout_data =  self.convert_hangout_template(data)

            return self.create_ontology_import(hangout_data)

if __name__ == "__main__":
    ontology_export = OntologyExport()
    data = ontology_export.convert_driver()

    with open('ontology_export.json', 'w') as outfile:
        json.dump(data, outfile)
