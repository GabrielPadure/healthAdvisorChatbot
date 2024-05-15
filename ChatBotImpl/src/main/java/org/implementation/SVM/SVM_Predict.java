package org.implementation.SVM;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.util.Scanner;

import org.json.JSONObject;

public class SVM_Predict {
    // sends a user question to the Flask API and returns the predicted category and cleaned text
    public static JSONObject getPrediction(String userQuestion) throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:5000/predict"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString("{\"text\":\"" + userQuestion + "\"}"))
                .build();

        HttpResponse<String> response = client.send(request, BodyHandlers.ofString());
        return new JSONObject(response.body());
    }

    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("Welcome, how may I help you? Type 'exit' to quit.");

            while (true) {
                System.out.print("Ask a question: ");
                String userInput = scanner.nextLine();
                if ("exit".equalsIgnoreCase(userInput.trim())) {
                    break;
                }
                JSONObject predictionResults = getPrediction(userInput);
                String category = predictionResults.getString("category");
                String cleanedText = predictionResults.getString("cleaned_text"); // Retrieve the cleaned text
                System.out.println("Cleaned Question: " + cleanedText); // Print the cleaned text
                System.out.println("You might be talking about: " + category);
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}
