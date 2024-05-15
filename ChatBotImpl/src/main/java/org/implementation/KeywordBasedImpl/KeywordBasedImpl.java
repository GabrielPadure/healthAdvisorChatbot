package org.implementation.KeywordBasedImpl;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class KeywordBasedImpl {
    private Map<String, String> keywordToAnswerMap;

    public KeywordBasedImpl(List<String> jsonFilePaths) throws IOException {
        this.keywordToAnswerMap = new HashMap<>();
        for (String path : jsonFilePaths) {
            loadFAQs(path);
        }
    }

    private void loadFAQs(String jsonFilePath) throws IOException {
        String content = new String(Files.readAllBytes(Paths.get(jsonFilePath)));
        JSONArray jsonArray = new JSONArray(content);

        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            String answer = obj.getString("answer");
            String keywords = obj.getString("keywords");
            keywordToAnswerMap.put(keywords.toLowerCase().trim(), answer);
        }
    }

    public String findAnswer(String userQuestion) throws IOException {
        String processedQuestion = callPython.callPythonForPreprocessing(userQuestion);
        System.out.println("Processed Question: " + processedQuestion);

        long startTime = System.nanoTime(); // Start timing only before searching for an answer
        String bestAnswer = "Sorry, I did not understand the question.";
        for (Map.Entry<String, String> entry : keywordToAnswerMap.entrySet()) {
            if (processedQuestion != null && processedQuestion.contains(entry.getKey())) {
                bestAnswer = entry.getValue();
                break;
            }
        }
        long endTime = System.nanoTime(); // End timing after finding the answer
        double duration = (endTime - startTime) / 1_000_000_000.0; // Convert duration from nanoseconds to milliseconds
        System.out.println("Time taken to find an answer: " + duration + " s");

        return bestAnswer;
    }

    public static void main(String[] args) throws IOException {
        List<String> jsonFiles = new ArrayList<>();
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Fitness.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Med&Suppl.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/MentalHealth.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Nutr&Diet.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Symp&Cond.json");
        KeywordBasedImpl bot = new KeywordBasedImpl(jsonFiles);
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("Welcome, how may I help you? Type 'exit' to quit.");

            while (true) {
                System.out.print("Ask a question: ");
                String userInput = scanner.nextLine();
                if ("exit".equalsIgnoreCase(userInput.trim())) {
                    break;
                }
                String answer = bot.findAnswer(userInput);
                System.out.println("Answer: " + answer);
            }
        }
        System.out.println("Have a wonderful day!");
    }
}
