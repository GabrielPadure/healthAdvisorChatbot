package org.implementation.GUI;

import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextField;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import org.implementation.CosineSimilarity.KeywordBasedImplV2;

import java.io.IOException;
import java.util.Arrays;

public class ChatBotGUI extends Application {
    private VBox chatPane;
    private TextField userInputField;
    private KeywordBasedImplV2 chatBot;

    @Override
    public void start(Stage primaryStage) {
        try {
            chatBot = new KeywordBasedImplV2(Arrays.asList(
                    "/Users/User/Documents/GitHub/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Fitness.json",
                    "/Users/User/Documents/GitHub/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Med&Suppl.json",
                    "/Users/User/Documents/GitHub/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/MentalHealth.json",
                    "/Users/User/Documents/GitHub/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Nutr&Diet.json",
                    "/Users/User/Documents/GitHub/healthAdvisorChatbot/DataPreprocessing/Resources/RawData/Symp&Cond.json"
            ));
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Header section
        HBox header = new HBox();
        header.setStyle("-fx-background-color: #007bff; -fx-padding: 10;");
        header.setAlignment(Pos.CENTER_LEFT);

        ImageView logo = new ImageView(new Image(getClass().getResourceAsStream("/logo.png")));
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

            String botResponse;
            try {
                botResponse = chatBot.findAnswer(userMessage);
            } catch (IOException e) {
                botResponse = "Error in getting response.";
                e.printStackTrace();
            }

            addMessage("ChatBot", botResponse, Pos.TOP_LEFT, "#F7F7F9", "#333333");
        }
    }

    private void addMessage(String sender, String message, Pos alignment, String bgColor, String textColor) {
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

        Label messageLabel = new Label(message);
        messageLabel.setStyle("-fx-font-size: 14px; -fx-text-fill: " + textColor + ";");
        messageLabel.setWrapText(true); // Enable text wrapping
        messageLabel.setMaxWidth(350); // Set a max width to ensure wrapping

        messageContainer.getChildren().addAll(senderLabel, messageLabel);
        messageBox.getChildren().add(messageContainer);
        chatPane.getChildren().add(messageBox);
    }

    public static void main(String[] args) {
        launch(args);
    }
}
