package org.implementation.CosineSimilarity;

import org.implementation.KeywordBasedImpl.callPython;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;

public class KeywordBasedImplV2 {
    private Map<String, String> keywordToAnswerMap;
    private Map<String, String> originalQuestionsMap;
    private CosineSimilarity cosineSimilarity;
    private Set<String> allKeywords = new HashSet<>();

    public KeywordBasedImplV2(List<String> jsonFilePaths) throws IOException {
        this.keywordToAnswerMap = new HashMap<>();
        this.originalQuestionsMap = new HashMap<>(); // Initialize the map to store original questions
        for (String path : jsonFilePaths) {
            loadFAQs(path);
        }
        this.cosineSimilarity = new CosineSimilarity(allKeywords);
    }

    private void loadFAQs(String jsonFilePath) throws IOException {
        String content = new String(Files.readAllBytes(Paths.get(jsonFilePath)));
        JSONArray jsonArray = new JSONArray(content);

        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject obj = jsonArray.getJSONObject(i);
            String answer = obj.getString("answer");
            String keywords = obj.getString("keywords");
            String question = obj.getString("question");
            allKeywords.addAll(Arrays.asList(keywords.split("\\s+")));
            keywordToAnswerMap.put(keywords, answer);
            originalQuestionsMap.put(keywords, question); // Store the original question linked to the keywords
        }
    }

    public String findAnswer(String userQuestion) throws IOException {
        // Assume preprocessing is done outside of timing
        String[] processedTokens = callPython.callPythonForPreprocessing(userQuestion).split("\\s+");

        long startTime = System.nanoTime(); // Start timing right before the similarity checks

        double maxSimilarity = 0;
        String bestAnswer = "Sorry, I did not understand the question.";
        String mostSimilarQuestion = "None";

        // Iterate through each keyword set in the map and calculate cosine similarity
        for (Map.Entry<String, String> entry : keywordToAnswerMap.entrySet()) {
            double similarity = cosineSimilarity.cosineSimilarity(processedTokens, entry.getKey().split("\\s+"));
            if (similarity > maxSimilarity) {
                maxSimilarity = similarity;
                bestAnswer = entry.getValue();
                mostSimilarQuestion = originalQuestionsMap.get(entry.getKey()); // Retrieve the most similar original question
            }
        }

        long endTime = System.nanoTime(); // End timing right after the loop completes
        double duration = (endTime - startTime) / 1_000_000_000.0; // Convert duration from nanoseconds to seconds

        System.out.println("Time taken to find an answer: " + duration + " s");
        System.out.println("Most similar question found: " + mostSimilarQuestion);

        return bestAnswer;
    }


    public static void main(String[] args) throws IOException {
        List<String> jsonFiles = new ArrayList<>();
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Fitness.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Med&Suppl.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/MentalHealth.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Nutr&Diet.json");
        jsonFiles.add("/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Symp&Cond.json");
        KeywordBasedImplV2 bot = new KeywordBasedImplV2(jsonFiles);
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
