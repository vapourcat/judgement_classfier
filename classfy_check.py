import re
import os
import jieba
import shutil
from transformers import BertTokenizer

# 載入BERT斷詞器
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

# 載入自定義詞典
jieba.load_userdict('dict.txt')

# 載入停用詞
with open('skip.txt', 'r', encoding='utf-8') as skip_file:
    stop_words = set(skip_file.read().splitlines())

folder_path = 'Others/'

# 使用for迴圈遍歷資料夾中的所有檔案
for file_name in sorted(os.listdir(folder_path), key=lambda x: int(re.findall(r'\d+', x)[0])):
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # 使用BERT斷詞器進行斷詞
    tokens = tokenizer.tokenize(text)

    # 使用中文斷詞工具進一步處理，略過停用詞和數字
    cut_result = [word for word in jieba.lcut("".join(tokens)) if word not in stop_words and not re.match('^\d+$', word)]
    print(f"\n斷詞完結果：\n{cut_result}\n")
    
    economic = ["經濟剝削","強盜","偷竊","詐欺","詐騙","洗錢","車手","恐嚇取財","金融"]
    sex = ["猥褻","強制性交","性交","性騷擾","性侵害","性剝削"]
    drug = ["毒品","藥事法","禁藥","安非他命"]
    abuse = ["虐待","家暴","對兒童犯傷害罪"]

    if any(keyword in cut_result for keyword in economic):
        category_folder = "Economic_assault"
        print(f"\n{file_name}分類結果："+"economic")
        corresponding_keywords = [keyword for keyword in cut_result if keyword in economic]
        print(f"對應的關鍵詞：\n{corresponding_keywords}")
        
    elif any(keyword in cut_result for keyword in abuse):
        category_folder = "Abuse"
        print(f"\n{file_name}分類結果："+"abuse")
        corresponding_keywords = [keyword for keyword in cut_result if keyword in abuse]
        print(f"對應的關鍵詞：\n{corresponding_keywords}")
        
    elif any(keyword in cut_result for keyword in sex):
        category_folder = "Sex_assault"
        print(f"\n{file_name}分類結果："+"sex")
        corresponding_keywords = [keyword for keyword in cut_result if keyword in sex]
        print(f"對應的關鍵詞：\n{corresponding_keywords}")
    
    elif any(keyword in cut_result for keyword in drug):
        category_folder = "Drug"
        print(f"\n{file_name}分類結果："+"drug")
        corresponding_keywords = [keyword for keyword in cut_result if keyword in drug]
        print(f"對應的關鍵詞：\n{corresponding_keywords}")
    
    else:
        category_folder = "Others"
        print(f"\n{file_name}分類結果："+"others")
        
    destination_path = os.path.join(category_folder, file_name)
    shutil.move(file_path, destination_path)
    print(f"Moved '{file_name}' to '{category_folder}' folder.")