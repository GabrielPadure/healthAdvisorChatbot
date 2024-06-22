import json
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizerFast, BertForQuestionAnswering, AdamW, get_linear_schedule_with_warmup


class QADataset(Dataset):
    def __init__(self, json_file, tokenizer, max_len=512):
        self.data = []
        self.tokenizer = tokenizer
        self.max_len = max_len

        print(f"Loading data from {json_file}")
        with open(json_file, 'r') as f:
            self.raw_data = json.load(f)

        for item in self.raw_data:
            question = item['question']
            context = item['context']
            answer = item['answer']
            start_idx = context.find(answer)
            end_idx = start_idx + len(answer)

            if start_idx == -1 or end_idx == -1:
                continue  # skip if the answer is not found in the context

            encoded_dict = tokenizer.encode_plus(
                question,
                context,
                max_length=max_len,
                truncation=True,
                padding='max_length',
                return_tensors='pt',
                return_offsets_mapping=True
            )

            # Find start and end token positions using offset_mapping
            offsets = encoded_dict['offset_mapping'].squeeze().tolist()
            start_positions = None
            end_positions = None

            for idx, (start, end) in enumerate(offsets):
                if start <= start_idx < end:
                    start_positions = idx
                if start < end_idx <= end:
                    end_positions = idx
                    break

            if start_positions is None or end_positions is None:
                continue  # skip if positions are not found

            self.data.append({
                "input_ids": encoded_dict['input_ids'].flatten(),
                "attention_mask": encoded_dict['attention_mask'].flatten(),
                "start_positions": torch.tensor(start_positions, dtype=torch.long),
                "end_positions": torch.tensor(end_positions, dtype=torch.long)
            })

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        return {
            "input_ids": item['input_ids'],
            "attention_mask": item['attention_mask'],
            "start_positions": item['start_positions'],
            "end_positions": item['end_positions']
        }


def train(model, dataset, device, epochs=3, batch_size=8):
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=2e-5)
    total_steps = len(dataloader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    model.train()
    for epoch in range(epochs):
        print(f"Starting epoch {epoch + 1}/{epochs}")
        total_loss = 0
        for batch in dataloader:
            model.zero_grad()

            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            start_positions = batch['start_positions'].to(device)
            end_positions = batch['end_positions'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask, start_positions=start_positions, end_positions=end_positions)
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()
            optimizer.step()
            scheduler.step()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch + 1}/{epochs} completed with average loss: {avg_loss}")

    print("Training completed")
    return model


def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    model = BertForQuestionAnswering.from_pretrained('bert-base-uncased').to(device)

    dataset_files = [
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Fitness.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Med&Suppl.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/MentalHealth.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Nutr&Diet.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithContext/Symp&Cond.json'
    ]

    datasets = [QADataset(file, tokenizer) for file in dataset_files]

    for dataset in datasets:
        print(f"Training on dataset: {dataset_files[datasets.index(dataset)]}")
        model = train(model, dataset, device)

    model.save_pretrained('fine_tuned_bert_qa')
    tokenizer.save_pretrained('fine_tuned_bert_qa')
    print("Model and tokenizer saved")


if __name__ == '__main__':
    main()
