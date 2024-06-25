package org.implementation.GUI;

import javafx.animation.PauseTransition;
import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextArea;
import javafx.scene.control.TextField;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import javafx.util.Duration;
import org.json.JSONArray;
import org.json.JSONObject;

import java.awt.*;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

public class ChatBotGUI extends Application {
    private VBox chatPane;
    private TextField userInputField;
    private HttpClient httpClient = HttpClient.newHttpClient();
    private String currentQuestion;
    private String matchedQuestion; // To store the matched question
    private String currentAnswer; // To store the current answer
    private String currentContext;
    private double currentThreshold;
    private Set<String> previousSuggestions = new HashSet<>();
    private String videoURL;

    @Override
    public void start(Stage primaryStage) {
        // Header section
        HBox header = new HBox();
        header.setStyle("-fx-background-color: #007bff; -fx-padding: 10;");
        header.setAlignment(Pos.CENTER_LEFT);

        Image logoImage = new Image(getClass().getResourceAsStream("/logo.png"));
        ImageView logo = new ImageView(logoImage);
        logo.setFitWidth(30);
        logo.setFitHeight(30);
        logo.setPreserveRatio(true);
        logo.setSmooth(true);
        logo.setCache(true);

        Label headerLabel = new Label("Chat with us");
        headerLabel.setStyle("-fx-text-fill: white; -fx-font-size: 16px; -fx-font-weight: bold;");
        header.getChildren().addAll(logo, new Region() {{
            setPrefWidth(10);
        }}, headerLabel);

        // Chat pane
        chatPane = new VBox();
        chatPane.setFillWidth(true);
        chatPane.setSpacing(10);
        chatPane.setPadding(new Insets(10));
        chatPane.setStyle("-fx-background-color: #ffffff;");

        ScrollPane scrollPane = new ScrollPane();
        scrollPane.setContent(chatPane);
        scrollPane.setFitToWidth(true);
        scrollPane.setVbarPolicy(ScrollPane.ScrollBarPolicy.ALWAYS);
        scrollPane.setStyle("-fx-background: #ffffff; -fx-border-color: #cccccc;");

        // User input field
        userInputField = new TextField();
        userInputField.setPromptText("Type your message here...");
        userInputField.setOnAction(e -> sendMessage());
        userInputField.setStyle("-fx-background-color: #ffffff; -fx-border-color: #cccccc; -fx-padding: 10; -fx-font-size: 14px;");

        // Input area layout
        HBox inputLayout = new HBox();
        inputLayout.getChildren().add(userInputField);
        HBox.setHgrow(userInputField, Priority.ALWAYS);
        inputLayout.setSpacing(10);
        inputLayout.setAlignment(Pos.CENTER);
        inputLayout.setPadding(new Insets(10));
        inputLayout.setStyle("-fx-background-color: #f1f1f1; -fx-border-color: #cccccc;");

        // Main layout
        VBox mainLayout = new VBox();
        mainLayout.getChildren().addAll(header, scrollPane, inputLayout);
        VBox.setVgrow(scrollPane, Priority.ALWAYS);

        Scene scene = new Scene(mainLayout, 500, 600);
        primaryStage.getIcons().add(new Image(getClass().getResourceAsStream("/logo.png")));
        primaryStage.setScene(scene);
        primaryStage.setTitle("ChatBot");
        primaryStage.show();
    }

    private void sendMessage() {
        String userMessage = userInputField.getText().trim();
        if (!userMessage.isEmpty()) {
            addMessage("You", userMessage, Pos.TOP_RIGHT, "#D9EDF7", "#333333");
            userInputField.clear();

            if ("yes".equalsIgnoreCase(userMessage) && currentQuestion != null && currentContext != null) {
                confirmQuestion(matchedQuestion, currentContext, videoURL);
            } else if ("no".equalsIgnoreCase(userMessage)) {
                currentThreshold -= 0.05;
                if (currentThreshold >= 0.5) {
                    searchForMatch(currentQuestion, currentThreshold);
                } else {
                    String fallbackAnswer = "I'm sorry, I couldn't find a good match. Here is a general answer:";
                    addMessage("ChatBot", fallbackAnswer, Pos.TOP_LEFT, "#F7F7F9", "#333333");
                    generateGPTNeoAnswer(currentQuestion);
                }
            } else {
                currentQuestion = userMessage;
                currentThreshold = 0.7;
                previousSuggestions.clear();  // Reset previous suggestions for a new question
                searchForMatch(userMessage, currentThreshold);
            }
        }
    }

    private void searchForMatch(String userMessage, double threshold) {
        CompletableFuture.runAsync(() -> {
            try {
                JSONObject requestJson = new JSONObject();
                requestJson.put("question", userMessage);
                requestJson.put("threshold", threshold);
                JSONArray previousSuggestionsJson = new JSONArray(previousSuggestions);
                requestJson.put("previous_suggestions", previousSuggestionsJson);

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:5001/ask"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(requestJson.toString()))
                        .build();

                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                JSONObject jsonResponse = new JSONObject(response.body());
                boolean foundMatch = jsonResponse.getBoolean("found_match");

                if (foundMatch) {
                    matchedQuestion = jsonResponse.getString("matched_question");
                    currentContext = jsonResponse.getString("context");
                    previousSuggestions.add(matchedQuestion);
                    currentThreshold = threshold;  // Update the current threshold

                    String responseMessage = "Did you mean: '" + matchedQuestion + "'? (yes/no)";
                    videoURL = jsonResponse.optString("videoURL", null);
                    String finalResponseMessage = responseMessage;
                    javafx.application.Platform.runLater(() -> addMessage("ChatBot", finalResponseMessage, Pos.TOP_LEFT, "#F7F7F9", "#333333"));
                } else {
                    if (threshold > 0.5) {
                        searchForMatch(userMessage, threshold - 0.05);
                    } else {
                        String gptAnswer = jsonResponse.getString("answer");
                        currentAnswer = gptAnswer; // Store the generated answer
                        javafx.application.Platform.runLater(() -> addMessage("ChatBot", gptAnswer, Pos.TOP_LEFT, "#F7F7F9", "#333333"));
                    }
                }
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
                javafx.application.Platform.runLater(() -> addMessage("ChatBot", "Error in getting response.", Pos.TOP_LEFT, "#F7F7F9", "#333333"));
            }
        });
    }

    private void confirmQuestion(String matchedQuestion, String context, String videoURL) {
        CompletableFuture.runAsync(() -> {
            try {
                JSONObject requestJson = new JSONObject();
                requestJson.put("question", currentQuestion);
                requestJson.put("threshold", currentThreshold);
                requestJson.put("previous_suggestions", new JSONArray(previousSuggestions));
                requestJson.put("confirm", true);
                requestJson.put("matched_question", matchedQuestion);
                requestJson.put("context", context);
                requestJson.put("videoURL", videoURL);

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:5001/ask"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(requestJson.toString()))
                        .build();

                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                JSONObject jsonResponse = new JSONObject(response.body());
                String answer = jsonResponse.getString("answer");
                String videoUrl = jsonResponse.optString("videoURL", null);

                // Update currentAnswer with the received answer
                currentAnswer = answer;

                javafx.application.Platform.runLater(() -> {
                    addMessage("ChatBot", answer, Pos.TOP_LEFT, "#F7F7F9", "#333333");
                    if (videoUrl != null) {
                        addMessage("ChatBot", videoUrl, Pos.TOP_LEFT, "#F7F7F9", "#333333", true);
                    }
                    PauseTransition pause = new PauseTransition(Duration.seconds(2));
                    pause.setOnFinished(event -> askForFeedback());
                    pause.play();
                });
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
                javafx.application.Platform.runLater(() -> addMessage("ChatBot", "Error in getting response.", Pos.TOP_LEFT, "#F7F7F9", "#333333"));
            }
        });
    }



    private void generateGPTNeoAnswer(String question) {
        CompletableFuture.runAsync(() -> {
            try {
                JSONObject requestJson = new JSONObject();
                requestJson.put("question", question);

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:5001/generate_gpt_neo_response"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(requestJson.toString()))
                        .build();

                HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
                JSONObject jsonResponse = new JSONObject(response.body());
                String answer = jsonResponse.getString("answer");
                currentAnswer = answer; // Store the answer

                javafx.application.Platform.runLater(() -> addMessage("ChatBot", answer, Pos.TOP_LEFT, "#F7F7F9", "#333333"));
            } catch (IOException | InterruptedException e) {
                e.printStackTrace();
                javafx.application.Platform.runLater(() -> addMessage("ChatBot", "Error in getting response.", Pos.TOP_LEFT, "#F7F7F9", "#333333"));
            }
        });
    }

    private void askForFeedback() {
        Label feedbackLabel = new Label("Would you like to provide feedback? (yes/no)");
        feedbackLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: #333333;");

        TextField feedbackInput = new TextField();
        feedbackInput.setPromptText("Type 'yes' or 'no'...");
        feedbackInput.setOnAction(e -> {
            String response = feedbackInput.getText().trim();
            if ("yes".equalsIgnoreCase(response)) {
                showRatingWindow();
            }
            chatPane.getChildren().removeAll(feedbackLabel, feedbackInput);
        });

        chatPane.getChildren().addAll(feedbackLabel, feedbackInput);
    }

    private void showRatingWindow() {
        Stage ratingStage = new Stage();
        ratingStage.setTitle("Rate the Answer");

        VBox layout = new VBox();
        layout.setPadding(new Insets(10));
        layout.setSpacing(10);
        layout.setAlignment(Pos.CENTER);

        Label rateLabel = new Label("Rate the answer (1 to 5 stars):");
        ChoiceBox<Integer> ratingChoiceBox = new ChoiceBox<>();
        ratingChoiceBox.getItems().addAll(1, 2, 3, 4, 5);

        Label commentLabel = new Label("Leave a comment:");
        TextArea commentTextArea = new TextArea();
        commentTextArea.setPromptText("Type your comment here...");
        commentTextArea.setWrapText(true);

        Button submitButton = new Button("Submit");
        submitButton.setOnAction(e -> {
            Integer rating = ratingChoiceBox.getValue();
            String comment = commentTextArea.getText().trim();
            if (rating != null) {
                saveFeedbackToFile(matchedQuestion != null ? matchedQuestion : currentQuestion, currentAnswer, rating, comment);
                ratingStage.close();
            } else {
                // Handle the case where the user did not select a rating
                Alert alert = new Alert(Alert.AlertType.WARNING);
                alert.setTitle("Warning");
                alert.setHeaderText(null);
                alert.setContentText("Please select a rating before submitting.");
                alert.showAndWait();
            }
        });

        layout.getChildren().addAll(rateLabel, ratingChoiceBox, commentLabel, commentTextArea, submitButton);

        Scene scene = new Scene(layout, 300, 400);
        ratingStage.setScene(scene);
        ratingStage.show();
    }

    private void saveFeedbackToFile(String question, String answer, int rating, String comment) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter("feedback.txt", true))) {
            DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy/MM/dd HH:mm:ss");
            LocalDateTime now = LocalDateTime.now();
            writer.write("Date/Time: " + dtf.format(now));
            writer.newLine();
            writer.write("Question: " + question);
            writer.newLine();
            writer.write("Answer: " + answer);
            writer.newLine();
            writer.write("Rating: " + rating);
            writer.newLine();
            writer.write("Comment: " + comment);
            writer.newLine();
            writer.write("-------------------------------");
            writer.newLine();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void addMessage(String sender, String message, Pos alignment, String bgColor, String textColor, boolean isUrl) {
        HBox messageBox = new HBox();
        messageBox.setAlignment(alignment);
        messageBox.setPadding(new Insets(5, 0, 5, 0));

        VBox messageContainer = new VBox();
        messageContainer.setStyle(String.format(
                "-fx-background-color: %s; -fx-border-radius: 10px; -fx-background-radius: 10px; -fx-padding: 10px;",
                bgColor));
        messageContainer.setPadding(new Insets(10));
        messageContainer.setSpacing(5);

        Label senderLabel = new Label(sender);
        senderLabel.setStyle("-fx-font-weight: bold; -fx-font-size: 12px; -fx-text-fill: " + textColor + ";");

        if (isUrl) {
            Hyperlink hyperlink = new Hyperlink("Watch the video tutorial");
            hyperlink.setStyle("-fx-font-size: 14px; -fx-text-fill: " + textColor + ";");
            hyperlink.setOnAction(e -> {
                try {
                    Desktop.getDesktop().browse(new URI(message)); // Open the URL in the default browser
                } catch (IOException | URISyntaxException ex) {
                    ex.printStackTrace();
                }
            });
            messageContainer.getChildren().addAll(senderLabel, hyperlink);
        } else {
            Label messageLabel = new Label(message);
            messageLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: " + textColor + ";");
            messageLabel.setWrapText(true);
            messageLabel.setMaxWidth(350);
            messageContainer.getChildren().addAll(senderLabel, messageLabel);
        }

        messageBox.getChildren().add(messageContainer);
        javafx.application.Platform.runLater(() -> chatPane.getChildren().add(messageBox));
    }

    private void addMessage(String sender, String message, Pos alignment, String bgColor, String textColor) {
        addMessage(sender, message, alignment, bgColor, textColor, false);
    }


    public static void main(String[] args) {
        launch(args);
    }
}
