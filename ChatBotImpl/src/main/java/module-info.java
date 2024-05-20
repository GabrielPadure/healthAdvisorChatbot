module ChatBotImpl {
    exports org.implementation.GUI;
    requires javafx.fxml;
    requires javafx.controls;
    requires org.json;
    requires java.net.http;
    requires commons.math3;

    opens org.implementation.GUI;
}