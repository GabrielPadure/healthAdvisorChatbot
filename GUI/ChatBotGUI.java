import javafx.application.Application;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.stage.Stage;

public class ChatBotGUI extends Application {
    private VBox chatPane;
    private TextField userInputField;

    @Override
    public void start(Stage primaryStage) {
        chatPane = new VBox();
        chatPane.setFillWidth(true);
        chatPane.setSpacing(10);
        chatPane.setAlignment(Pos.TOP_LEFT);

        ScrollPane scrollPane = new ScrollPane();
        scrollPane.setContent(chatPane);
        scrollPane.setFitToWidth(true);

        userInputField = new TextField();
        userInputField.setPromptText("Type your message here...");
        userInputField.setOnAction(e -> sendMessage());

        HBox inputLayout = new HBox();
        inputLayout.getChildren().addAll(userInputField);
        inputLayout.setHgrow(userInputField, Priority.ALWAYS);
        inputLayout.setSpacing(10);
        inputLayout.setAlignment(Pos.CENTER);

        VBox mainLayout = new VBox();
        mainLayout.getChildren().addAll(scrollPane, inputLayout);

        Scene scene = new Scene(mainLayout, 400, 400);
        primaryStage.setScene(scene);
        primaryStage.setTitle("ChatBot");
        primaryStage.show();
    }

    private void sendMessage() {
        String userMessage = userInputField.getText().trim();
        if (!userMessage.isEmpty()) {
            addMessage("You", userMessage);
            userInputField.clear();

            String botResponse = getBotResponse(userMessage);
            addMessage("ChatBot", botResponse);
        }
    }

    private void addMessage(String sender, String message) {
        Label messageLabel = new Label(sender + ": " + message);
        chatPane.getChildren().add(messageLabel);
    }

    // temporary method. The actual response has to go here
    private String getBotResponse(String userMessage) {
        if (userMessage.toLowerCase().contains("hello")) {
            return "Hello! How can I assist you?";
        } else {
            return "I'm sorry, I didn't understand that.";
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
