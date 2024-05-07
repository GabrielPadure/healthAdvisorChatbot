package org.example;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class CSVToJsonConverter {

    public static void convertCSVToJson(String csvFilePath, String jsonFilePath) {
        try (BufferedReader br = new BufferedReader(new FileReader(csvFilePath))) {
            // Skip the header
            String line = br.readLine();

            JSONArray jsonArray = new JSONArray();
            while ((line = br.readLine()) != null) {
                // Handling CSV parsing manually to accommodate for commas inside quotes
                String[] parts = parseCSVLine(line);
                if (parts.length == 3) {
                    JSONObject jsonObject = new JSONObject();
                    jsonObject.put("question", parts[0].trim());
                    jsonObject.put("answer", parts[1].trim());
                    jsonObject.put("keywords", parts[2].trim());
                    jsonArray.put(jsonObject);
                }
            }

            // Write JSON array to file
            Files.write(Paths.get(jsonFilePath), jsonArray.toString(4).getBytes());
            System.out.println("JSON file created successfully at " + jsonFilePath);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static String[] parseCSVLine(String line) {
        // Initialize the parts array to hold up to three elements
        String[] parts = new String[3];
        boolean inQuotes = false;
        int start = 0;
        int partIndex = 0;

        for (int i = 0; i < line.length(); i++) {
            if (line.charAt(i) == '\"') {
                inQuotes = !inQuotes; // Toggle the inQuotes flag when a quote is encountered
            } else if (line.charAt(i) == ',' && !inQuotes) {
                if (partIndex < parts.length) { // Check to ensure we don't exceed the parts array bounds
                    parts[partIndex++] = line.substring(start, i).replace("\"", "").trim();
                    start = i + 1;
                }
            }
        }
        // Handle the last part after the last comma, if not exceeding the array bounds
        if (partIndex < parts.length) {
            parts[partIndex] = line.substring(start).replace("\"", "").trim();
        }
        return parts;
    }


    public static void main(String[] args) {
        String csvFilePath = "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/updated_file.csv";
        String jsonFilePath = "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/json_mental_health.csv"; // Path where JSON file will be saved
        convertCSVToJson(csvFilePath, jsonFilePath);
    }
}
