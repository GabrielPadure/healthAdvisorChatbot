package org.implementation;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class StartBoth {

    public static void main(String[] args) {
        // Start Flask Application
        new Thread(StartBoth::startFlaskApp).start();

        // Wait for Flask to start
        waitForFlaskServer();

        // Start JavaFX GUI Application
        org.implementation.GUI.ChatBotGUI.main(args);
    }

    private static void startFlaskApp() {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder("python3", "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/BERT_Impl/BERT_api.py");
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Read and print the output from the Flask application
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println(line);
            }

            int exitCode = process.waitFor();
            System.out.println("Flask application exited with code: " + exitCode);
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    private static void waitForFlaskServer() {
        boolean isServerUp = false;
        while (!isServerUp) {
            try {
                HttpURLConnection connection = (HttpURLConnection) new URL("http://localhost:5001/ask").openConnection();
                connection.setRequestMethod("POST");
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setConnectTimeout(1000);
                connection.setReadTimeout(1000);

                String jsonInputString = "{\"question\": \"test\"}";

                try (DataOutputStream wr = new DataOutputStream(connection.getOutputStream())) {
                    wr.writeBytes(jsonInputString);
                    wr.flush();
                }

                int responseCode = connection.getResponseCode();
                if (responseCode == 200) {
                    isServerUp = true;
                } else {
                    System.out.println("Response Code: " + responseCode);
                }
            } catch (IOException e) {
                System.out.println("Waiting for Flask server...");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }
        }
    }
}
