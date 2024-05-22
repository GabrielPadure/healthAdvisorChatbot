package org.implementation.CosineSimilarity;

import org.implementation.BotConfig;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class KeywordBasedImplV2 {
    private Map<String, String> questionToAnswerMap;
    private CosineSimilarity cosineSimilarity;
    private Set<String> allWords;

    public KeywordBasedImplV2() throws IOException {
        this.questionToAnswerMap = new HashMap<>();
        this.allWords = new HashSet<>();
        for (String path : BotConfig.getJsonFilePaths()) {
            loadFAQs(path);
        }
        this.cosineSimilarity = new CosineSimilarity(allWords);
    }


    private void loadFAQs(String jsonFilePath) throws IOException {
        String content = new String(Files.readAllBytes(Paths.get(jsonFilePath)));
        JSONArray jsonArray = new JSONArray(content);

        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            String answer = obj.getString("answer");
            String question = obj.getString("question");
            String cleanedQuestion = callPythonV2.callPythonForPreprocessing(question);
            allWords.addAll(Arrays.asList(cleanedQuestion.split("\\s+")));
            questionToAnswerMap.put(cleanedQuestion, answer);
        }
    }

    public String findAnswer(String userQuestion) throws IOException {
        String cleanedUserQuestion = callPythonV2.callPythonForPreprocessing(userQuestion);
        System.out.println("Preprocessed Question: " + cleanedUserQuestion); // Show preprocessed question
        double maxSimilarity = 0;
        String bestAnswer = "Sorry, I did not understand the question.";

        for (Map.Entry<String, String> entry : questionToAnswerMap.entrySet()) {
            String question = entry.getKey();
            double similarity = cosineSimilarity.cosineSimilarity(cleanedUserQuestion.split("\\s+"), question.split("\\s+"));
            if (similarity > maxSimilarity) {
                maxSimilarity = similarity;
                bestAnswer = entry.getValue();
            }
        }

        return bestAnswer;
    }

    public static void main(String[] args) throws IOException {
        KeywordBasedImplV2 bot = new KeywordBasedImplV2();

        System.out.println("Welcome, how may I help you? Type 'exit' to quit.");

        try (Scanner scanner = new Scanner(System.in)) {
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
