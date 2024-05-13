import os
import re
import torch
from tqdm import tqdm
from torch.utils.data import Dataset, DataLoader
from transformers import BertForSequenceClassification, BertTokenizer, AdamW
from sklearn.metrics import accuracy_score, recall_score, f1_score, classification_report

# 載入BERT斷詞器
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

# 定義文本分類數據集
class CustomDataset(Dataset):
    def __init__(self, file_paths, labels):
        self.file_paths = file_paths
        self.labels = labels

    def __len__(self):
        return len(self.file_paths)

    def __getitem__(self, idx):
        file_path = self.file_paths[idx]
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return {'text': text, 'label': self.labels[idx]}

# 資料夾路徑和類別
categories = ['Abuse', 'Drug', 'Sex_assault', 'Economic_assault', 'Others']

# 收集所有文本檔案路徑和對應標籤
labels = []
file_paths = []

for i, category in enumerate(categories):
    category_folder_path = os.path.join(category)
    file_names = sorted(os.listdir(category_folder_path), key=lambda x: int(re.findall(r'\d+', x)[0]))
    
    # 選取前 60% 的檔案
    num_files_to_use = int(0.6 * len(file_names))
    selected_file_names = file_names[:num_files_to_use]
    
    for file_name in selected_file_names:
        file_paths.append(os.path.join(category_folder_path, file_name))
        labels.append(i)

train_dataset = CustomDataset(file_paths, labels)

# 使用BertForSequenceClassification模型
model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=len(categories))

# 定義訓練參數
optimizer = AdamW(model.parameters(), lr=3e-5, weight_decay=0.01)
num_epochs = 3

accumulation_steps = 3  # 梯度累積的步數
for epoch in range(num_epochs):
    model.train()
    for batch_idx, batch in enumerate(tqdm(DataLoader(train_dataset, batch_size=16, shuffle=True), desc=f'Epoch {epoch + 1}/{num_epochs}')):
        optimizer.zero_grad()
        inputs = tokenizer(batch['text'], return_tensors='pt', padding=True, truncation=True)
        labels = torch.tensor(batch['label']).clone().detach()
        outputs = model(**inputs, labels=labels)
        loss = outputs.loss
        loss = loss / accumulation_steps  # 梯度累積
        loss.backward()
        
        if (batch_idx + 1) % accumulation_steps == 0:
            optimizer.step()
print("訓練完畢")

output_folder = 'C:/Users/88690/Desktop/ClassfyModel'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 訓練完畢後，保存模型
model.save_pretrained(output_folder)

# ========================================== 評估↓ ==========================================

for i, category in enumerate(categories):
    category_folder_path = os.path.join(category)
    file_names = sorted(os.listdir(category_folder_path), key=lambda x: int(re.findall(r'\d+', x)[0]))
    
    # 選取後 40% 的檔案
    num_files_to_use = int(0.4 * len(file_names))
    selected_file_names = file_names[-num_files_to_use:]
    
    for file_name in selected_file_names:
        file_paths.append(os.path.join(category_folder_path, file_name))
        labels.append(i)

val_dataset = CustomDataset(file_paths, labels)

# 載入已保存的模型
loaded_model = BertForSequenceClassification.from_pretrained('C:/Users/88690/Desktop/ClassfyModel', num_labels=len(categories))
print("載入完成")

# 評估模型
loaded_model.eval()
all_predictions = []
all_labels = []

with torch.no_grad():
    for batch in tqdm(DataLoader(val_dataset, batch_size=32, shuffle=False), desc='Evaluating'):
        inputs = tokenizer(batch['text'], return_tensors='pt', padding=True, truncation=True)
        labels = torch.tensor(batch['label'], dtype=torch.long)
        outputs = loaded_model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=1).cpu().numpy()
        all_predictions.extend(predictions)
        all_labels.extend(labels.numpy())

# 計算評估指標
accuracy = accuracy_score(all_labels, all_predictions)
recall = recall_score(all_labels, all_predictions, average='weighted')
f1 = f1_score(all_labels, all_predictions, average='weighted')

# 打印評估指標
print(f'Accuracy: {accuracy:.4f}')
print(f'Recall: {recall:.4f}')
print(f'F1 Score: {f1:.4f}')

# 打印分類報告
report = classification_report(all_labels, all_predictions, target_names=categories)
print('Classification Report:\n', report)