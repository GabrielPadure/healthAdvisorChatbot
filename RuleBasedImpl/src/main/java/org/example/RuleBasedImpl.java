package org.example;

import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Scanner;

public class RuleBasedImpl {
    private Map<String, String> keywordToAnswerMap;

    public RuleBasedImpl(String jsonFilePath) throws IOException {
        this.keywordToAnswerMap = new HashMap<>();
        loadFAQs(jsonFilePath);
    }


     //Loads the Q&As from "mental_health.json" and stores them in a map.
     //Each entry in the map corresponds to a keyword and it's answer.
    private void loadFAQs(String jsonFilePath) throws IOException {
            String content = new String(Files.readAllBytes(Paths.get(jsonFilePath)));
            JSONArray jsonArray = new JSONArray(content);

        int i = 0;
        while (i < jsonArray.length()) {
            JSONObject obj = jsonArray.getJSONObject(i);
            String answer = obj.getString("answer");
            String keywords = obj.getString("keywords");
            keywordToAnswerMap.put(keywords.toLowerCase().trim(), answer); // Storing the entire keyword phrase
            i++;
        }

    }
    //Finds an answer to a given user question
    public String findAnswer(String userQuestion) throws IOException {
        String processedQuestion = callPython.callPythonForPreprocessing(userQuestion); // call Python script for preprocessing
        System.out.println("Processed Question: " + processedQuestion);  // just for checking the preprocessing

        for (Iterator<Map.Entry<String, String>> iterator = keywordToAnswerMap.entrySet().iterator(); iterator.hasNext(); ) {
            Map.Entry<String, String> entry = iterator.next();
            assert processedQuestion != null;
            if (processedQuestion.contains(entry.getKey())) {
                return entry.getValue();
            }
        }
        return "Sorry, I did not understand the question.";
    }


    //To handle user interaction
    public static void main(String[] args) throws IOException {
        RuleBasedImpl bot = new RuleBasedImpl("DataPreprocessing/mental_health.json");
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("Welcome, how may I help you? Type 'exit' to quit.");

            do {
                System.out.print("Ask a question: ");
                String userInput = scanner.nextLine();
                if ("exit".equalsIgnoreCase(userInput.trim())) {
                    break;
                }
                String answer = bot.findAnswer(userInput);
                System.out.println("Answer: " + answer);
            } while (true);
        }
        System.out.println("Have a wonderful day!");
    }
}
