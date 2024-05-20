import json
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import BertTokenizer, BertForQuestionAnswering, AdamW, get_linear_schedule_with_warmup


class QADataset(Dataset):
    def __init__(self, json_file, tokenizer, max_len=512):
        self.data = []
        self.tokenizer = tokenizer
        self.max_len = max_len

        print(f"Loading data from {json_file}")
        with open(json_file, 'r') as f:
            self.raw_data = json.load(f)

        for item in self.raw_data:
            context = item['answer']
            # Tokenize context to check its length
            encoded_context = tokenizer.encode(context)
            if len(encoded_context) > max_len:
                # Truncate context if it exceeds max length
                context = tokenizer.decode(encoded_context[:max_len], skip_special_tokens=True)
            self.data.append({
                "question": item['question'],
                "context": context,
                "label": item['label']
            })

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        encoding = self.tokenizer.encode_plus(
            item['question'], item['context'],
            max_length=self.max_len,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        # Adding dummy start and end positions for training
        start_positions = torch.tensor([0], dtype=torch.long)
        end_positions = torch.tensor([min(len(encoding['input_ids'][0]) - 1, self.max_len - 1)], dtype=torch.long)

        return encoding, start_positions, end_positions


def train(model, tokenizer, dataset, device, epochs=3, batch_size=8):
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = AdamW(model.parameters(), lr=2e-5)
    total_steps = len(dataloader) * epochs
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    model.train()
    for epoch in range(epochs):
        print(f"Starting epoch {epoch + 1}/{epochs}")
        for batch in dataloader:
            model.zero_grad()
            inputs, start_positions, end_positions = batch
            input_ids = inputs['input_ids'].squeeze().to(device)
            attention_mask = inputs['attention_mask'].squeeze().to(device)
            start_positions = start_positions.squeeze().to(device)
            end_positions = end_positions.squeeze().to(device)

            outputs = model(input_ids, attention_mask=attention_mask, start_positions=start_positions,
                            end_positions=end_positions)
            loss = outputs[0]
            loss.backward()
            optimizer.step()
            scheduler.step()

        print(f"Epoch {epoch + 1}/{epochs} completed with loss: {loss.item()}")

    print("Training completed")
    return model


def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForQuestionAnswering.from_pretrained('bert-base-uncased').to(device)

    dataset_files = [
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithLabels/clean_ComprehensiveMedicalQ&A.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithLabels/clean_Fitness.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithLabels/clean_MentalHealth.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithLabels/clean_Symp&Cond.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithLabels/clean_Med&Suppl.json',
        '/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/CleanData/WithLabels/clean_Nutr&Diet.json'
    ]

    datasets = [QADataset(file, tokenizer) for file in dataset_files]

    for dataset in datasets:
        print(f"Training on dataset: {dataset.data[0]['label']}")
        model = train(model, tokenizer, dataset, device)

    model.save_pretrained('fine_tuned_bert_qa')
    tokenizer.save_pretrained('fine_tuned_bert_qa')
    print("Model and tokenizer saved")


if __name__ == '__main__':
    main()
