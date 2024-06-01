import io 
import os
import re
import operator
import pandas as pd
from datetime import datetime
from google.cloud import vision
from google_vision_ai import VisionAI
from google_vision_ai import(
    prepare_image_local,
    prepare_image_web,
    draw_boundary,
    draw_boundary_normalized
)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials/client_file_vision-telegram-bot.json'


# Instantiates a client
client = vision.ImageAnnotatorClient()

image_file_path = 'images/image3.jpeg'
image = prepare_image_local(image_file_path)

va = VisionAI(client,image)

texts = va.text_detection()


possible_sustrings= {'TRI':0, 'DAU':0, 'BAG':0, 'RIZ':0}


result = texts[0].description.split('\n')

print("Google cloud api result :",result)

temp = []
temp2 = []

for i in range(len(result)):
    temp1= {'TRI':0, 'DAU':0, 'BAG':0, 'RIZ':0}
    for j in temp1:
        if j in result[i]:
            temp1[j] +=1 
    temp = [{result[i]:temp1}]+temp
    temp2 = [result[i]]+temp2


r = {}

for i in range(len(temp)):
    # print(temp[i][temp2[i]])
    # print(temp2[i])
    # print(type(temp2[i]))
    # print(sum(temp[i][temp2[i]].values()))
    r[temp2[i]] = sum(temp[i][temp2[i]].values())
# print(r)


# print(max(r.items(), key=operator.itemgetter(1))[0])

sandwich_name = max(r.items(), key=operator.itemgetter(1))[0]

quant = [a for a in result if 'x' in a or 'X' in a or '×' in a]
# print(quant)
quantity = int(re.search('[Xx×]\s?(\d+)(?:.(?![Xx]))*$',\
                    quant[0]).group(1))
# print(quantity)
# print(type(quantity))

dlc = [a for a in result if 'DLC' in a or 'Dic' in a]

# print(dlc)


# searching string
match_str = re.search(r'\d{2}[/]\d{2}[/]\d{2}', dlc[0])
# print(match_str)
# print(match_str.group())

# computed date
# feeding format
dlc_res = datetime.strptime(match_str.group(), "%d/%m/%y").date()

# print(dlc_res)
# print(type(dlc_res))

# printing result
# print("Computed date : " + str(dlc_res))

# print(sandwich_name)
# print(quantity)
# print(dlc_res)

df = pd.DataFrame({
    'Nom_du_sandwich' : [sandwich_name],
    'Quantite' : [quantity],
    'dlc' : [dlc_res]
})

print('\n')
print(df)