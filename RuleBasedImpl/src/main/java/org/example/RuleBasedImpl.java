package org.example;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class RuleBasedImpl {
    private Map<String, String> keywordToAnswerMap;

    public RuleBasedImpl(List<String> jsonFilePaths) throws IOException {
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

        for (Map.Entry<String, String> entry : keywordToAnswerMap.entrySet()) {
            if (processedQuestion != null && processedQuestion.contains(entry.getKey())) {
                return entry.getValue();
            }
        }
        return "Sorry, I did not understand the question.";
    }

    public static void main(String[] args) throws IOException {
        List<String> jsonFiles = new ArrayList<>();
        jsonFiles.add("DataPreprocessing/Fitness.json");
        jsonFiles.add("DataPreprocessing/Med&Suppl.json");
        jsonFiles.add("DataPreprocessing/MentalHealth.json");
        jsonFiles.add("DataPreprocessing/Nutr&Diet.json");
        jsonFiles.add("DataPreprocessing/Symp&Cond.json");
        RuleBasedImpl bot = new RuleBasedImpl(jsonFiles);
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
