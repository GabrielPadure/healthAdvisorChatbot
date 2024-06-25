import threading
import os

def start_flask_app():
    # Explicitly call the Python interpreter to run the script
    os.system("python3 /Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/PythonImplementation/BERT_Impl/BERT_api.py")

def start_java_gui():
    javafx_path = "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/javafx-sdk-22.0.1/lib"
    json_lib_path = "/Users/alexandruvalah/.m2/repository/org/json/json/20210307/json-20210307.jar"
    commons_math3_path = "/Users/alexandruvalah/.m2/repository/org/apache/commons/commons-math3/3.6.1/commons-math3-3.6.1.jar"
    resources_path = "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/ChatBotImpl/resources"
    class_output_dir = "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/ChatBotImpl/classes"
    classpath = f"{class_output_dir}:{resources_path}:{javafx_path}/*:{json_lib_path}:{commons_math3_path}"

    # Compile the JavaFX application
    compile_command = f"javac --module-path {javafx_path} --add-modules javafx.controls,javafx.fxml -d {class_output_dir} -cp {classpath} /Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/ChatBotImpl/src/main/java/org/implementation/GUI/ChatBotGUI.java"
    # Run the JavaFX application
    run_command = f"java --module-path {javafx_path} --add-modules javafx.controls,javafx.fxml -cp {classpath} org.implementation.GUI.ChatBotGUI"

    # Run the commands
    os.system(compile_command)
    os.system(run_command)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask_app)
    java_thread = threading.Thread(target=start_java_gui)

    flask_thread.start()
    java_thread.start()

    flask_thread.join()
    java_thread.join()
