package org.implementation.KeywordBasedImpl;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class callPython {

    //Preprocesses a question by calling the Python script
    public static String callPythonForPreprocessing(String question) throws IOException {
        String[] command = new String[]{"python", "/Users/alexandruvalah/IdeaProjects/healthAdvisorChatbot/DataPreprocessing/Data_Processing/data_preprocessing.py", question};
        Process process = Runtime.getRuntime().exec(command);

        BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder output = new StringBuilder();
        String line;
        while (true) {
            if ((line = in.readLine()) == null) break;
            output.append(line);
        }
        in.close();

        return output.toString();
    }
}

