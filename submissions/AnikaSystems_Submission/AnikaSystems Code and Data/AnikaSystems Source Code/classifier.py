# classifier.py - Run the trained classification model on an array of clauses and return array of predictions.
#
# Install pytorch with:
# pip3 install torch==1.6.0+cu101 torchvision==0.7.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html
#
# BERT fine tuner:
# https://github.com/prateekjoshi565/Fine-Tuning-BERT/blob/master/Fine_Tuning_BERT_for_Spam_Classification.ipynb
#
# Pytorch NN layers:
# https://pytorch.org/docs/stable/nn.html
#
# About layers:
# https://cs231n.github.io/convolutional-networks/#fc

import torch
import numpy as np
import pandas as pd

# Model class
from transformers import AutoModel, BertTokenizerFast
import torch.nn as nn


# Load pretrained BERT model.
bert = AutoModel.from_pretrained('bert-base-uncased')


class BERT_Arch(nn.Module):

    def __init__(self, bert):
      
      super(BERT_Arch, self).__init__()

      self.bert = bert 
      
      # dropout layer
      self.dropout = nn.Dropout(0.1)
      
      # relu activation function
      self.relu =  nn.ReLU()

      # dense layer 1
      self.fc1 = nn.Linear(768,512)
      
      # dense layer 2 (Output layer)
      self.fc2 = nn.Linear(512,2)

      #softmax activation function
      self.softmax = nn.LogSoftmax(dim=1)

    #define the forward pass
    def forward(self, sent_id, mask):

      #pass the inputs to the model  
      _, cls_hs = self.bert(sent_id, attention_mask=mask)
      
      x = self.fc1(cls_hs)

      x = self.relu(x)

      x = self.dropout(x)

      # output layer
      x = self.fc2(x)
      
      # apply softmax activation
      x = self.softmax(x)

      return x


def classify_clauses(vclauses=[]):
    # Classify each clause as acceptable or unacceptable.
    vres = []

    # Load model
    path = '..\\AnikaSystems Compiled Models\\saved_weights.pt'
    # model = torch.load(path)
    model = BERT_Arch(bert)
    device = torch.device("cpu")
    model = model.to(device)
    model.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
    model.eval()

    # Parse input data
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    df = pd.read_csv(".\\data\\AI_ML_Challenge_Training_Data_Set_1_v1.csv")
    df['label'].value_counts(normalize = True)
    tokens_test = tokenizer.batch_encode_plus(
        vclauses,
        max_length = 25,
        pad_to_max_length=True,
        truncation=True,
        return_token_type_ids=False
    )
    test_seq = torch.tensor(tokens_test['input_ids'])
    test_mask = torch.tensor(tokens_test['attention_mask'])

    # Get predictions from model
    with torch.no_grad():
        preds = model(test_seq.to(device), test_mask.to(device))

        # Calculate confidence probabilities with softmax and topk.
        vconf = torch.nn.functional.softmax(preds)
        vconf = torch.topk(vconf, 1)
        preds = preds.detach().cpu().numpy()    

    # Use argmax to calculate output from tensors.
    preds = np.argmax(preds, axis = 1)

    # Construct final output structure.
    i = 0
    for vclause in vclauses:
        vaccept = int(preds[i])
        if vaccept == 1: vaccept = False 
        else: vaccept = True
        
        vres.append({
            "text": vclause,
            "acceptable": vaccept,
            "confidence": round(float(vconf[0][i]), 2)
        })
        i += 1

    return vres


if __name__ == "__main__":
    # DEBUG
    # classify_clauses()

    vpreds = classify_clauses([
        # 1
        'COMPANY warrants that the SOFTWARE will, for a period of sixty (60) days from the date of your receipt, perform substantially in accordance with SOFTWARE written materials accompanying it. Except as just stated,The parties acknowledge that the Software is provided "AS IS," and may not be functional on every machine or in every environment.  Except as set forth herein,  COMPANY DISCLAIMS ALL WARRANTIES RELATING TO THE SOFTWARE, EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTIES AGAINST INFRINGEMENT OF THIRD PARTY RIGHTS, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.',

        # 0
        'Hello world',

        # 0
        '"Services " means any services that the Licensor provides to the User, or has an obligation to provide to the User, under this Agreement;'
    ])

    import json
    print(json.dumps(vpreds, indent=4))

    import pdf_to_string
    veula = ".\\data\\kofax-end-user-licencing-agreement.pdf"
    vclauses = pdf_to_string.pdf_to_string(veula)
    vpreds = classify_clauses(vclauses["clauses"])
    open("predictions.json", "w+").write(json.dumps(vpreds, indent=4))